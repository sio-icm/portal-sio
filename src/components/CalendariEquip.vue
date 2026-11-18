<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'
import { peticionIntranet, hoyIso } from '../utils/diario'
import {
  TIPOS_CALENDARIO, tipoCalendario, RECURSOS, recurso, nombreReserva, ICONOS_AVISO,
  aIso, deIso, fechaLarga, rangoTexto, horario, resumenDia, nombreCorto, textoAviso
} from '../utils/calendario'
import DetalleDia from './DetalleDia.vue'

// Calendari d'equip: qui és al centre (teletreball, campanyes, vacances...),
// reserves de la Pelagia, el tanc i els instruments, i els avisos que en surten.
const props = defineProps({ sesion: { type: Object, required: true } })
const { t, locale } = useI18n()
const emit = defineEmits(['sesion-caducada', 'cambiado'])
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })

const hoy = hoyIso()
const DIAS_SEMANA = computed(() => t('intranet.comun.diasSemana').split(','))
const mesVisible = ref(new Date(deIso(hoy).getFullYear(), deIso(hoy).getMonth(), 1))
const diaSeleccionado = ref(hoy)
const datos = ref({ entradas: [], reservas: [], festius: [], equipo: [], avisos: [], ajustes: { minim_presents: 3, patro_pelagia: '' } })
const instrumentos = ref([])
const proyectos = ref([])
const cargando = ref(true)
const error = ref('')
const mensaje = ref('')

const nombreMes = computed(() => {
  const texto = new Intl.DateTimeFormat(locale.value, { month: 'long', year: 'numeric' }).format(mesVisible.value)
  return texto.charAt(0).toUpperCase() + texto.slice(1)
})

// Cel·les del mes, començant en dilluns
const celdas = computed(() => {
  const primero = mesVisible.value
  const desfase = (primero.getDay() + 6) % 7
  const diasMes = new Date(primero.getFullYear(), primero.getMonth() + 1, 0).getDate()
  const total = Math.ceil((desfase + diasMes) / 7) * 7
  return Array.from({ length: total }, (_, i) => {
    const d = new Date(primero.getFullYear(), primero.getMonth(), 1 - desfase + i)
    return { iso: aIso(d), dia: d.getDate(), delMes: d.getMonth() === primero.getMonth() }
  })
})
const resumenes = computed(() => Object.fromEntries(celdas.value.map(c => [c.iso, resumenDia(datos.value, c.iso)])))
const detalle = computed(() => resumenDia(datos.value, diaSeleccionado.value))
// Avisos: els passats ja no surten, i cadascú pot tancar els que ja ha vist (es recorda en
// aquest navegador). Al detall del dia sí que hi surten tots.
const leerCerrados = () => { try { return JSON.parse(localStorage.getItem('sio_avisos_cerrados') || '[]') } catch { return [] } }
const avisosCerrados = ref(new Set(leerCerrados()))
// «responsable:21:2026-11-12» → «responsable:21»: la data del final depèn del mes que es mira
const claveAviso = (a) => a.id.split(':').length > 2 ? a.id.replace(/:\d{4}-\d{2}-\d{2}$/, '') : a.id
const avisoVisible = (a) => (a.fin || a.fecha) >= hoy && !avisosCerrados.value.has(claveAviso(a))
const cerrarAviso = (a) => {
  avisosCerrados.value = new Set([...avisosCerrados.value, claveAviso(a)])
  try { localStorage.setItem('sio_avisos_cerrados', JSON.stringify([...avisosCerrados.value].slice(-300))) } catch { /* sense emmagatzematge */ }
}
const avisosMes = computed(() => {
  const inicio = aIso(mesVisible.value)
  const fin = aIso(new Date(mesVisible.value.getFullYear(), mesVisible.value.getMonth() + 1, 0))
  return datos.value.avisos.filter(a => (a.fin || a.fecha) >= inicio && a.fecha <= fin && avisoVisible(a))
})

