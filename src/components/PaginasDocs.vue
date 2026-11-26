<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import EditorRico from './EditorRico.vue'
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'
import { limpiarHtml } from '../utils/limpiarHtml'
import { exportarPagina, FORMATOS, normalizarHtml } from '../utils/exportarPagina'

// Pàgines de documentació escrites a la intranet (una wiki interna): llista, lectura,
// edició amb historial (qui i quan) i recuperació de versions anteriors.
// Només per al personal amb sessió. No s'hi poden escriure contrasenyes.
const emit = defineEmits(['sesion-caducada'])
// inicial: { doc, carpeta } per obrir directament una pàgina o una carpeta (enllaços de la cerca)
const props = defineProps({ inicial: { type: Object, default: () => ({}) } })
const { t, locale } = useI18n()
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })

const vista = ref('lista') // 'lista' | 'ver' | 'editar' | 'version'
const paginas = ref([])
const pagina = ref(null)   // pàgina oberta (amb versions)
const version = ref(null)  // versió antiga que s'està mirant
const borrador = ref(null) // { id, titulo, categoria, contenido }
const buscador = ref('')
const error = ref('')
const mensaje = ref('')
const guardando = ref(false)

// El mateix control que fa el servidor, per avisar abans de desar
const PATRON_CONTRASENA = /\b(password|passwd|pwd|pass|passphrase|contrase(?:ñ|n)a|contrasenya|clau|clave|secret|token)\b\s*[:=]\s*(\S+)/gi
const PATRON_MARCADOR = /^([([<*…\-–—]|x+$|\*+$|\.+$|n\/?a$)/i
const textoPlano = (html) => (html || '').replace(/<(br|\/p|\/li|\/h[1-6]|\/pre|\/div|\/tr)[^>]*>/gi, '\n').replace(/<[^>]+>/g, ' ')
  .replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
const contrasenaEscrita = (html) => {
  for (const m of textoPlano(html).matchAll(PATRON_CONTRASENA)) if (!PATRON_MARCADOR.test(m[2])) return m[0].slice(0, 60)
  return null
}

const fecha = (iso) => iso ? new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  .format(new Date(iso.replace(' ', 'T') + 'Z')) : ''

const fallo = async (r) => {
  const d = await r.json().catch(() => ({}))
  error.value = traducirError(d.error) || t('intranet.comun.errorDesconocido')
}

const cargarLista = async () => {
  const r = await api('/api/paginas')
  if (r.ok) paginas.value = await r.json()
  else error.value = t('intranet.paginas.errorCarga')
}
onMounted(async () => {
  await cargarLista()
  cargarCarpetas()
  if (props.inicial?.carpeta) carpeta.value = props.inicial.carpeta
  if (props.inicial?.doc) abrir(props.inicial.doc)
})

// ---------- Introducció de cada carpeta ----------
const introducciones = ref({})
const cargarCarpetas = async () => {
  const r = await api('/api/paginas/carpetas')
  if (r.ok) introducciones.value = await r.json()
}
const introCarpeta = computed(() => introducciones.value[carpeta.value]?.introduccion || '')
const editandoIntro = ref(false)
const borradorIntro = ref('')
const editarIntro = () => { borradorIntro.value = introCarpeta.value; editandoIntro.value = true }
const guardarIntro = async () => {
  const sospecha = contrasenaEscrita(borradorIntro.value)
  if (sospecha) { error.value = t('intranet.paginas.hayContrasena', { fragmento: sospecha }); return }
  const r = await api('/api/paginas/carpetas', json('PUT', { nombre: carpeta.value, introduccion: borradorIntro.value }))
  if (!r.ok) return fallo(r)
  editandoIntro.value = false
  await cargarCarpetas()
}

// ---------- Cerca també dins dels PDF ----------
const enPdf = ref([])
let temporizadorPdf = null
const buscarEnPdf = () => {
  clearTimeout(temporizadorPdf)
  const q = buscador.value.trim()
  if (q.length < 2) { enPdf.value = []; return }
  temporizadorPdf = setTimeout(async () => {
    const r = await api(`/api/buscar?q=${encodeURIComponent(q)}&idioma=${locale.value}`)
    if (r.ok && buscador.value.trim() === q) enPdf.value = (await r.json()).filter(x => x.tipo === 'adjunto')
  }, 350)
}

const normalizar = (s) => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
const agrupadas = computed(() => {
  const q = normalizar(buscador.value.trim())
  const grupos = {}
  for (const p of paginas.value) {
    if (q && !normalizar([p.titulo, p.categoria, p.texto].join(' ')).includes(q)) continue
    const g = p.categoria || t('intranet.paginas.sinCategoria')
    ;(grupos[g] ||= []).push(p)
  }
  return Object.entries(grupos).sort(([a], [b]) => a.localeCompare(b))
})
const categorias = computed(() => [...new Set(paginas.value.map(p => p.categoria).filter(Boolean))].sort())

// Navegació com un gestor de fitxers: carpetes (categories) i, a dins, les pàgines
const carpeta = ref(null) // null = inici de la documentació
const SIN_CATEGORIA = () => t('intranet.paginas.sinCategoria')
const carpetas = computed(() => {
  const n = {}
  for (const p of paginas.value) { const g = p.categoria || SIN_CATEGORIA(); n[g] = (n[g] || 0) + 1 }
  return Object.entries(n).sort(([a], [b]) => a.localeCompare(b))
})
const buscando = computed(() => buscador.value.trim().length > 0)
// Pàgines que es mostren: les de la carpeta oberta o, si es cerca, totes les que coincideixen
const visibles = computed(() => {
  if (buscando.value) return agrupadas.value.flatMap(([, l]) => l)
  return paginas.value.filter(p => (p.categoria || SIN_CATEGORIA()) === carpeta.value)
    .sort((a, b) => a.titulo.localeCompare(b.titulo))
})
// Tipus de la fitxa: el del primer adjunt o «WEB» si només és text escrit aquí
const tipoFicha = (p) => p.adjuntos?.length ? (p.adjuntos[0] || '').toUpperCase() : 'WEB'
const COLOR_TIPO = { PDF: '#d93025', DOC: '#1a5fb4', DOCX: '#1a5fb4', XLS: '#1e7e34', XLSX: '#1e7e34', CSV: '#1e7e34', PPT: '#d35400', PPTX: '#d35400', JPG: '#8e44ad', JPEG: '#8e44ad', PNG: '#8e44ad', ZIP: '#6c757d', TXT: '#6c757d', WEB: '#17a2b8' }
const colorTipo = (p) => COLOR_TIPO[tipoFicha(p)] || '#6c757d'
const fechaCorta = (iso) => iso ? new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(iso.replace(' ', 'T') + 'Z')) : ''

const abrir = async (id) => {
  error.value = ''; mensaje.value = ''
  const r = await api(`/api/paginas/${id}`)
  if (!r.ok) return fallo(r)
  pagina.value = await r.json()
  vista.value = 'ver'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
// Enllaços interns d'una pàgina (#apartat, p. ex. un índex): baixar fins a l'apartat
const seguirEnlace = (e) => {
  const a = e.target.closest?.('a[href^="#"]')
  if (!a) return
  const destino = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)))
  if (!destino) return
  e.preventDefault()
  destino.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
