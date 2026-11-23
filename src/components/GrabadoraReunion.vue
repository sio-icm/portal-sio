<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'

// Gravar una reunió des del navegador (mòbil o ordinador) o pujar un àudio ja gravat.
// Abans de gravar surt un avís: s'ha d'avisar els assistents i és millor que cadascú es
// presenti al començament (així se sap qui parla). L'àudio es puja a trossos de 5 s mentre
// es grava: si la connexió falla es reintenta, i si no hi ha manera es pot descarregar
// el que s'ha gravat perquè no es perdi.
const props = defineProps({
  actaId: { type: Number, required: true },
  api: { type: Function, required: true }
})
const emit = defineEmits(['cambio'])
const { t, locale } = useI18n()

const TROZO_MS = 5000
const TROZO_ARCHIVO = 2 * 1024 * 1024
const MAX_ARCHIVO = 400 * 1024 * 1024
const soportado = typeof window !== 'undefined' && !!navigator.mediaDevices?.getUserMedia && typeof window.MediaRecorder !== 'undefined'

const estado = ref('') // '' | 'aviso' | 'grabando' | 'pausa' | 'acabando'
const avisados = ref(false)
const error = ref('')
const segundos = ref(0)
const nivel = ref(0)
const pendientes = ref(0)
const sinConexion = ref(false)
const copiaLocal = ref(null) // { url, nombre } si no s'ha pogut pujar
const archivo = ref(null) // { nombre, pct } mentre es puja un fitxer

let recorder = null, stream = null, audio = null, cola = [], todos = [], n = 0, subiendo = null
let reloj = null, acumulado = 0, inicioTramo = 0, ctxAudio = null, rafId = null, wakeLock = null, tipoGrabacion = ''

const espera = (ms) => new Promise(r => setTimeout(r, ms))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })
const reloj2 = (s) => `${Math.floor(s / 3600) ? Math.floor(s / 3600) + ':' : ''}${String(Math.floor(s / 60) % 60).padStart(2, '0')}:${String(Math.floor(s % 60)).padStart(2, '0')}`
const tiempo = computed(() => reloj2(segundos.value))
const grabando = computed(() => ['grabando', 'pausa', 'acabando'].includes(estado.value))
const nombreGrabacion = () => `${t('intranet.actas.grabacion')} ${new Intl.DateTimeFormat(locale.value, { dateStyle: 'short', timeStyle: 'short' }).format(new Date())}`

class ErrorPermanente extends Error {}

// Envia un tros; reintenta si falla la xarxa o el servidor (fins que torni la connexió)
const enviarTrozo = async (id, num, blob) => {
  for (let intento = 0; ; intento++) {
    let r = null
    try {
      r = await props.api(`/api/actas/audios/${id}/trozo?n=${num}`, { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: blob })
    } catch { r = null }
    if (r && r.ok) { sinConexion.value = false; return }
    if (r) {
      const d = await r.json().catch(() => ({}))
      if (r.status === 409 && d.trozos > num) return // ja hi era
      if (r.status === 401 || r.status === 403 || r.status === 413 || r.status === 507 || (r.status >= 400 && r.status < 500 && r.status !== 408 && r.status !== 429)) {
        throw new ErrorPermanente(traducirError(d.error) || t('intranet.comun.errorDesconocido'))
      }
    }
    sinConexion.value = true
    await espera(Math.min(20000, 1000 * 2 ** Math.min(intento, 5)))
  }
}

const procesarCola = () => {
  if (!subiendo) {
    subiendo = (async () => {
      try {
        while (cola.length) {
          await enviarTrozo(audio.id, cola[0].num, cola[0].blob)
          cola.shift()
          pendientes.value = cola.length
        }
      } finally { subiendo = null }
    })()
  }
  return subiendo
}

// ---------- Gravar ----------
const abrir = () => { error.value = ''; copiaLocal.value = null; avisados.value = false; estado.value = 'aviso' }
defineExpose({ abrir })

