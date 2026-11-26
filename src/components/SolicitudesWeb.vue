<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'

// Sol·licituds que arriben de la web (serveis i contacte): llegir-les, respondre per correu
// (el correu surt cap al sol·licitant amb còpia a sio@), canviar-ne l'estat i, si demanen
// dies (Pelagia, tanc, instrument), passar-los al calendari com a reserva.
const props = defineProps({ sesion: { type: Object, required: true }, inicial: { type: Number, default: null } })
const emit = defineEmits(['sesion-caducada', 'cambio'])
const { t, locale } = useI18n()
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })

const lista = ref([])
const actual = ref(null)
const filtro = ref('pendientes') // 'pendientes' | 'todas'
const error = ref('')
const mensaje = ref('')
const enviando = ref(false)
const respuesta = ref('')
const estadoTras = ref('') // estat després de respondre ('' = automàtic)

const ICONOS = { pelagia: '⛵', tanque: '🌊', instrumento: '🔧', salinidad: '🧂', fondeo: '⚓', prototipado: '🛠️', idi: '💡', contacto: '✉️' }
const ESTADOS = ['nova', 'en_curs', 'acceptada', 'rebutjada', 'tancada']
const fechaHora = (iso) => iso ? new Intl.DateTimeFormat(locale.value, { dateStyle: 'short', timeStyle: 'short' }).format(new Date(iso.replace(' ', 'T') + 'Z')) : ''
const fechaDia = (iso) => new Intl.DateTimeFormat(locale.value, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(iso + 'T12:00:00'))

const cargar = async () => {
  const r = await api('/api/solicitudes')
  if (r.ok) lista.value = await r.json()
  else error.value = t('intranet.comun.errorDesconocido')
}
onMounted(async () => { await cargar(); if (props.inicial) abrir(props.inicial) })

const visibles = computed(() => lista.value.filter(s => filtro.value === 'todas' || ['nova', 'en_curs'].includes(s.estado)))
const nNuevas = computed(() => lista.value.filter(s => s.estado === 'nova').length)

const abrir = async (id) => {
  error.value = ''; mensaje.value = ''; respuesta.value = ''; estadoTras.value = ''
  const r = await api(`/api/solicitudes/${id}`)
  if (!r.ok) { error.value = t('intranet.comun.errorDesconocido'); return }
  actual.value = await r.json()
  window.scrollTo?.({ top: 0, behavior: 'smooth' })
}
const volver = async () => { actual.value = null; await cargar(); emit('cambio') }
const refrescar = (d) => { actual.value = d; const i = lista.value.findIndex(s => s.id === d.id); if (i >= 0) lista.value[i] = { ...lista.value[i], estado: d.estado }; emit('cambio') }

const cambiarEstado = async (estado) => {
  const r = await api(`/api/solicitudes/${actual.value.id}`, json('PUT', { estado, notas: actual.value.notas }))
  if (r.ok) { refrescar(await r.json()); mensaje.value = t('intranet.solicitudes.guardado') }
}
const guardarNotas = async () => {
  const r = await api(`/api/solicitudes/${actual.value.id}`, json('PUT', { estado: actual.value.estado, notas: actual.value.notas }))
  if (r.ok) { refrescar(await r.json()); mensaje.value = t('intranet.solicitudes.guardado') }
}

