<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'
import { limpiarHtml } from '../utils/limpiarHtml'
import EditorRico from './EditorRico.vue'
import GrabadoraReunion from './GrabadoraReunion.vue'

// Actes de reunió: d'un projecte o del departament. Cada acta té els assistents, el text
// (amb una plantilla: ordre del dia, desenvolupament, acords), les tasques que en surten i,
// si es vol, la gravació de la reunió (l'àudio és temporal: s'esborra un temps després
// d'aprovar l'acta). Les gravacions les transcriu l'ordinador de transcripció del SIO
// (deploy/transcripcio/): en surt la transcripció, amb qui parla, i un esborrany de l'acta.
const props = defineProps({ sesion: { type: Object, required: true } })
const emit = defineEmits(['sesion-caducada'])
const { t, locale } = useI18n()
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })
const leer = (clave) => { try { return localStorage.getItem(clave) } catch { return null } }
const guardarLocal = (clave, valor) => { try { localStorage.setItem(clave, valor) } catch { /* sense emmagatzematge */ } }

const datos = ref(null)
// L'avís de la transcripció es pot plegar (es recorda en aquest navegador)
const avisoAbierto = leer('sio_actas_aviso') !== 'plegado'
const alPlegarAviso = (e) => guardarLocal('sio_actas_aviso', e.target.open ? 'abierto' : 'plegado')
const error = ref('')
const mensaje = ref('')
const acta = ref(null) // l'acta oberta (còpia per editar)
const original = ref('') // per saber si hi ha canvis sense desar
const guardando = ref(false)
const grabadora = ref(null)