const medir = (s) => {
  try {
    ctxAudio = new (window.AudioContext || window.webkitAudioContext)()
    ctxAudio.resume?.().catch(() => {})
    const analizador = ctxAudio.createAnalyser()
    analizador.fftSize = 512
    ctxAudio.createMediaStreamSource(s).connect(analizador)
    const datos = new Uint8Array(analizador.fftSize)
    const paso = () => {
      analizador.getByteTimeDomainData(datos)
      let suma = 0
      for (const v of datos) suma += ((v - 128) / 128) ** 2
      nivel.value = Math.min(1, Math.sqrt(suma / datos.length) * 4)
      rafId = requestAnimationFrame(paso)
    }
    paso()
  } catch { /* sense mesurador */ }
}
const pedirPantalla = async () => {
  try { wakeLock = await navigator.wakeLock?.request('screen') } catch { wakeLock = null }
}
const alVolver = () => { if (document.visibilityState === 'visible' && grabando.value) pedirPantalla() }
const alSalir = (e) => { if (grabando.value || pendientes.value) { e.preventDefault(); e.returnValue = '' } }

const empezar = async () => {
  error.value = ''
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } })
  } catch (e) {
    error.value = t(e?.name === 'NotAllowedError' ? 'intranet.actas.sinPermisoMicro' : 'intranet.actas.sinMicro')
    estado.value = ''
    return
  }
  tipoGrabacion = ['audio/webm;codecs=opus', 'audio/mp4', 'audio/ogg;codecs=opus', 'audio/webm'].find(x => MediaRecorder.isTypeSupported?.(x)) || ''
  try {
    recorder = new MediaRecorder(stream, { ...(tipoGrabacion ? { mimeType: tipoGrabacion } : {}), audioBitsPerSecond: 32000 })
  } catch {
    recorder = new MediaRecorder(stream)
  }
  const r = await props.api(`/api/actas/${props.actaId}/audios`, json('POST', { tipo: recorder.mimeType || tipoGrabacion || 'audio/webm', nombre: nombreGrabacion(), avisados: avisados.value }))
  const d = await r.json().catch(() => ({}))
  if (!r.ok) {
    error.value = traducirError(d.error) || t('intranet.comun.errorDesconocido')
    stream.getTracks().forEach(tr => tr.stop())
    estado.value = ''
    return
  }
  audio = d; cola = []; todos = []; n = 0; pendientes.value = 0; sinConexion.value = false
  recorder.ondataavailable = (e) => {
    if (!e.data || !e.data.size) return
    todos.push(e.data)
    cola.push({ num: n++, blob: e.data })
    pendientes.value = cola.length
    procesarCola().catch(fallo)
  }
  recorder.onstop = acabar
  recorder.start(TROZO_MS)
  acumulado = 0; inicioTramo = Date.now(); segundos.value = 0
  reloj = setInterval(() => { segundos.value = (acumulado + (estado.value === 'grabando' ? Date.now() - inicioTramo : 0)) / 1000 }, 500)
  estado.value = 'grabando'
  medir(stream)
  pedirPantalla()
  document.addEventListener('visibilitychange', alVolver)
  window.addEventListener('beforeunload', alSalir)
}

const pausar = () => {
  if (recorder?.state !== 'recording') return
  recorder.pause(); acumulado += Date.now() - inicioTramo; estado.value = 'pausa'
}
const continuar = () => {
  if (recorder?.state !== 'paused') return
  recorder.resume(); inicioTramo = Date.now(); estado.value = 'grabando'
}
const parar = () => {
  if (!recorder || recorder.state === 'inactive') return
  if (estado.value === 'grabando') acumulado += Date.now() - inicioTramo
  estado.value = 'acabando'
  recorder.stop() // el darrer tros arriba abans d'onstop
}