const volver = async () => { vista.value = 'lista'; pagina.value = null; version.value = null; await cargarLista() }

const nueva = () => {
  error.value = ''; mensaje.value = ''
  borrador.value = { id: null, titulo: '', categoria: carpeta.value && carpeta.value !== SIN_CATEGORIA() ? carpeta.value : '', contenido: '' }
  vista.value = 'editar'
}
const editar = () => {
  error.value = ''; mensaje.value = ''
  // Les pàgines fetes amb l'editor antic (Quill) es passen a HTML estàndard per a l'editor nou
  borrador.value = { id: pagina.value.id, titulo: pagina.value.titulo, categoria: pagina.value.categoria, contenido: normalizarHtml(pagina.value.contenido) }
  vista.value = 'editar'
}
const cancelar = () => { vista.value = borrador.value.id ? 'ver' : 'lista' }

const guardar = async () => {
  error.value = ''
  const sospecha = contrasenaEscrita(borrador.value.titulo + '\n' + borrador.value.contenido)
  if (sospecha) { error.value = t('intranet.paginas.hayContrasena', { fragmento: sospecha }); return }
  guardando.value = true
  try {
    const b = borrador.value
    const r = await api(b.id ? `/api/paginas/${b.id}` : '/api/paginas', json(b.id ? 'PUT' : 'POST', b))
    if (!r.ok) return fallo(r)
    const d = await r.json()
    await abrir(d.id)
    mensaje.value = t('intranet.paginas.guardada')
  } finally {
    guardando.value = false
  }
}