const cargar = async () => {
  cargando.value = true
  error.value = ''
  const desde = celdas.value[0].iso
  const hasta = celdas.value[celdas.value.length - 1].iso
  try {
    const r = await api(`/api/calendario?desde=${desde}&hasta=${hasta}`)
    if (!r.ok) throw new Error()
    datos.value = await r.json()
  } catch {
    error.value = t('intranet.calendario.errorCarga')
  } finally {
    cargando.value = false
  }
}
watch(mesVisible, cargar)
onMounted(async () => {
  cargar()
  try {
    const [r, rp] = await Promise.all([api('/api/instrumentos'), api('/api/proyectos')])
    if (r.ok) instrumentos.value = (await r.json()).sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''))
    if (rp.ok) proyectos.value = (await rp.json()).sort((a, b) => (a.titulo || '').localeCompare(b.titulo || ''))
  } catch { /* les llistes són opcionals */ }
})

const moverMes = (salto) => {
  const d = mesVisible.value
  mesVisible.value = new Date(d.getFullYear(), d.getMonth() + salto, 1)
}
const irAHoy = () => {
  diaSeleccionado.value = hoy
  const d = deIso(hoy)
  if (d.getMonth() !== mesVisible.value.getMonth() || d.getFullYear() !== mesVisible.value.getFullYear()) {
    mesVisible.value = new Date(d.getFullYear(), d.getMonth(), 1)
  }
}
// En clicar un dia s'obre una finestra amb el seu detall (i també surt a sota del calendari)
const ventanaDia = ref(false)
const seleccionarDia = (c) => {
  diaSeleccionado.value = c.iso
  if (!c.delMes) mesVisible.value = new Date(deIso(c.iso).getFullYear(), deIso(c.iso).getMonth(), 1)
  ventanaDia.value = true
}
const verAviso = (a) => {
  diaSeleccionado.value = a.fecha
  ventanaDia.value = true
}
const teclaVentana = (ev) => { if (ev.key === 'Escape') ventanaDia.value = false }
watch(ventanaDia, (abierta) => {
  if (abierta) window.addEventListener('keydown', teclaVentana)
  else window.removeEventListener('keydown', teclaVentana)
})
onBeforeUnmount(() => window.removeEventListener('keydown', teclaVentana))
const desdeVentana = (accion, ...args) => {
  ventanaDia.value = false
  accion(...args)
}

// Chips d'una cel·la: qui és fora i les reserves. El que dura més d'una setmana (préstecs,
// vacances llargues) surt en una sola línia i al final, perquè no ompli tots els dies.
const LARGO = 7
const dias = (x) => Math.round((deIso(x.fin) - deIso(x.inicio)) / 86400000) + 1
const chips = (r) => chipsDia(r)
  .map(ch => ch.largo ? { ...ch, detalle: '' } : ch)
  .sort((a, b) => a.largo - b.largo)
const chipsDia = (r) => [
  ...r.entradas.map(e => ({
    clave: `e${e.id}`, color: tipoCalendario(e.tipo).color,
    largo: dias(e) > LARGO,
    texto: `${tipoCalendario(e.tipo).icono} ${e.persona ? nombreCorto(e.persona, datos.value.equipo) : t('intranet.comun.equipoCorto')}`,
    detalle: [horario(e), e.nota || e.proyecto].filter(Boolean).join(' · '),
    titulo: `${tipoCalendario(e.tipo).etiqueta}: ${e.persona || t('intranet.comun.todoEquipoMin')}${horario(e) ? ' · 🕘 ' + horario(e) : ''}${e.nota ? ' · ' + e.nota : ''}${e.proyecto ? ' · ' + e.proyecto : ''}`
  })),
  ...r.reservas.map(x => ({
    clave: `r${x.id}`, color: '#012169',
    largo: dias(x) > LARGO,
    texto: `${recurso(x.recurso).icono} ${nombreReserva(x)}`,
    detalle: [x.persona ? nombreCorto(x.persona, datos.value.equipo) : x.para, x.persona && x.para ? '→ ' + x.para : ''].filter(Boolean).join(' '),
    titulo: `${nombreReserva(x)}: ${x.persona || x.para}${x.proposito ? ' · ' + x.proposito : ''}`
  }))
]