const soltar = () => {
  clearInterval(reloj)
  if (rafId) cancelAnimationFrame(rafId)
  try { ctxAudio?.close() } catch { /* res */ }
  stream?.getTracks().forEach(tr => tr.stop())
  try { wakeLock?.release() } catch { /* res */ }
  wakeLock = null; nivel.value = 0
  document.removeEventListener('visibilitychange', alVolver)
}

// Si la pujada falla del tot: es para i es pot descarregar el que s'ha gravat
const fallo = (e) => {
  if (!(e instanceof ErrorPermanente)) return
  error.value = e.message
  if (recorder && recorder.state !== 'inactive') { recorder.onstop = null; recorder.stop() }
  soltar()
  ofrecerCopia()
  estado.value = ''
  window.removeEventListener('beforeunload', alSalir)
}
const ofrecerCopia = () => {
  if (!todos.length) return
  const tipo = (recorder?.mimeType || tipoGrabacion || 'audio/webm').split(';')[0]
  const ext = tipo.includes('mp4') ? 'm4a' : tipo.includes('ogg') ? 'ogg' : 'webm'
  copiaLocal.value = { url: URL.createObjectURL(new Blob(todos, { type: tipo })), nombre: `${nombreGrabacion().replace(/[^\w\d-]+/g, '_')}.${ext}` }
}

const acabar = async () => {
  soltar()
  try {
    while (cola.length || subiendo) await procesarCola()
    const r = await props.api(`/api/actas/audios/${audio.id}`, json('PUT', { duracion: Math.round(acumulado / 1000) }))
    if (!r.ok) throw new ErrorPermanente(traducirError((await r.json().catch(() => ({}))).error) || t('intranet.comun.errorDesconocido'))
    estado.value = ''
    emit('cambio')
  } catch (e) {
    error.value = e.message || t('intranet.comun.errorDesconocido')
    ofrecerCopia()
    estado.value = ''
    emit('cambio')
  } finally {
    window.removeEventListener('beforeunload', alSalir)
  }
}

onBeforeUnmount(() => {
  // Si se surt de la pàgina mentre es grava, es para i s'acaba de pujar el que hi ha
  if (recorder && recorder.state !== 'inactive') parar()
})

// ---------- Pujar un fitxer d'àudio (p. ex. la gravadora del mòbil) ----------
const duracionArchivo = (f) => new Promise((resolve) => {
  const url = URL.createObjectURL(f)
  const a = new Audio()
  const fin = (v) => { URL.revokeObjectURL(url); resolve(Number.isFinite(v) ? Math.round(v) : 0) }
  a.preload = 'metadata'
  a.onloadedmetadata = () => fin(a.duration)
  a.onerror = () => fin(0)
  setTimeout(() => fin(0), 8000)
  a.src = url
})
const subirArchivo = async (ev) => {
  const f = ev.target.files?.[0]
  ev.target.value = ''
  if (!f) return
  error.value = ''
  if (f.size > MAX_ARCHIVO) { error.value = t('intranet.actas.archivoGrande'); return }
  const r = await props.api(`/api/actas/${props.actaId}/audios`, json('POST', { tipo: f.type, nombre: f.name, avisados: false }))
  const d = await r.json().catch(() => ({}))
  if (!r.ok) { error.value = traducirError(d.error) || t('intranet.comun.errorDesconocido'); return }
  archivo.value = { nombre: f.name, pct: 0 }
  window.addEventListener('beforeunload', alSalir)
  pendientes.value = 1
  try {
    const total = Math.max(1, Math.ceil(f.size / TROZO_ARCHIVO))
    for (let i = 0; i < total; i++) {
      await enviarTrozo(d.id, i, f.slice(i * TROZO_ARCHIVO, (i + 1) * TROZO_ARCHIVO))
      archivo.value.pct = Math.round(100 * (i + 1) / total)
    }
    const rf = await props.api(`/api/actas/audios/${d.id}`, json('PUT', { duracion: await duracionArchivo(f) }))
    if (!rf.ok) throw new Error(traducirError((await rf.json().catch(() => ({}))).error) || '')
  } catch (e) {
    error.value = e.message || t('intranet.comun.errorDesconocido')
  } finally {
    archivo.value = null
    pendientes.value = 0
    window.removeEventListener('beforeunload', alSalir)
    emit('cambio')
  }
}
</script>