// ---------- ADJUNTS ----------
const MAX_MB = 40
const ICONOS = { PDF: '📕', DOC: '📘', DOCX: '📘', XLS: '📗', XLSX: '📗', CSV: '📗', PPT: '📙', PPTX: '📙', JPG: '🖼️', JPEG: '🖼️', PNG: '🖼️', ZIP: '🗜️', TXT: '📄' }
const icono = (formato) => ICONOS[(formato || '').toUpperCase()] || '📎'
const tamano = (b) => !b ? '' : b > 1048576 ? `${(b / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(b / 1024))} kB`
const subiendo = ref(false)
const inputArchivo = ref(null)
const verVisor = ref(true)
const pdfVisor = computed(() => (pagina.value?.adjuntos || []).find(a => (a.formato || '').toUpperCase() === 'PDF'))
const subirAdjunto = async (e) => {
  const fichero = e.target.files[0]
  e.target.value = ''
  if (!fichero) return
  if (fichero.size > MAX_MB * 1048576) { error.value = t('intranet.paginas.adjuntoGrande', { max: MAX_MB }); return }
  error.value = ''; subiendo.value = true
  try {
    const datos = new FormData()
    datos.append('archivo', fichero)
    const r = await api(`/api/paginas/${pagina.value.id}/adjuntos`, { method: 'POST', body: datos })
    if (!r.ok) return fallo(r)
    await abrir(pagina.value.id)
    mensaje.value = t('intranet.paginas.adjuntoSubido')
  } finally {
    subiendo.value = false
  }
}
const quitarAdjunto = async (a) => {
  if (!confirm(t('intranet.paginas.confirmarQuitar', { nombre: a.nombre }))) return
  const r = await api(`/api/paginas/${pagina.value.id}/adjuntos/${a.id}`, { method: 'DELETE' })
  if (!r.ok) return fallo(r)
  await abrir(pagina.value.id)
}

// ---------- DESCARREGAR LA PÀGINA ----------
const formatoDescarga = ref('pdf')
const exportando = ref(false)
const descargar = async (formato) => {
  exportando.value = true; error.value = ''
  try {
    const p = pagina.value
    await exportarPagina(p, formato, {
      adjuntos: t('intranet.paginas.adjuntos', { n: p.adjuntos.length }),
      meta: [p.categoria, t('intranet.paginas.actualizadaPor', { quien: p.actualizado_por, fecha: fecha(p.actualizado) })].filter(Boolean).join(' · ')
    })
  } catch (e) {
    console.error(e)
    error.value = t('intranet.paginas.errorExportar')
  } finally {
    exportando.value = false
  }
}

const borrar = async () => {
  if (!confirm(t('intranet.paginas.confirmarBorrar', { titulo: pagina.value.titulo }))) return
  const r = await api(`/api/paginas/${pagina.value.id}`, { method: 'DELETE' })
  if (!r.ok) return fallo(r)
  mensaje.value = t('intranet.comun.borrado')
  await volver()
}

const verVersion = async (v) => {
  const r = await api(`/api/paginas/${pagina.value.id}/versiones/${v.id}`)
  if (!r.ok) return fallo(r)
  version.value = await r.json()
  vista.value = 'version'
}
const restaurar = async () => {
  if (!confirm(t('intranet.paginas.confirmarRestaurar', { fecha: fecha(version.value.fecha) }))) return
  const r = await api(`/api/paginas/${pagina.value.id}`, json('PUT', { titulo: version.value.titulo, categoria: version.value.categoria, contenido: version.value.contenido }))
  if (!r.ok) return fallo(r)
  await abrir(pagina.value.id)
  mensaje.value = t('intranet.paginas.restaurada')
}
</script>