const hoyIso = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` }
const fecha = (iso) => iso ? new Intl.DateTimeFormat(locale.value, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(iso.slice(0, 10) + 'T12:00:00')) : ''
const fechaHora = (iso) => iso ? new Intl.DateTimeFormat(locale.value, { dateStyle: 'short', timeStyle: 'short' }).format(new Date(iso.replace(' ', 'T') + 'Z')) : ''
const duracion = (s) => !s ? '' : s < 60 ? `${s} s` : `${Math.floor(s / 3600) ? Math.floor(s / 3600) + ' h ' : ''}${Math.floor(s / 60) % 60} min`
const megas = (b) => b >= 1048576 ? `${(b / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(b / 1024))} kB`
const nombreProyecto = (id) => datos.value?.proyectos.find(p => p.id === id)?.titulo || ''

const cargar = async () => {
  const r = await api('/api/actas')
  if (!r.ok) { error.value = t('intranet.comun.errorDesconocido'); return }
  datos.value = await r.json()
}
// ---------- Ordinador de transcripció ----------
const transcriptor = ref(null)
const claveNueva = ref('')
const cargarTranscriptor = async () => {
  const r = await api('/api/transcripcion/estado')
  if (r.ok) transcriptor.value = await r.json()
}
const minutosDesde = (iso) => iso ? Math.max(0, Math.round((Date.now() - new Date(iso.replace(' ', 'T') + 'Z')) / 60000)) : null
const estadoOrdenador = computed(() => {
  const tr = transcriptor.value
  if (!tr) return null
  if (!tr.configurado || !tr.visto) return { clase: 'apagado', texto: t('intranet.actas.trNunca') }
  const m = minutosDesde(tr.visto)
  if (m <= 25) return { clase: 'encendido', texto: t('intranet.actas.trConectado', { maquina: tr.maquina || '?', min: m }) }
  return { clase: 'apagado', texto: t('intranet.actas.trApagado', { maquina: tr.maquina || '?', cuando: fechaHora(tr.visto) }) }
})
const generarClave = async () => {
  if (transcriptor.value?.configurado && !confirm(t('intranet.actas.trConfirmarClave'))) return
  const r = await api('/api/transcripcion/clave', { method: 'POST' })
  if (!r.ok) { error.value = t('intranet.comun.errorDesconocido'); return }
  claveNueva.value = (await r.json()).clave
  cargarTranscriptor()
}
const copiarClave = () => { navigator.clipboard?.writeText(claveNueva.value).then(() => { mensaje.value = t('intranet.actas.trCopiada') }).catch(() => {}) }

// Mentre hi ha gravacions per transcriure, es mira cada 30 s com van
let temporizador = null
onMounted(() => {
  cargar()
  cargarTranscriptor()
  temporizador = setInterval(() => {
    if (acta.value?.id && (acta.value.audios || []).some(a => ['pendent', 'processant'].includes(a.transcripcion_estado))) {
      refrescarAudios()
      cargarTranscriptor()
    }
  }, 30000)
})
onBeforeUnmount(() => clearInterval(temporizador))

// ---------- Llista ----------
// '' = totes, 'dep' = departament, o l'id d'un projecte
const filtro = ref(leer('sio_actas_filtro') || '')
watch(filtro, (v) => guardarLocal('sio_actas_filtro', v))
const lista = computed(() => (datos.value?.actas || []).filter(a =>
  filtro.value === '' ? true : filtro.value === 'dep' ? a.proyecto_id == null : String(a.proyecto_id) === filtro.value))
const proyectosConActas = computed(() => new Set((datos.value?.actas || []).map(a => a.proyecto_id).filter(Boolean)))
const proyectosOrdenados = computed(() => [...(datos.value?.proyectos || [])].sort((a, b) =>
  (proyectosConActas.value.has(b.id) - proyectosConActas.value.has(a.id)) || a.titulo.localeCompare(b.titulo)))

// ---------- Acta ----------
const plantilla = () => `<h2>${t('intranet.actas.plOrden')}</h2><ol><li><p></p></li></ol><h2>${t('intranet.actas.plDesarrollo')}</h2><p></p><h2>${t('intranet.actas.plAcuerdos')}</h2><ul><li><p></p></li></ul>`
const instantanea = (a) => JSON.stringify({ ...a, audios: undefined, n_audios: undefined })
const hayCambios = computed(() => acta.value && instantanea(acta.value) !== original.value)
const abrirActa = (a) => {
  acta.value = JSON.parse(JSON.stringify(a))
  original.value = instantanea(acta.value)
  error.value = ''; mensaje.value = ''
  window.scrollTo?.({ top: 0 })
}
const nueva = () => abrirActa({
  id: null, titulo: '', fecha: hoyIso(), hora: '', lugar: '',
  proyecto_id: filtro.value && filtro.value !== 'dep' ? Number(filtro.value) : null,
  asistentes: props.sesion.usuario_id ? [props.sesion.usuario_id] : [], otros_asistentes: '',
  contenido: plantilla(), tareas: [], estado: 'esborrany', audios: [], puede_borrar: true
})
const verActa = async (a) => {
  const r = await api(`/api/actas/${a.id}`)
  if (!r.ok) { error.value = t('intranet.comun.errorDesconocido'); return }
  abrirActa(await r.json())
}
const volver = () => {
  if (hayCambios.value && !confirm(t('intranet.actas.salirSinGuardar'))) return
  acta.value = null
  cargar()
}

// Assistents: primer la gent del SIO, després la resta d'usuaris
const usuariosOrdenados = computed(() => [...(datos.value?.usuarios || [])].sort((a, b) => (b.plantilla - a.plantilla) || a.nombre.localeCompare(b.nombre)))
const alternarAsistente = (id) => {
  const s = acta.value.asistentes
  const i = s.indexOf(id)
  if (i >= 0) s.splice(i, 1); else s.push(id)
}
const todoSio = () => {
  for (const u of datos.value.usuarios) if (u.plantilla && !acta.value.asistentes.includes(u.id)) acta.value.asistentes.push(u.id)
}

// Tasques
const nuevaTarea = () => acta.value.tareas.push({ texto: '', responsable: '', fecha: '', hecha: false })

const guardar = async (estado = acta.value.estado) => {
  error.value = ''; mensaje.value = ''
  guardando.value = true
  const acabaDeAprobar = estado === 'aprovada' && acta.value.estado !== 'aprovada'
  try {
    const cuerpo = { ...acta.value, estado, tareas: acta.value.tareas.filter(x => x.texto.trim()) }
    const r = await api(acta.value.id ? `/api/actas/${acta.value.id}` : '/api/actas', json(acta.value.id ? 'PUT' : 'POST', cuerpo))
    const d = await r.json().catch(() => ({}))
    if (!r.ok) { error.value = traducirError(d.error) || t('intranet.comun.noGuardado'); return false }
    abrirActa(d)
    mensaje.value = acabaDeAprobar ? t('intranet.actas.guardadaAprobada', { dias: datos.value.dias_audio }) : t('intranet.actas.guardada')
    return true
  } finally { guardando.value = false }
}
const aprobar = () => guardar('aprovada')
const reabrir = () => guardar('esborrany')

const borrarActa = async () => {
  if (!confirm(t('intranet.actas.confirmarBorrar'))) return
  const r = await api(`/api/actas/${acta.value.id}`, { method: 'DELETE' })
  if (!r.ok) { error.value = traducirError((await r.json().catch(() => ({}))).error) || t('intranet.comun.noBorrado'); return }
  acta.value = null
  mensaje.value = t('intranet.comun.borrado')
  cargar()
}

// Gravar una acta nova: primer es desa (l'àudio va lligat a l'acta)
const guardarYGrabar = async () => {
  if (!acta.value.titulo.trim()) { error.value = t('intranet.actas.ponTitulo'); return }
  if (await guardar()) { await nextTick(); grabadora.value?.abrir() }
}

// Quan s'acaba de gravar o pujar un àudio, es torna a llegir l'acta (sense perdre el que s'està escrivint)
const refrescarAudios = async () => {
  const r = await api(`/api/actas/${acta.value.id}`)
  if (!r.ok) return
  const d = await r.json()
  acta.value.audios = d.audios
  acta.value.audio_se_borra = d.audio_se_borra
}
// ---------- Transcripció d'una gravació ----------
const transcripciones = ref({}) // id de l'àudio → { segmentos, hablantes, borrador }
const abiertas = ref({})
const cargarTranscripcion = async (au) => {
  const r = await api(`/api/actas/audios/${au.id}/transcripcion`)
  if (!r.ok) return null
  transcripciones.value[au.id] = await r.json()
  return transcripciones.value[au.id]
}
const verTranscripcion = async (au) => {
  if (abiertas.value[au.id]) { abiertas.value[au.id] = false; return }
  if (!transcripciones.value[au.id]) await cargarTranscripcion(au)
  abiertas.value[au.id] = true
}
const vocesDe = (tr) => [...new Set((tr?.segmentos || []).map(s => s.hablante).filter(Boolean))]
const nombreVoz = (tr, h) => (tr.hablantes || {})[h] || h
const guardarNombres = async (au) => {
  const r = await api(`/api/actas/audios/${au.id}/transcripcion`, json('PUT', { hablantes: transcripciones.value[au.id].hablantes }))
  if (r.ok) { transcripciones.value[au.id] = await r.json(); mensaje.value = t('intranet.actas.trNombresGuardados') }
}
const minuto = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`
// Clicar un fragment el fa sonar
const escuchar = (au, seg) => {
  const el = document.getElementById(`audio-${au.id}`)
  if (!el) return
  el.currentTime = seg.inicio
  el.play().catch(() => {})
}
// Blocs seguits de la mateixa veu (més fàcil de llegir)
const bloques = (tr) => {
  const res = []
  for (const s of tr?.segmentos || []) {
    const ultimo = res[res.length - 1]
    if (ultimo && ultimo.hablante === s.hablante && s.inicio - ultimo.fin < 30) { ultimo.segs.push(s); ultimo.fin = s.fin }
    else res.push({ hablante: s.hablante, inicio: s.inicio, fin: s.fin, segs: [s] })
  }
  return res
}
const descargarTexto = (au) => {
  const tr = transcripciones.value[au.id]
  const texto = bloques(tr).map(b => `[${minuto(b.inicio)}]${b.hablante ? ' ' + nombreVoz(tr, b.hablante) + ':' : ''} ${b.segs.map(s => s.texto).join(' ')}`).join('\n\n')
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([texto], { type: 'text/plain;charset=utf-8' }))
  a.download = `${(acta.value.titulo || 'transcripcio').replace(/[^\w\d-]+/g, '_')}.txt`
  a.click()
}
const retranscribir = async (au) => {
  const r = await api(`/api/actas/audios/${au.id}/transcribir`, { method: 'POST' })
  if (r.ok) refrescarAudios()
}
// Posar l'esborrany que ha fet l'ordinador al text de l'acta (i les tasques a la taula)
const textoVacio = (html) => !(html || '').replace(/<h2>[^<]*<\/h2>/g, '').replace(/<[^>]+>/g, '').trim()
const usarBorrador = async (au) => {
  const tr = transcripciones.value[au.id] || await cargarTranscripcion(au)
  if (!tr?.borrador) return
  let b
  try { b = JSON.parse(tr.borrador) } catch { b = { html: tr.borrador, tareas: [] } }
  const html = limpiarHtml(b.html || '')
  if (textoVacio(acta.value.contenido)) acta.value.contenido = html
  else if (confirm(t('intranet.actas.trSustituir'))) acta.value.contenido = html
  else acta.value.contenido += html
  const ya = new Set(acta.value.tareas.map(x => x.texto.trim().toLowerCase()))
  for (const x of b.tareas || []) if (!ya.has(x.texto.trim().toLowerCase())) acta.value.tareas.push({ ...x, hecha: false })
  mensaje.value = t('intranet.actas.trBorradorPuesto')
}