<template>
  <div class="grabadora">
    <div v-if="!grabando && !archivo" class="botones">
      <button type="button" class="btn-grabar" :disabled="!soportado" @click="abrir">🎙️ {{ $t('intranet.actas.grabar') }}</button>
      <label class="btn-subir">⬆️ {{ $t('intranet.actas.subirAudio') }}
        <input type="file" accept="audio/*,.m4a,.mp3,.wav,.ogg,.opus,.webm,.aac,.3gp,.amr" @change="subirArchivo">
      </label>
    </div>
    <p v-if="!soportado && !grabando" class="nota">{{ $t('intranet.actas.noSoportado') }}</p>

    <!-- Gravant -->
    <div v-if="grabando" class="en-curso" :class="{ pausa: estado === 'pausa' }" role="status">
      <div class="linea">
        <span class="punto" aria-hidden="true"></span>
        <strong>{{ estado === 'pausa' ? $t('intranet.actas.enPausa') : estado === 'acabando' ? $t('intranet.actas.acabando') : $t('intranet.actas.grabando') }}</strong>
        <span class="tiempo">{{ tiempo }}</span>
        <span class="nivel" aria-hidden="true"><i :style="{ width: Math.round(nivel * 100) + '%' }"></i></span>
      </div>
      <p class="recordatorio">🗣️ {{ $t('intranet.actas.recordatorioPresentarse') }}</p>
      <p class="nota">
        {{ $t('intranet.actas.dejarAbierta') }}
        <span v-if="pendientes > 1"> · {{ $t('intranet.actas.trozosPendientes', { n: pendientes }) }}</span>
        <span v-if="sinConexion" class="aviso-red"> · ⚠️ {{ $t('intranet.actas.sinConexion') }}</span>
      </p>
      <div class="botones">
        <button v-if="estado === 'grabando'" type="button" class="btn-mini" @click="pausar">⏸️ {{ $t('intranet.actas.pausar') }}</button>
        <button v-if="estado === 'pausa'" type="button" class="btn-mini" @click="continuar">▶️ {{ $t('intranet.actas.continuar') }}</button>
        <button type="button" class="btn-parar" :disabled="estado === 'acabando'" @click="parar">⏹️ {{ $t('intranet.actas.parar') }}</button>
      </div>
    </div>

    <p v-if="archivo" class="nota" role="status">⬆️ {{ $t('intranet.actas.subiendo', { nombre: archivo.nombre, pct: archivo.pct }) }}
      <span v-if="sinConexion" class="aviso-red"> · ⚠️ {{ $t('intranet.actas.sinConexion') }}</span></p>

    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="copiaLocal" class="copia">
      {{ $t('intranet.actas.copiaLocal') }}
      <a :href="copiaLocal.url" :download="copiaLocal.nombre">💾 {{ $t('intranet.actas.descargarCopia') }}</a>
    </p>

    <!-- Avís abans de gravar -->
    <div v-if="estado === 'aviso'" class="velo" @click.self="estado = ''">
      <div class="ventana" role="dialog" aria-modal="true" :aria-label="$t('intranet.actas.antesDeGrabar')">
        <header>
          <h3>🎙️ {{ $t('intranet.actas.antesDeGrabar') }}</h3>
          <button type="button" class="cerrar" :aria-label="$t('intranet.comun.cerrar')" @click="estado = ''">✕</button>
        </header>
        <ol class="pasos">
          <li><strong>{{ $t('intranet.actas.paso1Titulo') }}</strong> {{ $t('intranet.actas.paso1') }}</li>
          <li><strong>{{ $t('intranet.actas.paso2Titulo') }}</strong> {{ $t('intranet.actas.paso2') }}
            <em class="ejemplo">{{ $t('intranet.actas.paso2Ejemplo') }}</em></li>
          <li><strong>{{ $t('intranet.actas.paso3Titulo') }}</strong> {{ $t('intranet.actas.paso3') }}</li>
        </ol>
        <label class="confirmar"><input v-model="avisados" type="checkbox"> {{ $t('intranet.actas.confirmoAvisados') }}</label>
        <footer>
          <button type="button" class="btn-grabar" :disabled="!avisados" @click="empezar">🔴 {{ $t('intranet.actas.empezar') }}</button>
          <button type="button" class="btn-mini" @click="estado = ''">{{ $t('intranet.comun.cancelar') }}</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grabadora { margin-top: 6px; }