// ---------- FORMULARIS ----------
const formulario = ref(null) // { clase: 'entrada'|'reserva', ... }
const errorFormulario = ref('')
const guardando = ref(false)

const nuevaEntrada = () => {
  errorFormulario.value = ''
  formulario.value = { clase: 'entrada', id: null, tipo: 'teletreball', usuario_id: props.sesion.usuario_id ?? '', inicio: diaSeleccionado.value, fin: diaSeleccionado.value, hora_inicio: '', hora_fin: '', nota: '', proyecto_id: '' }
}
const nuevaReserva = () => {
  errorFormulario.value = ''
  formulario.value = { clase: 'reserva', id: null, recurso: 'pelagia', instrumento_id: '', usuario_id: props.sesion.usuario_id ?? '', para: '', inicio: diaSeleccionado.value, fin: diaSeleccionado.value, proposito: '' }
}
const editar = (clase, x) => {
  errorFormulario.value = ''
  formulario.value = clase === 'entrada'
    ? { clase, id: x.id, tipo: x.tipo, usuario_id: x.usuario_id ?? '', inicio: x.inicio, fin: x.fin, hora_inicio: x.hora_inicio || '', hora_fin: x.hora_fin || '', nota: x.nota, proyecto_id: x.proyecto_id ?? '' }
    : { clase, id: x.id, recurso: x.recurso, instrumento_id: x.instrumento_id ?? '', usuario_id: x.usuario_id ?? '', para: x.para, inicio: x.inicio, fin: x.fin, proposito: x.proposito }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Persones que es poden triar: l'administrador, qualsevol; els altres, ells mateixos
const personasElegibles = computed(() => props.sesion.es_admin
  ? datos.value.equipo
  : datos.value.equipo.filter(u => u.id === props.sesion.usuario_id))
const permiteEquipo = computed(() => formulario.value?.clase === 'reserva' || ['reunio', 'altres'].includes(formulario.value?.tipo))

const guardar = async () => {
  const f = formulario.value
  if (f.fin < f.inicio) f.fin = f.inicio
  guardando.value = true
  errorFormulario.value = ''
  const base = f.clase === 'entrada' ? '/api/calendario/entradas' : '/api/calendario/reservas'
  const cuerpo = { ...f, usuario_id: f.usuario_id === '' ? null : f.usuario_id }
  try {
    const r = await api(f.id ? `${base}/${f.id}` : base, json(f.id ? 'PUT' : 'POST', cuerpo))
    if (!r.ok) {
      const d = await r.json().catch(() => ({}))
      errorFormulario.value = traducirError(d.error) || t('intranet.comun.noGuardado')
      return
    }
    mensaje.value = f.clase === 'entrada' ? t('intranet.calendario.guardadoEntrada') : t('intranet.calendario.guardadaReserva')
    diaSeleccionado.value = f.inicio
    formulario.value = null
    const d = deIso(f.inicio)
    if (d.getMonth() !== mesVisible.value.getMonth() || d.getFullYear() !== mesVisible.value.getFullYear()) {
      mesVisible.value = new Date(d.getFullYear(), d.getMonth(), 1) // el watch torna a carregar
    } else await cargar()
    emit('cambiado')
  } finally {
    guardando.value = false
  }
}

const borrar = async (clase, x) => {
  const fechas = rangoTexto(x.inicio, x.fin)
  const pregunta = clase === 'entrada'
    ? t('intranet.calendario.confirmarBorrarEntrada', { tipo: tipoCalendario(x.tipo).etiqueta, persona: x.persona || t('intranet.comun.todoEquipoMin'), fechas })
    : t('intranet.calendario.confirmarBorrarReserva', { recurso: nombreReserva(x), fechas })
  if (!confirm(pregunta)) return
  const r = await api(`/api/calendario/${clase === 'entrada' ? 'entradas' : 'reservas'}/${x.id}`, { method: 'DELETE' })
  if (r.ok) { mensaje.value = t('intranet.comun.borrado'); await cargar(); emit('cambiado') }
  else error.value = t('intranet.comun.noBorrado')
}

// ---------- CONFIGURACIÓ (administradors) ----------
const verConfig = ref(false)
const festius = ref([])
const nuevoFestiu = ref({ fecha: '', nombre: '' })
const ajustesForm = ref({ minim_presents: 3, patro_pelagia: '' })
const abrirConfig = async () => {
  verConfig.value = !verConfig.value
  if (!verConfig.value) return
  ajustesForm.value = { ...datos.value.ajustes }
  const r = await api('/api/calendario/festius')
  if (r.ok) festius.value = (await r.json()).filter(f => f.fecha >= `${new Date().getFullYear()}-01-01`)
}
const resultado = async (r, ok) => {
  if (r.ok) { mensaje.value = ok; error.value = ''; await cargar(); emit('cambiado'); return true }
  const d = await r.json().catch(() => ({}))
  error.value = traducirError(d.error) || t('intranet.comun.errorDesconocido')
  return false
}
// La configuració s'obre des de la finestra del dia (només administradors)
const abrirConfigVentana = async () => {
  if (!verConfig.value) await abrirConfig()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
const guardarAjustes = async () => resultado(await api('/api/calendario/ajustes', json('PUT', ajustesForm.value)), t('intranet.calendario.configGuardada'))
const afegirFestiu = async () => {
  if (await resultado(await api('/api/calendario/festius', json('POST', nuevoFestiu.value)), t('intranet.calendario.festivoAnadido'))) {
    nuevoFestiu.value = { fecha: '', nombre: '' }
    verConfig.value = false
    await abrirConfig()
  }
}
const treureFestiu = async (f) => {
  if (!confirm(t('intranet.calendario.confirmarQuitarFestivo', { nombre: f.nombre, fecha: rangoTexto(f.fecha, f.fecha) }))) return
  if (await resultado(await api(`/api/calendario/festius/${f.fecha}`, { method: 'DELETE' }), t('intranet.calendario.festivoQuitado'))) {
    festius.value = festius.value.filter(x => x.fecha !== f.fecha)
  }
}
</script>

<template>
  <div class="panel-calendari">
    <div class="cabecera">
      <div>
        <h2>{{ $t('intranet.calendario.titulo') }}</h2>
        <p class="ayuda">{{ $t('intranet.calendario.ayuda') }}</p>
      </div>
    </div>

    <p v-if="mensaje" class="ok">{{ mensaje }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <!-- Configuració -->
    <div v-if="verConfig" class="caja config">
      <h3>{{ $t('intranet.calendario.configTitulo') }}</h3>
      <form class="fila" @submit.prevent="guardarAjustes">
        <label>{{ $t('intranet.calendario.avisarSiMenos') }}
          <span class="en-linea"><input type="number" min="0" max="50" v-model.number="ajustesForm.minim_presents" class="corto"> {{ $t('intranet.calendario.personas') }}</span>
        </label>
        <label>{{ $t('intranet.calendario.patron') }}
          <select v-model="ajustesForm.patro_pelagia">
            <option value="">{{ $t('intranet.comun.ninguno') }}</option>
            <option v-for="u in datos.equipo" :key="u.id" :value="u.usuario">{{ u.nombre }}</option>
          </select>
        </label>
        <button type="submit" class="btn-principal">{{ $t('intranet.comun.guardar') }}</button>
      </form>
      <p class="ayuda">{{ $t('intranet.calendario.plantillaAyuda', { n: datos.equipo.filter(u => u.plantilla).length, nombres: datos.equipo.filter(u => u.plantilla).map(u => nombreCorto(u.nombre, datos.equipo)).join(', ') }) }}</p>

      <h3>{{ $t('intranet.calendario.festivosTitulo') }}</h3>
      <p class="ayuda">{{ $t('intranet.calendario.festivosAyuda') }}</p>
      <ul class="festius">
        <li v-for="f in festius" :key="f.fecha">
          <span>{{ rangoTexto(f.fecha, f.fecha) }} {{ f.fecha.slice(0, 4) }} · {{ f.nombre }}</span>
          <button class="btn-mini peligro" @click="treureFestiu(f)" :aria-label="$t('intranet.calendario.quitarFestivo', { nombre: f.nombre })">✕</button>
        </li>
      </ul>
      <form class="fila" @submit.prevent="afegirFestiu">
        <label>{{ $t('intranet.calendario.fecha') }} <input type="date" v-model="nuevoFestiu.fecha" required></label>
        <label class="ancho">{{ $t('intranet.calendario.nombre') }} <input v-model="nuevoFestiu.nombre" maxlength="100" :placeholder="$t('intranet.calendario.festivoPh')" required></label>
        <button type="submit" class="btn-secundario">{{ $t('intranet.calendario.anadirFestivo') }}</button>
      </form>
    </div>

    <!-- Formulari -->
    <form v-if="formulario" class="caja formulario" @submit.prevent="guardar">
      <h3>{{ $t(formulario.clase === 'entrada' ? (formulario.id ? 'intranet.calendario.editarEntrada' : 'intranet.calendario.nuevaEntrada') : (formulario.id ? 'intranet.calendario.editarReserva' : 'intranet.calendario.nuevaReserva')) }}</h3>
      <div class="fila">
        <template v-if="formulario.clase === 'entrada'">
          <label>{{ $t('intranet.calendario.que') }}
            <select v-model="formulario.tipo">
              <option v-for="t in TIPOS_CALENDARIO" :key="t.valor" :value="t.valor">{{ t.icono }} {{ t.etiqueta }}</option>
            </select>
          </label>
        </template>
        <template v-else>
          <label>{{ $t('intranet.calendario.recurso') }}
            <select v-model="formulario.recurso">
              <option v-for="r in RECURSOS" :key="r.valor" :value="r.valor">{{ r.icono }} {{ r.etiqueta }}</option>
            </select>
          </label>
          <label v-if="formulario.recurso === 'instrument'" class="ancho">{{ $t('intranet.calendario.instrumento') }}
            <select v-model="formulario.instrumento_id" required>
              <option value="" disabled>{{ $t('intranet.calendario.eligeInstrumento') }}</option>
              <option v-for="i in instrumentos" :key="i.id" :value="i.id">{{ i.nombre }}{{ i.numero_serie ? ` (${i.numero_serie})` : '' }}</option>
            </select>
          </label>
        </template>
        <label>{{ $t(formulario.clase === 'entrada' ? 'intranet.calendario.quien' : 'intranet.calendario.responsable') }}
          <select v-model="formulario.usuario_id">
            <option v-if="personasElegibles.length === 0 && !permiteEquipo" value="" disabled>{{ $t('intranet.calendario.eligePersona') }}</option>
            <option v-for="u in personasElegibles" :key="u.id" :value="u.id">{{ u.nombre }}</option>
            <option v-if="formulario.clase === 'entrada' && permiteEquipo" value="">{{ $t('intranet.comun.todoEquipo') }}</option>
            <option v-if="formulario.clase === 'reserva' && sesion.es_admin" value="">{{ $t('intranet.calendario.alguienFuera') }}</option>
          </select>
        </label>
        <label>{{ $t('intranet.calendario.desde') }} <input type="date" v-model="formulario.inicio" required></label>
        <label>{{ $t('intranet.calendario.hastaFecha') }} <input type="date" v-model="formulario.fin" :min="formulario.inicio" required></label>
      </div>
      <div class="fila">
        <label v-if="formulario.clase === 'reserva'" class="ancho">{{ $t('intranet.calendario.para') }}
          <input v-model="formulario.para" maxlength="200" :required="formulario.usuario_id === ''" :placeholder="$t('intranet.calendario.paraPh')">
        </label>
        <template v-if="formulario.clase === 'entrada'">
          <label>{{ $t('intranet.calendario.horaInicio') }} <input type="time" v-model="formulario.hora_inicio" step="300"></label>
          <label>{{ $t('intranet.calendario.horaFin') }} <input type="time" v-model="formulario.hora_fin" step="300"
            :min="formulario.inicio === formulario.fin ? formulario.hora_inicio : undefined"></label>
        </template>
        <label v-if="formulario.clase === 'entrada' && !['teletreball', 'vacances', 'baixa'].includes(formulario.tipo)">{{ $t('intranet.calendario.proyecto') }}
          <select v-model="formulario.proyecto_id">
            <option value="">{{ $t('intranet.comun.cap') }}</option>
            <option v-for="p in proyectos" :key="p.id" :value="p.id">{{ p.titulo }}</option>
          </select>
        </label>
        <label class="ancho">{{ $t(formulario.clase === 'entrada' ? 'intranet.calendario.nota' : 'intranet.calendario.motivo') }}
          <input v-if="formulario.clase === 'entrada'" v-model="formulario.nota" maxlength="500" :placeholder="$t('intranet.calendario.notaPh')">
          <input v-else v-model="formulario.proposito" maxlength="500" :placeholder="$t('intranet.calendario.motivoPh')">
        </label>
      </div>
      <p v-if="errorFormulario" class="error">{{ errorFormulario }}</p>
      <div class="botones">
        <button type="submit" class="btn-principal" :disabled="guardando">{{ $t('intranet.comun.guardar') }}</button>
        <button type="button" class="btn-secundario" @click="formulario = null">{{ $t('intranet.comun.cancelar') }}</button>
      </div>
    </form>

    <!-- Avisos del mes -->
    <div v-if="avisosMes.length" class="avisos-mes" role="status">
      <strong>{{ $t('intranet.calendario.avisosDe', { mes: locale === 'en' ? nombreMes : nombreMes.toLowerCase() }) }}</strong>
      <span v-for="a in avisosMes" :key="a.id" class="aviso-chip">
        <button type="button" class="aviso-texto" @click="verAviso(a)">{{ ICONOS_AVISO[a.tipo] }} {{ rangoTexto(a.fecha, a.fin || a.fecha) }} · {{ textoAviso(a) }}</button>
        <button type="button" class="aviso-cerrar" :title="$t('intranet.calendario.cerrarAviso')" :aria-label="$t('intranet.calendario.cerrarAviso')" @click="cerrarAviso(a)">✕</button>
      </span>
    </div>

    <!-- Calendari -->
    <div class="calendario">
      <div class="cal-cabecera">
        <button type="button" class="btn-mini" @click="moverMes(-1)" :aria-label="$t('intranet.comun.mesAnterior')">◀</button>
        <span class="cal-mes">{{ nombreMes }}</span>
        <button type="button" class="btn-mini" @click="moverMes(1)" :aria-label="$t('intranet.comun.mesSiguiente')">▶</button>
        <button type="button" class="btn-mini" @click="irAHoy">{{ $t('intranet.comun.hoy') }}</button>
        <span v-if="cargando" class="cargando">{{ $t('intranet.comun.cargando') }}</span>
      </div>
      <div class="cal-grid">
        <div v-for="d in DIAS_SEMANA" :key="d" class="cal-dia-semana">{{ d }}</div>
        <button v-for="c in celdas" :key="c.iso" type="button" class="cal-celda"
          :class="{ fuera: !c.delMes, hoy: c.iso === hoy, elegido: c.iso === diaSeleccionado,
                    festivo: !resumenes[c.iso].laborable, alerta: resumenes[c.iso].avisos.some(avisoVisible) }"
          :aria-label="fechaLarga(c.iso)" :aria-pressed="c.iso === diaSeleccionado" @click="seleccionarDia(c)">
          <span class="cal-numero">{{ c.dia }}<span v-if="resumenes[c.iso].avisos.some(avisoVisible)" class="marca-aviso" aria-hidden="true">⚠️</span></span>
          <span v-if="resumenes[c.iso].festiu" class="cal-festiu" :title="resumenes[c.iso].festiu">{{ resumenes[c.iso].festiu }}</span>
          <span v-for="ch in chips(resumenes[c.iso])" :key="ch.clave" class="cal-chip" :style="{ background: ch.color }" :title="ch.titulo">
            <span class="chip-texto">{{ ch.texto }}</span><span v-if="ch.detalle" class="chip-detalle">{{ ch.detalle }}</span>
          </span>
        </button>
      </div>
      <p class="leyenda">
        <span v-for="t in TIPOS_CALENDARIO" :key="t.valor"><i :style="{ background: t.color }"></i>{{ t.etiqueta }}</span>
        <span><i style="background: #012169"></i>{{ $t('intranet.calendario.reserva') }}</span>
      </p>
    </div>

    <!-- Detall del dia (a sota) -->
    <section class="caja detalle" aria-live="polite">
      <DetalleDia :detalle="detalle" :equipo="datos.equipo" @editar="editar" @borrar="borrar" />
    </section>

    <!-- Finestra amb el detall del dia clicat -->
    <div v-if="ventanaDia" class="velo" @click.self="ventanaDia = false">
      <div class="ventana" role="dialog" aria-modal="true" :aria-label="fechaLarga(detalle.dia)">
        <header>
          <h3>{{ fechaLarga(detalle.dia) }}</h3>
          <button type="button" class="cerrar" :aria-label="$t('intranet.comun.cerrar')" @click="ventanaDia = false">✕</button>
        </header>
        <DetalleDia :detalle="detalle" :equipo="datos.equipo" :titulo="false"
          @editar="(c, x) => desdeVentana(editar, c, x)" @borrar="(c, x) => desdeVentana(borrar, c, x)" />
        <footer>
          <button class="btn-principal" @click="desdeVentana(nuevaEntrada)">{{ $t('intranet.calendario.apuntarme') }}</button>
          <button class="btn-secundario" @click="desdeVentana(nuevaReserva)">{{ $t('intranet.calendario.reservar') }}</button>
          <button v-if="sesion.es_admin" class="btn-secundario config-btn" @click="desdeVentana(abrirConfigVentana)">{{ $t('intranet.calendario.configuracion') }}</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-calendari { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #0086c0; }
.cabecera { display: flex; justify-content: space-between; gap: 15px; flex-wrap: wrap; align-items: flex-start; }
h2 { margin: 0; color: #012169; }
h3 { margin: 0 0 10px; color: #012169; }
.ayuda { color: #666; font-size: 0.9rem; margin: 6px 0 12px; }
.botones { display: flex; gap: 8px; flex-wrap: wrap; }
.btn-principal { background: #012169; color: white; border: none; padding: 9px 16px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-principal:disabled { opacity: 0.6; cursor: wait; }
.btn-secundario { background: #f4f7f9; color: #012169; border: 1px solid #c9d3dd; padding: 8px 14px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.8rem; }
.btn-mini.peligro { color: #b02a37; }
.ok { color: #198754; font-weight: bold; }
.error { color: #b02a37; font-weight: bold; }
.caja { background: #f4f7f9; border-radius: 8px; padding: 15px 20px; margin: 12px 0; }
.fila { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; margin-bottom: 10px; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; font-weight: bold; color: #444; }
.ancho { flex: 1; min-width: 200px; }
.en-linea { display: flex; align-items: center; gap: 6px; font-weight: normal; }
input, select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font: inherit; font-weight: normal; background: white; }
input.corto { width: 70px; }
.festius { list-style: none; padding: 0; margin: 0 0 10px; columns: 2; font-size: 0.85rem; }
.festius li { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 2px 0; break-inside: avoid; }

.avisos-mes { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; background: #fff4e5; border: 1px solid #ffd59e; border-radius: 8px; padding: 10px 12px; margin: 12px 0; font-size: 0.9rem; color: #7a4300; }
.aviso-chip { display: inline-flex; align-items: center; background: white; border: 1px solid #ffd59e; border-radius: 12px; font-size: 0.82rem; overflow: hidden; }
.aviso-texto { background: none; border: none; padding: 3px 4px 3px 10px; cursor: pointer; font: inherit; color: #7a4300; text-align: left; }
.aviso-cerrar { background: none; border: none; border-left: 1px solid #ffe3bd; padding: 3px 8px; cursor: pointer; color: #b0731c; font-size: 0.8rem; }
.aviso-cerrar:hover { background: #ffe9cc; color: #7a4300; }

/* Finestra del dia */
.velo { position: fixed; inset: 0; background: rgba(1, 20, 60, 0.45); display: flex; align-items: center; justify-content: center; padding: 16px; z-index: 10000; }
.ventana { background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.25); width: min(620px, 100%); max-height: 85vh; overflow-y: auto; padding: 18px 20px; border-top: 4px solid #0086c0; }
.ventana header { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 6px; }
.ventana header h3 { margin: 0; }
.ventana header h3::first-letter { text-transform: uppercase; }
.ventana .cerrar { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #555; padding: 0 4px; line-height: 1; }
.ventana footer .config-btn { margin-left: auto; }
.ventana footer { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; padding-top: 12px; border-top: 1px solid #e3e8ee; }

.calendario { border: 1px solid #e3e8ee; border-radius: 8px; padding: 12px; margin: 12px 0; }
.cal-cabecera { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
.cal-mes { font-weight: bold; color: #012169; font-size: 1.1rem; min-width: 170px; text-align: center; }
.cargando { color: #666; font-size: 0.85rem; }
.cal-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1.25fr)) repeat(2, minmax(0, 0.75fr)); gap: 4px; }
.cal-dia-semana { text-align: center; font-size: 0.75rem; font-weight: bold; color: #666; padding: 4px 0; }
.cal-celda { min-height: 96px; border: 1px solid #e3e8ee; border-radius: 6px; background: white; padding: 4px; display: flex; flex-direction: column; gap: 2px; align-items: stretch; text-align: left; cursor: pointer; font: inherit; overflow: hidden; }
.cal-celda:hover { border-color: #0086c0; }
.cal-celda.festivo { background: #f6f6f6; }
.cal-celda.fuera { opacity: 0.45; }
.cal-celda.alerta { border-color: #f0a640; background: #fffaf2; }
.cal-celda.hoy .cal-numero { background: #0086c0; color: white; border-radius: 10px; padding: 0 6px; }
.cal-celda.elegido { border: 2px solid #012169; box-shadow: 0 0 0 2px rgba(1,33,105,0.12); }
.cal-numero { font-size: 0.8rem; font-weight: bold; align-self: flex-start; }
.marca-aviso { font-size: 0.7rem; margin-left: 3px; }
.cal-festiu { font-size: 0.68rem; color: #b02a37; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cal-chip { color: white; font-size: 0.76rem; line-height: 1.25; border-radius: 4px; padding: 2px 6px; display: flex; flex-direction: column; overflow: hidden; }
.chip-texto { font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chip-detalle { font-size: 0.7rem; opacity: 0.92; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; word-break: break-word; }
.leyenda { display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 0.78rem; color: #555; margin: 10px 0 0; }
.leyenda i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; vertical-align: -1px; }

.vacio { color: #666; font-style: italic; }

@media (max-width: 768px) {
  .panel-calendari { padding: 14px; }
  .calendario { padding: 6px; }
  .cal-grid { gap: 2px; }
  .cal-mes { min-width: 0; font-size: 1rem; }
  .cal-celda { min-height: 52px; padding: 3px; }
  .cal-festiu { font-size: 0; height: 3px; background: #b02a37; border-radius: 2px; }
  .cal-grid { grid-template-columns: repeat(7, minmax(0, 1fr)); }
  .cal-chip { font-size: 0; height: 6px; padding: 0; }
  .chip-detalle { display: none; }
  .festius { columns: 1; }
}
</style>