// Plantilles de resposta, en l'idioma de qui ha fet la sol·licitud
const idiomaSol = computed(() => ['ca', 'es', 'en'].includes(actual.value?.idioma) ? actual.value.idioma : 'es')
const diasTexto = computed(() => (actual.value?.dias || []).map(d => new Intl.DateTimeFormat(idiomaSol.value, { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(d + 'T12:00:00'))).join(', '))
const PLANTILLAS = {
  aceptar: {
    ca: (s, d) => `Hola, ${s.nombre}:\n\nGràcies per la vostra sol·licitud. Us confirmem la reserva${d ? ' per als dies ' + d : ''}.\n\nPer a qualsevol dubte, responeu aquest correu.\n\nSalutacions,`,
    es: (s, d) => `Hola, ${s.nombre}:\n\nGracias por vuestra solicitud. Os confirmamos la reserva${d ? ' para los días ' + d : ''}.\n\nPara cualquier duda, responded a este correo.\n\nUn saludo,`,
    en: (s, d) => `Dear ${s.nombre},\n\nThank you for your request. We confirm the booking${d ? ' for ' + d : ''}.\n\nIf you have any questions, just reply to this email.\n\nBest regards,`
  },
  rechazar: {
    ca: (s, d) => `Hola, ${s.nombre}:\n\nGràcies per la vostra sol·licitud. Malauradament${d ? ' els dies ' + d : ''} no és possible. Si us va bé, proposeu-nos altres dates i ho mirarem.\n\nSalutacions,`,
    es: (s, d) => `Hola, ${s.nombre}:\n\nGracias por vuestra solicitud. Lamentablemente${d ? ' los días ' + d : ''} no es posible. Si os va bien, proponednos otras fechas y lo miraremos.\n\nUn saludo,`,
    en: (s, d) => `Dear ${s.nombre},\n\nThank you for your request. Unfortunately it is not possible${d ? ' on ' + d : ''}. If you like, suggest other dates and we will check.\n\nBest regards,`
  },
  info: {
    ca: (s) => `Hola, ${s.nombre}:\n\nGràcies per la vostra sol·licitud. Per poder-la tramitar necessitem una mica més d'informació:\n\n- \n\nSalutacions,`,
    es: (s) => `Hola, ${s.nombre}:\n\nGracias por vuestra solicitud. Para poder tramitarla necesitamos algo más de información:\n\n- \n\nUn saludo,`,
    en: (s) => `Dear ${s.nombre},\n\nThank you for your request. To process it we need a little more information:\n\n- \n\nBest regards,`
  }
}
const usarPlantilla = (clave) => {
  respuesta.value = PLANTILLAS[clave][idiomaSol.value](actual.value, diasTexto.value)
  estadoTras.value = { aceptar: 'acceptada', rechazar: 'rebutjada', info: 'en_curs' }[clave]
}
const enviarRespuesta = async () => {
  if (!respuesta.value.trim()) return
  if (!confirm(t('intranet.solicitudes.confirmarEnvio', { email: actual.value.email }))) return
  enviando.value = true; error.value = ''
  try {
    const r = await api(`/api/solicitudes/${actual.value.id}/respuesta`, json('POST', { texto: respuesta.value, estado: estadoTras.value || undefined }))
    const d = await r.json().catch(() => ({}))
    if (!r.ok) { error.value = traducirError(d.error) || t('intranet.comun.errorDesconocido'); return }
    refrescar(d); respuesta.value = ''; estadoTras.value = ''
    mensaje.value = t('intranet.solicitudes.enviada')
  } finally { enviando.value = false }
}
const pasarCalendario = async () => {
  if (!confirm(t('intranet.solicitudes.confirmarReserva'))) return
  const r = await api(`/api/solicitudes/${actual.value.id}/reserva`, { method: 'POST' })
  const d = await r.json().catch(() => ({}))
  if (!r.ok) { error.value = traducirError(d.error) || t('intranet.comun.errorDesconocido'); return }
  refrescar(d); mensaje.value = t('intranet.solicitudes.reservada')
}
const borrar = async () => {
  if (!confirm(t('intranet.solicitudes.confirmarBorrar'))) return
  const r = await api(`/api/solicitudes/${actual.value.id}`, { method: 'DELETE' })
  if (r.ok) volver()
}
</script>

<template>
  <div class="panel-sol">
    <h2>📬 {{ $t('intranet.solicitudes.titulo') }}</h2>
    <p class="ayuda">{{ $t('intranet.solicitudes.ayuda') }}</p>
    <p v-if="mensaje" class="ok" role="status">{{ mensaje }}</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <!-- LLISTA -->
    <template v-if="!actual">
      <div class="filtros">
        <button type="button" :class="{ on: filtro === 'pendientes' }" @click="filtro = 'pendientes'">{{ $t('intranet.solicitudes.pendientes') }}</button>
        <button type="button" :class="{ on: filtro === 'todas' }" @click="filtro = 'todas'">{{ $t('intranet.solicitudes.todas') }}</button>
        <span v-if="nNuevas" class="cuenta-nuevas">{{ $t('intranet.solicitudes.nuevas', { n: nNuevas }) }}</span>
      </div>
      <p v-if="!visibles.length" class="vacio">{{ $t('intranet.solicitudes.ninguna') }}</p>
      <ul class="lista">
        <li v-for="s in visibles" :key="s.id">
          <button type="button" class="fila" :class="s.estado" @click="abrir(s.id)">
            <span class="icono" aria-hidden="true">{{ ICONOS[s.tipo] || '📄' }}</span>
            <span class="que">
              <strong>{{ $t('intranet.solicitudes.tipos.' + s.tipo) }} · {{ s.nombre }}<template v-if="s.institucion"> ({{ s.institucion }})</template></strong>
              <small>{{ s.asunto.replace('[Web SIO] ', '') }}<template v-if="s.dias.length"> · 📅 {{ s.dias.map(d => fechaDia(d)).join(', ') }}</template></small>
            </span>
            <span class="lado">
              <span class="estado" :class="s.estado">{{ $t('intranet.solicitudes.estados.' + s.estado) }}</span>
              <small>{{ fechaHora(s.creado) }}</small>
            </span>
          </button>
        </li>
      </ul>
    </template>

    <!-- DETALL -->
    <template v-else>
      <div class="barra">
        <button type="button" class="btn-mini" @click="volver">← {{ $t('intranet.solicitudes.volver') }}</button>
        <span class="estado" :class="actual.estado">{{ $t('intranet.solicitudes.estados.' + actual.estado) }}</span>
        <small>nº {{ actual.id }} · {{ fechaHora(actual.creado) }}</small>
      </div>

      <section class="caja">
        <h3>{{ ICONOS[actual.tipo] }} {{ $t('intranet.solicitudes.tipos.' + actual.tipo) }}</h3>
        <dl class="datos">
          <dt>{{ $t('intranet.solicitudes.quien') }}</dt><dd>{{ actual.nombre }}<template v-if="actual.institucion"> · {{ actual.institucion }}</template></dd>
          <dt>{{ $t('intranet.solicitudes.correo') }}</dt><dd><a :href="`mailto:${actual.email}`">{{ actual.email }}</a></dd>
          <template v-if="actual.instrumento"><dt>{{ $t('intranet.solicitudes.instrumento') }}</dt><dd>{{ actual.instrumento }}</dd></template>
          <template v-if="actual.dias.length"><dt>{{ $t('intranet.solicitudes.dias') }}</dt><dd>{{ actual.dias.map(d => fechaDia(d)).join(', ') }}</dd></template>
          <template v-if="actual.tiene_adjunto"><dt>{{ $t('intranet.solicitudes.adjunto') }}</dt>
            <dd><a :href="actual.enlace_adjunto" target="_blank" rel="noopener">📎 {{ actual.adjunto_nombre }}</a>
              <span v-if="actual.tipo === 'instrumento'" :class="actual.adjunto_firmado ? 'firmado' : 'sin-firma'">
                {{ actual.adjunto_firmado ? '✔ ' + $t('intranet.solicitudes.firmado') : '⚠️ ' + $t('intranet.solicitudes.sinFirma') }}</span></dd></template>
        </dl>
        <pre class="cuerpo">{{ actual.cuerpo }}</pre>

        <div class="acciones">
          <template v-if="actual.puede_reservar">
            <button v-if="!actual.reserva_ids.length" type="button" class="btn-cal" @click="pasarCalendario">📅 {{ $t('intranet.solicitudes.pasarCalendario') }}</button>
            <span v-else class="firmado">✔ {{ $t('intranet.solicitudes.yaEnCalendario', { n: actual.reserva_ids.length }) }}</span>
          </template>
          <label class="cambiar">{{ $t('intranet.solicitudes.estado') }}
            <select :value="actual.estado" @change="cambiarEstado($event.target.value)">
              <option v-for="e in ESTADOS" :key="e" :value="e">{{ $t('intranet.solicitudes.estados.' + e) }}</option>
            </select>
          </label>
          <button v-if="sesion.es_admin" type="button" class="btn-mini peligro" @click="borrar">🗑️</button>
        </div>
      </section>

      <!-- Respostes -->
      <section class="caja">
        <h3>✉️ {{ $t('intranet.solicitudes.responder') }} <small>({{ $t('intranet.solicitudes.idiomaSol', { idioma: idiomaSol.toUpperCase() }) }})</small></h3>
        <div v-for="m in actual.mensajes" :key="m.id" class="mensaje">
          <small>{{ m.autor }} · {{ fechaHora(m.creado) }}</small>
          <pre>{{ m.texto }}</pre>
        </div>
        <div class="plantillas">
          <span>{{ $t('intranet.solicitudes.plantillas') }}</span>
          <button type="button" class="btn-mini" @click="usarPlantilla('aceptar')">✅ {{ $t('intranet.solicitudes.pAceptar') }}</button>
          <button type="button" class="btn-mini" @click="usarPlantilla('rechazar')">❌ {{ $t('intranet.solicitudes.pRechazar') }}</button>
          <button type="button" class="btn-mini" @click="usarPlantilla('info')">❓ {{ $t('intranet.solicitudes.pInfo') }}</button>
        </div>
        <textarea v-model="respuesta" rows="9" :placeholder="$t('intranet.solicitudes.respuestaPh')"></textarea>
        <div class="enviar">
          <label>{{ $t('intranet.solicitudes.estadoTras') }}
            <select v-model="estadoTras">
              <option value="">{{ $t('intranet.solicitudes.automatico') }}</option>
              <option v-for="e in ESTADOS.slice(1)" :key="e" :value="e">{{ $t('intranet.solicitudes.estados.' + e) }}</option>
            </select>
          </label>
          <button type="button" class="btn-principal" :disabled="enviando || !respuesta.trim()" @click="enviarRespuesta">📤 {{ $t('intranet.solicitudes.enviar', { email: actual.email }) }}</button>
        </div>
        <p class="nota">{{ $t('intranet.solicitudes.notaCopia') }}</p>
      </section>

      <section class="caja">
        <h3>🗒️ {{ $t('intranet.solicitudes.notas') }}</h3>
        <textarea v-model="actual.notas" rows="3" :placeholder="$t('intranet.solicitudes.notasPh')"></textarea>
        <button type="button" class="btn-mini" @click="guardarNotas">{{ $t('intranet.comun.guardar') }}</button>
      </section>
    </template>
  </div>
</template>

<style scoped>
.panel-sol { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #012169; }
.panel-sol h2 { margin: 0 0 6px; color: #012169; }
.ayuda { color: #555; font-size: 0.9rem; margin: 0 0 12px; }
.ok { color: #198754; font-weight: bold; }
.error { color: #b02a37; font-weight: bold; }
.vacio { color: #666; font-style: italic; }
.nota { color: #666; font-size: 0.82rem; margin: 6px 0 0; }
.filtros { display: flex; gap: 6px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
.filtros button { border: 1px solid #b9c6d6; background: white; border-radius: 16px; padding: 5px 14px; cursor: pointer; font: inherit; font-size: 0.88rem; }
.filtros button.on { background: #012169; color: white; border-color: #012169; }
.cuenta-nuevas { margin-left: auto; background: #c62828; color: white; border-radius: 12px; padding: 2px 10px; font-size: 0.82rem; font-weight: bold; }
.lista { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.fila { width: 100%; display: grid; grid-template-columns: 36px 1fr auto; gap: 12px; align-items: center; text-align: left; background: #f7f9fb; border: 1px solid #e1e7ee; border-left: 4px solid #9aa5b4; border-radius: 8px; padding: 10px 14px; cursor: pointer; font: inherit; color: inherit; }
.fila:hover { background: #eef3f9; }
.fila.nova { border-left-color: #c62828; background: #fff7f7; }
.fila.en_curs { border-left-color: #f0a640; }
.fila.acceptada { border-left-color: #198754; }
.icono { font-size: 1.5rem; text-align: center; }
.que { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.que strong { color: #012169; }
.que small { color: #555; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lado { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.lado small { color: #777; font-size: 0.78rem; }
.estado { display: inline-block; padding: 2px 9px; border-radius: 10px; font-size: 0.78rem; font-weight: bold; background: #eef1f4; color: #444; }
.estado.nova { background: #c62828; color: white; }
.estado.en_curs { background: #fff4e5; color: #7a4300; }
.estado.acceptada { background: #e6f4ea; color: #1e6b34; }
.estado.rebutjada { background: #fde8ea; color: #b02a37; }
.barra { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; }
.barra small { color: #777; }
.caja { border: 1px solid #dde3ea; border-radius: 8px; padding: 12px 16px; margin-bottom: 14px; background: #fbfcfe; }
.caja h3 { margin: 0 0 10px; color: #012169; font-size: 1.05rem; }
.caja h3 small { color: #777; font-weight: normal; font-size: 0.8rem; }
.datos { display: grid; grid-template-columns: max-content 1fr; gap: 4px 14px; margin: 0 0 10px; font-size: 0.92rem; }
.datos dt { color: #666; }
.datos dd { margin: 0; }
.cuerpo, .mensaje pre { white-space: pre-wrap; font: inherit; font-size: 0.92rem; background: white; border: 1px solid #e6ebf0; border-radius: 6px; padding: 10px 12px; margin: 0 0 10px; }
.mensaje small { color: #666; }
.firmado { color: #1e6b34; font-weight: bold; font-size: 0.88rem; margin-left: 8px; }
.sin-firma { color: #b02a37; font-weight: bold; font-size: 0.88rem; margin-left: 8px; }
.acciones, .enviar, .plantillas { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.plantillas { margin-bottom: 6px; font-size: 0.88rem; color: #555; }
.cambiar, .enviar label { display: flex; gap: 6px; align-items: center; font-size: 0.88rem; }
select, textarea { font: inherit; padding: 6px 8px; border: 1px solid #ccd5df; border-radius: 4px; }
textarea { width: 100%; box-sizing: border-box; margin-bottom: 8px; }
.btn-cal { background: #198754; color: white; border: none; border-radius: 6px; padding: 8px 14px; font-weight: bold; cursor: pointer; }
.btn-principal { background: #012169; color: white; border: none; padding: 9px 16px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-principal:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 5px 10px; cursor: pointer; font-size: 0.85rem; }
.btn-mini.peligro { color: #b02a37; margin-left: auto; }
@media (max-width: 700px) {
  .panel-sol { padding: 16px; }
  .fila { grid-template-columns: 30px 1fr; }
  .lado { grid-column: 2; flex-direction: row; align-items: center; }
}
</style>