.botones { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.btn-grabar { background: #c62828; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 1rem; }
.btn-grabar:disabled { background: #c9a9a9; cursor: not-allowed; }
.btn-subir { background: white; color: #012169; border: 1px solid #b9c6d6; padding: 9px 14px; border-radius: 6px; cursor: pointer; font-size: 0.92rem; }
.btn-subir input { display: none; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 6px 12px; cursor: pointer; font-size: 0.88rem; }
.btn-parar { background: #012169; color: white; border: none; padding: 7px 14px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-parar:disabled { opacity: 0.6; cursor: wait; }
.nota { color: #666; font-size: 0.83rem; margin: 6px 0; }
.error { color: #b02a37; font-weight: bold; }
.aviso-red { color: #b0731c; font-weight: bold; }
.copia { background: #fff4e5; border: 1px solid #f0c37a; border-radius: 6px; padding: 8px 12px; font-size: 0.9rem; }

.en-curso { border: 2px solid #c62828; background: #fff5f5; border-radius: 8px; padding: 12px 14px; }
.en-curso.pausa { border-color: #b0731c; background: #fffaf0; }
.linea { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; color: #8a1c1c; }
.en-curso.pausa .linea { color: #7a4300; }
.punto { width: 12px; height: 12px; border-radius: 50%; background: #c62828; animation: latido 1.2s infinite; }
.en-curso.pausa .punto { background: #b0731c; animation: none; }
@keyframes latido { 50% { opacity: 0.25; } }
.tiempo { font-family: monospace; font-size: 1.4rem; font-weight: bold; }
.nivel { flex: 1; min-width: 80px; max-width: 220px; height: 8px; background: #f1d6d6; border-radius: 4px; overflow: hidden; }
.nivel i { display: block; height: 100%; background: #2e9d57; transition: width 0.1s; }
.recordatorio { margin: 8px 0 2px; font-size: 0.9rem; color: #333; }

.velo { position: fixed; inset: 0; background: rgba(1, 20, 60, 0.45); display: flex; align-items: center; justify-content: center; padding: 16px; z-index: 10000; }
.ventana { background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.25); width: min(560px, 100%); max-height: 88vh; overflow-y: auto; padding: 18px 20px; border-top: 4px solid #c62828; }
.ventana header { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
.ventana h3 { margin: 0 0 8px; color: #012169; }
.cerrar { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #555; }
.pasos { padding-left: 20px; margin: 6px 0 12px; line-height: 1.45; }
.pasos li { margin-bottom: 8px; }
.ejemplo { display: block; color: #1d5f8c; margin-top: 2px; }
.confirmar { display: flex; gap: 8px; align-items: flex-start; background: #f0f4f8; border-radius: 6px; padding: 10px 12px; font-weight: bold; color: #012169; cursor: pointer; }
.confirmar input { margin-top: 3px; width: 18px; height: 18px; }
.ventana footer { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
</style>