const borrarAudio = async (au) => {
  if (!confirm(t('intranet.actas.confirmarBorrarAudio'))) return
  const r = await api(`/api/actas/audios/${au.id}`, { method: 'DELETE' })
  if (!r.ok) { error.value = traducirError((await r.json().catch(() => ({}))).error) || t('intranet.comun.noBorrado'); return }
  refrescarAudios()
}

// ---------- Imprimir / PDF ----------
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
const imprimir = () => {
  const a = acta.value
  const asistentes = [...a.asistentes.map(id => datos.value.usuarios.find(u => u.id === id)?.nombre).filter(Boolean), ...(a.otros_asistentes ? [a.otros_asistentes] : [])]
  const tareas = a.tareas.filter(x => x.texto.trim())
  const w = window.open('', '_blank')
  if (!w) return
  w.document.write(`<!doctype html><html lang="${locale.value}"><head><meta charset="utf-8"><title>${esc(a.titulo)}</title><style>
    body{font-family:Arial,sans-serif;color:#222;max-width:780px;margin:30px auto;padding:0 20px;line-height:1.45}
    h1{color:#012169;font-size:1.5rem;margin:0 0 4px} .meta{color:#555;margin:0 0 14px} .bloque{border-top:2px solid #012169;padding-top:6px;margin-top:16px}
    h2{color:#012169;font-size:1.1rem} table{border-collapse:collapse;width:100%} td,th{border:1px solid #ccc;padding:5px 8px;text-align:left;font-size:.92rem}
    .estado{display:inline-block;padding:1px 8px;border-radius:10px;font-size:.8rem;background:${a.estado === 'aprovada' ? '#e6f4ea' : '#fff4e5'}}
    img{max-width:100%} @media print{body{margin:0}}</style></head><body>
    <h1>${esc(a.titulo)}</h1>
    <p class="meta">${esc(fecha(a.fecha))}${a.hora ? ' · ' + esc(a.hora) : ''}${a.lugar ? ' · ' + esc(a.lugar) : ''} · ${esc(a.proyecto_id ? nombreProyecto(a.proyecto_id) : t('intranet.actas.departamento'))}
      · <span class="estado">${esc(t('intranet.actas.estado_' + a.estado))}</span></p>
    <p><b>${esc(t('intranet.actas.asistentes'))}:</b> ${esc(asistentes.join(', ') || '—')}</p>
    <div class="bloque">${limpiarHtml(a.contenido)}</div>
    ${tareas.length ? `<div class="bloque"><h2>${esc(t('intranet.actas.tareas'))}</h2><table><tr><th>${esc(t('intranet.actas.tarea'))}</th><th>${esc(t('intranet.actas.responsable'))}</th><th>${esc(t('intranet.actas.fechaLimite'))}</th><th></th></tr>
      ${tareas.map(x => `<tr><td>${esc(x.texto)}</td><td>${esc(x.responsable)}</td><td>${esc(x.fecha ? fecha(x.fecha) : '')}</td><td>${x.hecha ? '✔' : ''}</td></tr>`).join('')}</table></div>` : ''}
    <script>setTimeout(function(){print()},300)<\/script></body></html>`)
  w.document.close()
}
</script>