<template>
  <div class="panel-paginas">
    <p v-if="mensaje" class="aviso-ok" role="status">{{ mensaje }}</p>
    <p v-if="error" class="aviso-error" role="alert">{{ error }}</p>

    <!-- LLISTA: carpetes i fitxes, com un gestor de fitxers -->
    <template v-if="vista === 'lista'">
      <div class="cabecera">
        <div>
          <h2>{{ $t('intranet.paginas.titulo') }}</h2>
          <p class="subtitulo">{{ $t('intranet.paginas.subtitulo') }}</p>
        </div>
        <div class="acciones">
          <input v-model="buscador" type="search" class="buscador" :placeholder="$t('intranet.paginas.buscar')" @input="buscarEnPdf">
          <button type="button" class="btn-principal" @click="nueva">{{ $t('intranet.paginas.nueva') }}</button>
        </div>
      </div>

      <!-- Ruta: Documentació › carpeta -->
      <nav class="ruta" :aria-label="$t('intranet.paginas.ruta')">
        <button type="button" :class="{ actual: !carpeta && !buscando }" @click="carpeta = null; buscador = ''">📚 {{ $t('intranet.paginas.inicio') }}</button>
        <template v-if="buscando"><span aria-hidden="true">›</span><span class="actual">🔍 {{ $t('intranet.paginas.resultados', { n: visibles.length }) }}</span></template>
        <template v-else-if="carpeta"><span aria-hidden="true">›</span><span class="actual">📂 {{ carpeta }}</span></template>
      </nav>

      <p v-if="!paginas.length" class="vacio">{{ $t('intranet.paginas.ninguna') }}</p>

      <!-- Inici: carpetes -->
      <ul v-else-if="!carpeta && !buscando" class="graella carpetas">
        <li v-for="[nombre, n] in carpetas" :key="nombre">
          <button type="button" class="carpeta" @click="carpeta = nombre">
            <span class="icono-carpeta" aria-hidden="true"></span>
            <span class="nombre">{{ nombre }}</span>
            <span class="detalle">{{ $t('intranet.paginas.elementos', { n }) }}</span>
          </button>
        </li>
      </ul>

      <!-- Dins d'una carpeta o resultats de la cerca: fitxes -->
      <template v-else>
        <!-- Introducció de la carpeta -->
        <section v-if="carpeta && !buscando" class="intro-carpeta">
          <template v-if="!editandoIntro">
            <div v-if="introCarpeta" class="intro-texto contenido-wiki" v-html="limpiarHtml(introCarpeta)"></div>
            <p v-else class="vacio">{{ $t('intranet.paginas.sinIntro') }}</p>
            <button type="button" class="btn-mini" @click="editarIntro">✏️ {{ introCarpeta ? $t('intranet.paginas.editarIntro') : $t('intranet.paginas.anadirIntro') }}</button>
          </template>
          <template v-else>
            <EditorRico v-model="borradorIntro" :placeholder="$t('intranet.paginas.introPh')" />
            <div class="botones-intro">
              <button type="button" class="btn-principal" @click="guardarIntro">{{ $t('intranet.comun.guardar') }}</button>
              <button type="button" class="btn-mini" @click="editandoIntro = false">{{ $t('intranet.comun.cancelar') }}</button>
            </div>
          </template>
        </section>
        <p v-if="!visibles.length && !enPdf.length" class="vacio">{{ $t('intranet.paginas.sinResultados') }}</p>
        <ul class="graella fichas">
          <li v-for="p in visibles" :key="p.id">
            <button type="button" class="ficha" @click="abrir(p.id)" :title="p.titulo">
              <span class="hoja" :style="{ '--tipo': colorTipo(p) }">
                <span class="etiqueta-tipo">{{ tipoFicha(p) }}</span>
                <span v-if="p.adjuntos?.length > 1" class="clip">📎 {{ p.adjuntos.length }}</span>
              </span>
              <span class="nombre">{{ p.titulo }}</span>
              <span class="detalle"><template v-if="buscando">📂 {{ p.categoria || SIN_CATEGORIA() }} · </template>{{ fechaCorta(p.actualizado) }}</span>
            </button>
            <a v-if="p.adjunto" class="obrir-adjunt" :href="p.adjunto.href" target="_blank" rel="noopener" :title="p.adjunto.nombre">📎 {{ $t('intranet.paginas.obrirAdjunt') }}</a>
          </li>
        </ul>
        <!-- Resultats de dins dels PDF -->
        <section v-if="buscando && enPdf.length" class="en-pdf">
          <h3>📄 {{ $t('intranet.paginas.dinsPdf', { n: enPdf.length }) }}</h3>
          <ul>
            <li v-for="r in enPdf" :key="r.id">
              <a :href="r.enlace" target="_blank" rel="noopener"><strong>{{ r.pagina }}</strong></a>
              <span class="detalle">📂 {{ r.carpeta }} · {{ r.titulo }} · {{ $t('intranet.paginas.paginaPdf', { n: r.pagina_pdf }) }}</span>
              <p>{{ r.extracto }}</p>
            </li>
          </ul>
        </section>
      </template>
    </template>

    <!-- LECTURA -->
    <template v-else-if="vista === 'ver' && pagina">
      <button type="button" class="btn-volver" @click="volver">← {{ $t('intranet.paginas.volver') }}</button>
      <article class="pagina">
        <p v-if="pagina.categoria" class="categoria">📂 {{ pagina.categoria }}</p>
        <h1>{{ pagina.titulo }}</h1>
        <p class="meta">
          {{ $t('intranet.paginas.creadaPor', { quien: pagina.creado_por, fecha: fecha(pagina.creado) }) }}
          <template v-if="pagina.versiones.length > 1"> · {{ $t('intranet.paginas.actualizadaPor', { quien: pagina.actualizado_por, fecha: fecha(pagina.actualizado) }) }}</template>
        </p>
        <div class="botones">
          <button type="button" class="btn-principal" @click="editar">✏️ {{ $t('intranet.paginas.editar') }}</button>
          <button v-if="pagina.puede_borrar" type="button" class="btn-peligro" @click="borrar">🗑️ {{ $t('intranet.comun.borrar') }}</button>
          <span class="descarga">
            <button type="button" class="btn-descarga" :disabled="exportando" @click="descargar(formatoDescarga)">⬇ {{ $t('intranet.paginas.descargar') }}</button>
            <select v-model="formatoDescarga" :aria-label="$t('intranet.paginas.formato')">
              <option v-for="f in FORMATOS" :key="f" :value="f">{{ $t(`intranet.paginas.formatos.${f}`) }}</option>
            </select>
          </span>
        </div>
        <div v-if="textoPlano(pagina.contenido).trim() || /<img/i.test(pagina.contenido || '')" class="contenido-wiki" v-html="limpiarHtml(pagina.contenido)" @click="seguirEnlace"></div>

        <!-- Fitxers adjunts -->
        <section class="adjuntos">
          <div class="adjuntos-cabecera">
            <h2>📎 {{ $t('intranet.paginas.adjuntos', { n: pagina.adjuntos.length }) }}</h2>
            <button type="button" class="btn-secundario" :disabled="subiendo" @click="inputArchivo.click()">
              {{ $t(subiendo ? 'intranet.paginas.subiendo' : 'intranet.paginas.adjuntar') }}
            </button>
            <input ref="inputArchivo" type="file" hidden @change="subirAdjunto">
          </div>
          <ul v-if="pagina.adjuntos.length" class="lista-adjuntos">
            <li v-for="a in pagina.adjuntos" :key="a.id">
              <span class="icono-adjunto" aria-hidden="true">{{ icono(a.formato) }}</span>
              <a :href="a.href" target="_blank" rel="noopener">{{ a.nombre }}</a>
              <span class="gris">{{ a.formato }}<template v-if="a.tamano"> · {{ tamano(a.tamano) }}</template></span>
              <button v-if="a.puede_borrar" type="button" class="btn-mini peligro" @click="quitarAdjunto(a)" :aria-label="$t('intranet.paginas.quitar')">✕</button>
            </li>
          </ul>
          <template v-if="pdfVisor">
            <button type="button" class="btn-volver" @click="verVisor = !verVisor">{{ $t(verVisor ? 'intranet.paginas.ocultarVisor' : 'intranet.paginas.mostrarVisor') }}</button>
            <iframe v-if="verVisor" :src="pdfVisor.href" class="visor-pdf" :title="pdfVisor.nombre"></iframe>
          </template>
        </section>
      </article>
      <details class="historial">
        <summary>🕘 {{ $t('intranet.paginas.historial', { n: pagina.versiones.length }) }}</summary>
        <ol>
          <li v-for="(v, i) in pagina.versiones" :key="v.id">
            <span>{{ fecha(v.fecha) }} · {{ v.editado_por }}</span>
            <span v-if="i === 0" class="actual">{{ $t('intranet.paginas.actual') }}</span>
            <button v-else type="button" class="btn-mini" @click="verVersion(v)">{{ $t('intranet.paginas.verVersion') }}</button>
          </li>
        </ol>
      </details>
    </template>

    <!-- VERSIÓ ANTIGA -->
    <template v-else-if="vista === 'version' && version">
      <button type="button" class="btn-volver" @click="vista = 'ver'">← {{ $t('intranet.paginas.volverActual') }}</button>
      <p class="aviso-version">🕘 {{ $t('intranet.paginas.mirandoVersion', { fecha: fecha(version.fecha), quien: version.editado_por }) }}
        <button type="button" class="btn-principal" @click="restaurar">{{ $t('intranet.paginas.restaurar') }}</button></p>
      <article class="pagina antigua">
        <h1>{{ version.titulo }}</h1>
        <div class="contenido-wiki" v-html="limpiarHtml(version.contenido)"></div>
      </article>
    </template>

    <!-- EDICIÓ -->
    <template v-else-if="vista === 'editar' && borrador">
      <h2>{{ $t(borrador.id ? 'intranet.paginas.editando' : 'intranet.paginas.nuevaTitulo') }}</h2>
      <p class="aviso-seguridad">🔒 {{ $t('intranet.paginas.avisoContrasenas') }}</p>
      <form class="formulario" @submit.prevent="guardar">
        <div class="fila">
          <label class="ancho">{{ $t('intranet.paginas.tituloCampo') }}
            <input v-model="borrador.titulo" maxlength="200" required :placeholder="$t('intranet.paginas.tituloPh')">
          </label>
          <label>{{ $t('intranet.paginas.categoria') }}
            <input v-model="borrador.categoria" maxlength="100" list="categorias-paginas" :placeholder="$t('intranet.paginas.categoriaPh')">
          </label>
          <datalist id="categorias-paginas"><option v-for="c in categorias" :key="c" :value="c"></option></datalist>
        </div>
        <div class="editor">
          <EditorRico v-model="borrador.contenido" :placeholder="$t('intranet.editor.placeholder')" />
        </div>
        <div class="botones">
          <button type="submit" class="btn-principal" :disabled="guardando">{{ $t('intranet.comun.guardar') }}</button>
          <button type="button" class="btn-secundario" @click="cancelar">{{ $t('intranet.comun.cancelar') }}</button>
        </div>
      </form>
    </template>
  </div>