<template>
  <div class="panel-actas">
    <h2>📝 {{ $t('intranet.actas.titulo') }}</h2>

    <!-- La transcripció automàtica encara no hi és -->
    <details class="aviso-transcripcion" :open="avisoAbierto" @toggle="alPlegarAviso">
      <summary><strong>🤖 {{ $t('intranet.actas.avisoTitulo') }}</strong></summary>
      <p>{{ $t('intranet.actas.avisoTexto') }}</p>
      <p v-if="estadoOrdenador" class="ordenador" :class="estadoOrdenador.clase">
        🖥️ {{ estadoOrdenador.texto }}<template v-if="transcriptor?.pendientes"> · {{ $t('intranet.actas.trEnCola', { n: transcriptor.pendientes }) }}</template>
      </p>
      <div v-if="sesion.es_admin" class="admin-tr">
        <button type="button" class="btn-mini" @click="generarClave">🔑 {{ $t(transcriptor?.configurado ? 'intranet.actas.trClaveNueva' : 'intranet.actas.trGenerarClave') }}</button>
        <div v-if="claveNueva" class="clave">
          <p>{{ $t('intranet.actas.trClaveSoloAhora') }}</p>
          <input :value="claveNueva" readonly @focus="$event.target.select()">
          <button type="button" class="btn-mini" @click="copiarClave">📋 {{ $t('intranet.actas.trCopiar') }}</button>
        </div>
      </div>
    </details>

    <p v-if="mensaje" class="ok" role="status">{{ mensaje }}</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="!datos && !error" class="vacio">{{ $t('intranet.comun.cargando') }}</p>

    <!-- ================= LLISTA ================= -->
    <template v-if="datos && !acta">
      <div class="barra-lista">
        <label class="filtro">{{ $t('intranet.actas.actasDe') }}
          <select v-model="filtro">
            <option value="">{{ $t('intranet.actas.todas') }}</option>
            <option value="dep">🏢 {{ $t('intranet.actas.departamento') }}</option>
            <option v-for="p in proyectosOrdenados" :key="p.id" :value="String(p.id)">📁 {{ p.titulo }}</option>
          </select>
        </label>
        <button type="button" class="btn-principal" @click="nueva">＋ {{ $t('intranet.actas.nueva') }}</button>
      </div>

      <p v-if="!lista.length" class="vacio">{{ $t('intranet.actas.ninguna') }}</p>
      <ul v-else class="lista">
        <li v-for="a in lista" :key="a.id">
          <button type="button" class="fila-acta" @click="verActa(a)">
            <span class="cuando">{{ fecha(a.fecha) }}<small v-if="a.hora"> · {{ a.hora }}</small></span>
            <span class="que">
              <strong>{{ a.titulo }}</strong>
              <small>{{ a.proyecto_id ? '📁 ' + nombreProyecto(a.proyecto_id) : '🏢 ' + $t('intranet.actas.departamento') }}</small>
            </span>
            <span class="marcas">
              <span class="estado" :class="a.estado">{{ $t('intranet.actas.estado_' + a.estado) }}</span>
              <span v-if="a.n_audios" :title="$t('intranet.actas.audios')">🎙️ {{ a.n_audios }}</span>
              <span v-if="a.tareas_pendientes" class="pendientes" :title="$t('intranet.actas.tareasPendientes')">☐ {{ a.tareas_pendientes }}</span>
            </span>
          </button>
        </li>
      </ul>
    </template>

    <!-- ================= ACTA ================= -->
    <template v-if="datos && acta">
      <div class="barra-acta">
        <button type="button" class="btn-mini" @click="volver">← {{ $t('intranet.actas.volver') }}</button>
        <span class="estado" :class="acta.estado">{{ $t('intranet.actas.estado_' + acta.estado) }}</span>
        <span v-if="hayCambios" class="sin-guardar">● {{ $t('intranet.actas.sinGuardar') }}</span>
      </div>

      <form class="form-acta" @submit.prevent="guardar()">
        <div class="fila">
          <label class="ancho">{{ $t('intranet.actas.tituloCampo') }}
            <input v-model="acta.titulo" maxlength="200" required :placeholder="$t('intranet.actas.tituloPh')">
          </label>
          <label>{{ $t('intranet.actas.de') }}
            <select v-model="acta.proyecto_id">
              <option :value="null">🏢 {{ $t('intranet.actas.departamento') }}</option>
              <option v-for="p in proyectosOrdenados" :key="p.id" :value="p.id">📁 {{ p.titulo }}</option>
            </select>
          </label>
        </div>
        <div class="fila">
          <label>{{ $t('intranet.actas.fecha') }} <input v-model="acta.fecha" type="date" required></label>
          <label>{{ $t('intranet.actas.hora') }} <input v-model="acta.hora" type="time" step="300"></label>
          <label class="ancho">{{ $t('intranet.actas.lugar') }}
            <input v-model="acta.lugar" maxlength="200" :placeholder="$t('intranet.actas.lugarPh')">
          </label>
        </div>

        <fieldset class="bloque">
          <legend>{{ $t('intranet.actas.asistentes') }}</legend>
          <div class="chips">
            <button v-for="u in usuariosOrdenados" :key="u.id" type="button" class="chip" :class="{ on: acta.asistentes.includes(u.id), fuera: !u.plantilla }"
              :aria-pressed="acta.asistentes.includes(u.id)" @click="alternarAsistente(u.id)">{{ acta.asistentes.includes(u.id) ? '✓ ' : '' }}{{ u.nombre }}</button>
            <button type="button" class="btn-mini" @click="todoSio">＋ {{ $t('intranet.actas.todoSio') }}</button>
          </div>
          <label class="otros">{{ $t('intranet.actas.otrosAsistentes') }}
            <input v-model="acta.otros_asistentes" maxlength="2000" :placeholder="$t('intranet.actas.otrosPh')">
          </label>
        </fieldset>

        <fieldset class="bloque">
          <legend>🎙️ {{ $t('intranet.actas.grabacionReunion') }}</legend>
          <p class="nota">{{ $t('intranet.actas.ayudaGrabacion', { dias: datos.dias_audio }) }}</p>
          <ul v-if="acta.audios?.length" class="audios">
            <li v-for="au in acta.audios" :key="au.id">
              <div class="audio-info">
                <strong>{{ au.nombre || $t('intranet.actas.grabacion') }}</strong>
                <small>{{ fechaHora(au.creado) }} · {{ au.creado_por }}<template v-if="au.duracion"> · {{ duracion(au.duracion) }}</template> · {{ megas(au.bytes) }}
                  <template v-if="au.avisados"> · ✓ {{ $t('intranet.actas.avisadosOk') }}</template></small>
                <small v-if="!au.completo" class="incompleto">⚠️ {{ $t('intranet.actas.incompleto') }}</small>
                <small v-if="au.audio_borrado" class="gris">{{ $t('intranet.actas.trAudioBorrado') }}</small>
              </div>
              <template v-if="!au.audio_borrado">
                <audio :id="`audio-${au.id}`" controls preload="none" :src="au.enlace"></audio>
                <a class="btn-mini" :href="au.enlace" :download="au.nombre || 'audio'">⬇️</a>
              </template>
              <button v-if="au.puede_borrar" type="button" class="btn-mini peligro" :aria-label="$t('intranet.comun.borrar')" @click="borrarAudio(au)">🗑️</button>

              <!-- Transcripció -->
              <div v-if="au.transcripcion_estado" class="tr-estado" :class="au.transcripcion_estado">
                <template v-if="au.transcripcion_estado === 'pendent'">⏳ {{ $t('intranet.actas.trPendiente') }}</template>
                <template v-else-if="au.transcripcion_estado === 'processant'">⚙️ {{ $t('intranet.actas.trProcesando') }}<template v-if="au.transcripcion_progreso"> · {{ au.transcripcion_progreso }}</template></template>
                <template v-else-if="au.transcripcion_estado === 'error'">⚠️ {{ $t('intranet.actas.trError') }} <small>{{ au.transcripcion_error }}</small>
                  <button type="button" class="btn-mini" @click="retranscribir(au)">↻ {{ $t('intranet.actas.trReintentar') }}</button></template>
                <template v-else>
                  <button type="button" class="btn-mini" :aria-expanded="!!abiertas[au.id]" @click="verTranscripcion(au)">📝 {{ abiertas[au.id] ? $t('intranet.actas.trOcultar') : $t('intranet.actas.trVer') }}</button>
                  <button v-if="au.tiene_borrador" type="button" class="btn-borrador" @click="usarBorrador(au)">✨ {{ $t('intranet.actas.trUsarBorrador') }}</button>
                  <button v-if="!au.audio_borrado" type="button" class="btn-mini" :title="$t('intranet.actas.trReintentar')" @click="retranscribir(au)">↻</button>
                </template>
              </div>
              <div v-if="abiertas[au.id] && transcripciones[au.id]" class="tr-panel">
                <div v-if="vocesDe(transcripciones[au.id]).length" class="voces">
                  <span class="nota">{{ $t('intranet.actas.trVoces') }}</span>
                  <label v-for="h in vocesDe(transcripciones[au.id])" :key="h">{{ h }}
                    <input v-model="transcripciones[au.id].hablantes[h]" list="actas-personas" :placeholder="$t('intranet.actas.trQuien')">
                  </label>
                  <button type="button" class="btn-mini" @click="guardarNombres(au)">{{ $t('intranet.comun.guardar') }}</button>
                </div>
                <div class="tr-texto">
                  <p v-for="(b, i) in bloques(transcripciones[au.id])" :key="i">
                    <button type="button" class="tiempo" :disabled="au.audio_borrado" @click="escuchar(au, b)">{{ minuto(b.inicio) }}</button>
                    <strong v-if="b.hablante">{{ nombreVoz(transcripciones[au.id], b.hablante) }}:</strong>
                    {{ b.segs.map(s => s.texto).join(' ') }}
                  </p>
                  <p v-if="!transcripciones[au.id].segmentos.length" class="vacio">{{ $t('intranet.actas.trVacia') }}</p>
                </div>
                <button type="button" class="btn-mini" @click="descargarTexto(au)">⬇️ {{ $t('intranet.actas.trDescargar') }}</button>
              </div>
            </li>
          </ul>
          <p v-if="acta.audio_se_borra" class="nota">🕓 {{ $t('intranet.actas.audioSeBorra', { fecha: fecha(acta.audio_se_borra) }) }}</p>
          <GrabadoraReunion v-if="acta.id" ref="grabadora" :acta-id="acta.id" :api="api" @cambio="refrescarAudios" />
          <button v-else type="button" class="btn-grabar" :disabled="guardando" @click="guardarYGrabar">🎙️ {{ $t('intranet.actas.guardarYGrabar') }}</button>
        </fieldset>

        <fieldset class="bloque">
          <legend>{{ $t('intranet.actas.textoActa') }}</legend>
          <EditorRico v-model="acta.contenido" :placeholder="$t('intranet.actas.textoPh')" />
        </fieldset>

        <fieldset class="bloque">
          <legend>{{ $t('intranet.actas.tareas') }}</legend>
          <p v-if="!acta.tareas.length" class="nota">{{ $t('intranet.actas.sinTareas') }}</p>
          <div v-for="(x, i) in acta.tareas" :key="i" class="tarea" :class="{ hecha: x.hecha }">
            <input v-model="x.hecha" type="checkbox" :aria-label="$t('intranet.actas.hecha')">
            <input v-model="x.texto" class="texto" maxlength="500" :placeholder="$t('intranet.actas.tareaPh')">
            <input v-model="x.responsable" class="resp" maxlength="100" list="actas-personas" :placeholder="$t('intranet.actas.responsable')">
            <input v-model="x.fecha" type="date" :aria-label="$t('intranet.actas.fechaLimite')">
            <button type="button" class="btn-mini peligro" :aria-label="$t('intranet.comun.borrar')" @click="acta.tareas.splice(i, 1)">✕</button>
          </div>
          <datalist id="actas-personas"><option v-for="u in usuariosOrdenados" :key="u.id" :value="u.nombre" /></datalist>
          <button type="button" class="btn-mini" @click="nuevaTarea">＋ {{ $t('intranet.actas.nuevaTarea') }}</button>
        </fieldset>

        <div class="acciones">
          <button type="submit" class="btn-principal" :disabled="guardando">{{ $t('intranet.comun.guardar') }}</button>
          <button v-if="acta.estado !== 'aprovada'" type="button" class="btn-aprobar" :disabled="guardando" @click="aprobar">✅ {{ $t('intranet.actas.aprobar') }}</button>
          <button v-else type="button" class="btn-mini" :disabled="guardando" @click="reabrir">↩️ {{ $t('intranet.actas.reabrir') }}</button>
          <button v-if="acta.id" type="button" class="btn-mini" @click="imprimir">🖨️ {{ $t('intranet.actas.imprimir') }}</button>
          <button v-if="acta.id && acta.puede_borrar" type="button" class="btn-mini peligro derecha" @click="borrarActa">{{ $t('intranet.comun.borrar') }}</button>
        </div>
        <p v-if="acta.id" class="nota">{{ $t('intranet.actas.creadaPor', { quien: acta.creado_por, cuando: fechaHora(acta.creado) }) }}
          <template v-if="acta.actualizado !== acta.creado"> · {{ $t('intranet.actas.modificadaPor', { quien: acta.actualizado_por, cuando: fechaHora(acta.actualizado) }) }}</template></p>
      </form>
    </template>
  </div>
</template>

<style scoped>
.panel-actas { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #012169; }
.panel-actas h2 { margin: 0 0 14px; color: #012169; }
.ok { color: #198754; font-weight: bold; }
.error { color: #b02a37; font-weight: bold; }
.vacio { color: #666; font-style: italic; }
.nota { color: #666; font-size: 0.83rem; margin: 2px 0 8px; }

.aviso-transcripcion { background: #eef4fb; border-left: 4px solid #2a7ab0; border-radius: 6px; padding: 10px 14px; margin-bottom: 16px; font-size: 0.9rem; color: #234; }
.aviso-transcripcion p { margin: 6px 0 0; }
.aviso-transcripcion summary { cursor: pointer; }
.ordenador { font-weight: bold; }
.ordenador.encendido { color: #1e6b34; }
.ordenador.apagado { color: #7a4300; }
.admin-tr { margin-top: 8px; }
.clave { background: white; border: 1px solid #f0c37a; border-radius: 6px; padding: 8px 10px; margin-top: 6px; }
.clave p { margin: 0 0 6px; color: #7a4300; font-weight: bold; }
.clave input { width: min(460px, 100%); font-family: monospace; padding: 6px; border: 1px solid #ccd5df; border-radius: 4px; margin-right: 6px; }
.gris { color: #777; }
.tr-estado { flex-basis: 100%; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font-size: 0.88rem; color: #444; border-top: 1px dashed #e1e7ee; padding-top: 6px; }
.tr-estado.error { color: #b02a37; }
.tr-estado.processant { color: #1d5f8c; }
.btn-borrador { background: #6f42c1; color: white; border: none; border-radius: 4px; padding: 6px 12px; cursor: pointer; font-weight: bold; font-size: 0.85rem; }
.tr-panel { flex-basis: 100%; }
.voces { display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end; background: #f0f4f8; border-radius: 6px; padding: 8px 10px; margin-bottom: 8px; }
.voces label { display: flex; flex-direction: column; gap: 2px; font-size: 0.8rem; color: #444; }
.voces input { padding: 5px 7px; border: 1px solid #ccd5df; border-radius: 4px; font: inherit; font-size: 0.85rem; width: 170px; }
.tr-texto { max-height: 420px; overflow-y: auto; border: 1px solid #e1e7ee; border-radius: 6px; padding: 6px 12px; background: white; margin-bottom: 8px; font-size: 0.92rem; line-height: 1.5; }
.tr-texto p { margin: 6px 0; }
.tiempo { background: #eef3f9; border: none; border-radius: 3px; color: #1d5f8c; font-family: monospace; font-size: 0.78rem; padding: 1px 5px; cursor: pointer; margin-right: 4px; }
.tiempo:disabled { cursor: default; }

.barra-lista { display: flex; justify-content: space-between; align-items: flex-end; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.filtro { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-weight: bold; color: #012169; }
.filtro select { font: inherit; padding: 8px 10px; border: 2px solid #012169; border-radius: 6px; background: white; color: #012169; min-width: 260px; max-width: 100%; }

.lista { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.fila-acta { width: 100%; display: grid; grid-template-columns: 170px 1fr auto; gap: 12px; align-items: center; text-align: left; background: #f7f9fb; border: 1px solid #e1e7ee; border-left: 4px solid #012169; border-radius: 8px; padding: 10px 14px; cursor: pointer; font: inherit; color: inherit; }
.fila-acta:hover { background: #eef3f9; }
.cuando { color: #444; font-size: 0.9rem; }
.que { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.que strong { color: #012169; }
.que small { color: #666; }
.marcas { display: flex; gap: 10px; align-items: center; font-size: 0.85rem; white-space: nowrap; }
.pendientes { color: #7a4300; font-weight: bold; }
.estado { display: inline-block; padding: 2px 9px; border-radius: 10px; font-size: 0.78rem; font-weight: bold; }
.estado.esborrany { background: #fff4e5; color: #7a4300; }
.estado.aprovada { background: #e6f4ea; color: #1e6b34; }

.barra-acta { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.sin-guardar { color: #b0731c; font-size: 0.85rem; font-weight: bold; }
.fila { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; margin-bottom: 10px; }
.fila label, .otros { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; color: #333; }
.fila input, .fila select, .otros input, .tarea input { padding: 8px; border: 1px solid #ccd5df; border-radius: 4px; font: inherit; background: white; }
.fila select { max-width: 340px; }
.ancho { flex: 1; min-width: 220px; }
.bloque { border: 1px solid #dde3ea; border-radius: 8px; padding: 10px 14px 12px; margin: 0 0 14px; background: #fbfcfe; }
.bloque legend { font-weight: bold; color: #012169; padding: 0 6px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.chip { border: 1px solid #b9c6d6; background: white; color: #333; border-radius: 14px; padding: 4px 11px; cursor: pointer; font-size: 0.85rem; }
.chip.fuera { border-style: dashed; }
.chip.on { background: #012169; border-color: #012169; color: white; }

.audios { list-style: none; padding: 0; margin: 0 0 10px; display: flex; flex-direction: column; gap: 8px; }
.audios li { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; background: white; border: 1px solid #e1e7ee; border-radius: 6px; padding: 8px 10px; }
.audio-info { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 200px; }
.audio-info small { color: #666; }
.incompleto { color: #b0731c !important; }
.audios audio { height: 36px; max-width: 100%; }

.tarea { display: grid; grid-template-columns: auto 1fr 180px 150px auto; gap: 8px; align-items: center; margin-bottom: 6px; }
.tarea.hecha .texto { text-decoration: line-through; color: #888; }

.acciones { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-top: 6px; }
.derecha { margin-left: auto; }
.btn-principal { background: #012169; color: white; border: none; padding: 9px 18px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-aprobar { background: #198754; color: white; border: none; padding: 9px 16px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-grabar { background: #c62828; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 1rem; }
.btn-principal:disabled, .btn-aprobar:disabled, .btn-grabar:disabled { opacity: 0.6; cursor: wait; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 5px 10px; cursor: pointer; font-size: 0.85rem; text-decoration: none; color: inherit; }
.btn-mini.peligro { color: #b02a37; }

@media (max-width: 700px) {
  .panel-actas { padding: 16px; }
  .fila-acta { grid-template-columns: 1fr; gap: 4px; }
  .tarea { grid-template-columns: auto 1fr auto; }
  .tarea .resp, .tarea input[type="date"] { grid-column: 2 / 4; }
  .filtro select { min-width: 0; width: 100%; }
}
</style>