</template>

<style scoped>
.panel-paginas { background: white; border-radius: 10px; padding: 28px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #17a2b8; }
.cabecera { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; border-bottom: 2px solid #eee; padding-bottom: 18px; margin-bottom: 18px; }
.cabecera h2, .panel-paginas > h2 { color: #012169; margin: 0 0 5px; font-size: 1.5rem; }
.subtitulo { color: #666; margin: 0; font-size: 0.93rem; max-width: 620px; }
.acciones { display: flex; gap: 10px; flex-wrap: wrap; }
.buscador { padding: 9px 14px; border: 1px solid #ccc; border-radius: 6px; width: 260px; font: inherit; font-size: 0.93rem; }
.btn-principal { background: #17a2b8; color: white; border: none; padding: 9px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; font: inherit; font-weight: bold; }
.btn-principal:hover { background: #117a8b; }
.btn-principal:disabled { opacity: 0.6; cursor: wait; }
.btn-secundario { background: #f4f7f9; border: 1px solid #ccd5df; padding: 9px 18px; border-radius: 6px; cursor: pointer; font: inherit; }
.btn-peligro { background: white; color: #b02a37; border: 1px solid #e3b5ba; padding: 9px 16px; border-radius: 6px; cursor: pointer; font: inherit; }
/* Introducció de la carpeta i enllaç directe a l'adjunt */
.intro-carpeta { background: #f4f9fb; border-left: 4px solid #17a2b8; border-radius: 6px; padding: 12px 16px; margin: 0 0 16px; }
.intro-texto { border-top: none; padding-top: 0; margin-bottom: 8px; }
.botones-intro { display: flex; gap: 8px; margin-top: 8px; }
.obrir-adjunt { display: block; text-align: center; font-size: 0.78rem; color: #0060a0; text-decoration: none; margin-top: 4px; }
.obrir-adjunt:hover { text-decoration: underline; }
.en-pdf { margin-top: 20px; border-top: 1px solid #e3e8ee; padding-top: 10px; }
.en-pdf h3 { color: #012169; font-size: 1rem; margin: 0 0 6px; }
.en-pdf ul { list-style: none; padding: 0; margin: 0; }
.en-pdf li { padding: 8px 0; border-bottom: 1px solid #f0f2f4; }
.en-pdf a { color: #0060a0; text-decoration: none; }
.en-pdf .detalle { display: block; color: #777; font-size: 0.8rem; }
.en-pdf p { margin: 3px 0 0; font-size: 0.88rem; color: #333; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 3px 10px; cursor: pointer; font-size: 0.8rem; }
.btn-volver { background: none; border: none; color: #0086c0; font-weight: bold; cursor: pointer; padding: 0; margin-bottom: 14px; font: inherit; font-weight: bold; }
.aviso-ok { color: #198754; font-weight: bold; }
.aviso-error { color: #b02a37; font-weight: bold; background: #fdecea; padding: 10px 14px; border-radius: 6px; }
.vacio { color: #666; font-style: italic; }

.ruta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 0 0 16px; font-size: 0.95rem; color: #777; }
.ruta button { background: none; border: none; padding: 4px 6px; border-radius: 4px; color: #0086c0; font: inherit; font-weight: bold; cursor: pointer; }
.ruta button:hover { background: #eef5fa; }
.ruta .actual { color: #012169; font-weight: bold; }
.ruta button.actual { color: #012169; cursor: default; }
.graella { list-style: none; padding: 0; margin: 0; display: grid; gap: 14px; }
.carpetas { grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); }
.fichas { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
.carpeta, .ficha { width: 100%; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 10px 12px; background: white; border: 1px solid transparent;
  border-radius: 10px; cursor: pointer; font: inherit; text-align: center; transition: background 0.15s, border-color 0.15s, transform 0.15s; }
.carpeta:hover, .ficha:hover { background: #f2f8fc; border-color: #cfe3f0; transform: translateY(-2px); }
.carpeta:focus-visible, .ficha:focus-visible { outline: 2px solid #0086c0; outline-offset: 2px; }
/* Carpeta dibuixada amb CSS (pestanya + cos) */
.icono-carpeta { position: relative; width: 96px; height: 72px; margin-top: 8px; border-radius: 6px 8px 8px 8px; background: linear-gradient(180deg, #4a90d9, #2f6fb8); box-shadow: 0 4px 10px rgba(47, 111, 184, 0.25); }
.icono-carpeta::before { content: ''; position: absolute; left: 0; top: -10px; width: 40px; height: 14px; border-radius: 6px 6px 0 0; background: #2f6fb8; }
.icono-carpeta::after { content: ''; position: absolute; left: 6px; right: 6px; top: 10px; height: 4px; border-radius: 2px; background: rgba(255, 255, 255, 0.35); }
/* Full amb la cantonada doblegada i el tipus de fitxer */
.hoja { position: relative; width: 74px; height: 96px; border-radius: 4px; background: white; border: 1px solid #d5dbe2; box-shadow: 0 3px 8px rgba(0,0,0,0.08);
  display: flex; align-items: flex-end; justify-content: center; padding-bottom: 12px; box-sizing: border-box; }
.hoja::before { content: ''; position: absolute; top: -1px; right: -1px; width: 20px; height: 20px; background: linear-gradient(225deg, #f4f7f9 50%, #d5dbe2 50%); border-bottom-left-radius: 3px; }
.hoja::after { content: ''; position: absolute; left: 12px; right: 12px; top: 26px; height: 30px; background: repeating-linear-gradient(#e8ecf0 0 3px, transparent 3px 8px); }
.etiqueta-tipo { position: relative; z-index: 1; background: var(--tipo); color: white; font-size: 0.7rem; font-weight: bold; letter-spacing: 0.5px; padding: 2px 7px; border-radius: 3px; }
.clip { position: absolute; top: -8px; left: -10px; background: white; border: 1px solid #d5dbe2; border-radius: 10px; padding: 0 6px; font-size: 0.72rem; color: #555; }
.carpeta .nombre, .ficha .nombre { color: #012169; font-weight: bold; font-size: 0.88rem; line-height: 1.25; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow-wrap: anywhere; }
.carpeta .detalle, .ficha .detalle { color: #888; font-size: 0.76rem; }
.grupo h3 { color: #012169; font-size: 1.05rem; margin: 18px 0 8px; }
.lista { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; }
.item { width: 100%; text-align: left; display: flex; flex-direction: column; gap: 4px; padding: 12px 14px; background: #f8fafc; border: 1px solid #e3e8ee; border-left: 4px solid #17a2b8; border-radius: 6px; cursor: pointer; font: inherit; }
.item:hover { background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.item-titulo { color: #012169; font-weight: bold; }
.item-meta { color: #777; font-size: 0.8rem; }

.pagina { max-width: 1000px; }
.pagina h1 { color: #012169; font-size: 1.8rem; margin: 4px 0 6px; }
.categoria { color: #17a2b8; font-weight: bold; margin: 0; font-size: 0.9rem; }
.meta { color: #777; font-size: 0.85rem; margin: 0 0 12px; }
.botones { display: flex; gap: 10px; flex-wrap: wrap; margin: 6px 0 18px; }
.contenido-wiki { color: #333; line-height: 1.65; font-size: 0.98rem; border-top: 1px solid #eee; padding-top: 16px; overflow-wrap: anywhere; }
.contenido-wiki :deep(h2) { color: #012169; font-size: 1.35rem; margin: 22px 0 8px; }
.contenido-wiki :deep(h3) { color: #012169; font-size: 1.12rem; margin: 18px 0 6px; }
.contenido-wiki :deep(p) { margin: 0 0 10px; }
.contenido-wiki :deep(ul), .contenido-wiki :deep(ol) { margin: 0 0 12px 22px; }
.contenido-wiki :deep(blockquote) { margin: 0 0 12px; padding: 8px 14px; border-left: 4px solid #8cc63f; background: #f6faf0; }
.contenido-wiki :deep(pre) { background: #0f1b2d; color: #e6edf3; padding: 12px 14px; border-radius: 6px; overflow-x: auto; font-size: 0.88rem; line-height: 1.5; white-space: pre; }
/* Format de l'editor (Quill 2): llistes de punts dins d'<ol>, marcadors interns i blocs de codi */
.contenido-wiki :deep(li[data-list="bullet"]) { list-style-type: disc; }
.contenido-wiki :deep(li[data-list="ordered"]) { list-style-type: decimal; }
.contenido-wiki :deep(.ql-ui) { display: none; }
.contenido-wiki :deep(.ql-code-block-container) { background: #0f1b2d; color: #e6edf3; padding: 12px 14px; border-radius: 6px; overflow-x: auto; margin: 0 0 12px;
  font-family: 'Courier New', monospace; font-size: 0.88rem; line-height: 1.5; white-space: pre; }
.contenido-wiki :deep(h1) { color: #012169; font-size: 1.6rem; margin: 24px 0 10px; }
.contenido-wiki :deep(h4) { color: #012169; font-size: 1rem; margin: 14px 0 4px; }
.contenido-wiki :deep(hr) { border: none; border-top: 2px solid #d5dbe2; margin: 18px 0; }
.contenido-wiki :deep(mark) { padding: 0 2px; border-radius: 2px; }
.contenido-wiki :deep(th) { background: #eef3f8; text-align: left; }
.contenido-wiki :deep(table) { width: 100%; }
.contenido-wiki :deep(ul[data-type="taskList"]) { list-style: none; padding-left: 4px; margin-left: 0; }
.contenido-wiki :deep(ul[data-type="taskList"] li) { display: flex; gap: 8px; align-items: flex-start; }
.contenido-wiki :deep(ul[data-type="taskList"] li > label) { margin-top: 3px; pointer-events: none; }
.contenido-wiki :deep(ul[data-type="taskList"] li > div) { flex: 1; }
.contenido-wiki :deep(ul[data-type="taskList"] li[data-checked="true"] > div) { color: #6b7785; text-decoration: line-through; }
.contenido-wiki :deep(code) { font-family: 'Courier New', monospace; }
.contenido-wiki :deep(img) { max-width: 100%; height: auto; border-radius: 6px; margin: 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.12); }
.contenido-wiki :deep(a) { color: #0086c0; }
.contenido-wiki :deep(table) { border-collapse: collapse; margin: 0 0 12px; }
.contenido-wiki :deep(td), .contenido-wiki :deep(th) { border: 1px solid #ddd; padding: 6px 10px; }

.item-adjuntos { color: #17a2b8; font-size: 0.78rem; font-weight: bold; }
.descarga { display: inline-flex; margin-left: auto; }
.btn-descarga { background: #012169; color: white; border: none; padding: 9px 16px; border-radius: 6px 0 0 6px; font: inherit; font-weight: bold; cursor: pointer; }
.btn-descarga:hover { background: #0086c0; }
.btn-descarga:disabled { opacity: 0.6; cursor: wait; }
.descarga select { border: 1px solid #012169; border-left: none; border-radius: 0 6px 6px 0; padding: 0 8px; font: inherit; color: #012169; background: white; cursor: pointer; }
.adjuntos { margin-top: 22px; border-top: 1px solid #eee; padding-top: 14px; }
.adjuntos-cabecera { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.adjuntos-cabecera h2 { color: #012169; font-size: 1.1rem; margin: 0; }
.lista-adjuntos { list-style: none; padding: 0; margin: 10px 0; display: flex; flex-direction: column; gap: 6px; }
.lista-adjuntos li { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: #f8fafc; border: 1px solid #e3e8ee; border-radius: 6px; }
.lista-adjuntos a { color: #0086c0; font-weight: bold; text-decoration: none; overflow-wrap: anywhere; }
.lista-adjuntos a:hover { text-decoration: underline; }
.lista-adjuntos .btn-mini { margin-left: auto; }
.icono-adjunto { font-size: 1.2rem; }
.gris { color: #777; font-size: 0.82rem; white-space: nowrap; }
.btn-mini.peligro { color: #b02a37; }
.visor-pdf { width: 100%; height: 75vh; border: 1px solid #d8dde3; border-radius: 6px; margin-top: 6px; background: #f4f7f9; }
.historial { margin-top: 26px; background: #f8fafc; border-radius: 8px; padding: 10px 14px; max-width: 860px; }
.historial summary { cursor: pointer; font-weight: bold; color: #012169; }
.historial ol { margin: 10px 0 0; padding-left: 20px; font-size: 0.88rem; }
.historial li { display: flex; gap: 10px; align-items: center; padding: 4px 0; }
.actual { color: #198754; font-weight: bold; font-size: 0.8rem; }
.aviso-version { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; background: #fff4e5; border-left: 4px solid #f0a640; padding: 10px 14px; color: #7a4300; border-radius: 6px; }
.antigua { opacity: 0.92; }

.aviso-seguridad { background: #eef7fb; border-left: 4px solid #17a2b8; padding: 10px 14px; border-radius: 6px; color: #0b4f5c; font-size: 0.9rem; }
.formulario { display: flex; flex-direction: column; gap: 12px; }
.fila { display: flex; gap: 12px; flex-wrap: wrap; }
.fila label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; color: #333; font-weight: bold; }
.fila input { padding: 9px; border: 1px solid #ccd5df; border-radius: 4px; font: inherit; font-weight: normal; }
.ancho { flex: 1; min-width: 240px; }
.editor { background: white; }
.editor :deep(.ql-editor) { min-height: 320px; font-size: 0.98rem; }
.editor :deep(.ql-editor pre.ql-syntax) { background: #0f1b2d; color: #e6edf3; }

@media (max-width: 768px) {
  .panel-paginas { padding: 16px; }
  .buscador { width: 100%; }
  .acciones { width: 100%; }
}
</style>
