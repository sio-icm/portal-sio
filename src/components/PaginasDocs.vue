<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { QuillEditor } from '@vueup/vue-quill'
import 'quill/dist/quill.snow.css' // estils de Quill 2 (els de vue-quill són de Quill 1 i no pinten bé llistes ni codi)
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'
import { limpiarHtml } from '../utils/limpiarHtml'

// Pàgines de documentació escrites a la intranet (una wiki interna): llista, lectura,
// edició amb historial (qui i quan) i recuperació de versions anteriors.
// Només per al personal amb sessió. No s'hi poden escriure contrasenyes.
const emit = defineEmits(['sesion-caducada'])
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

const TOOLBAR = [
  [{ header: [2, 3, false] }],
  ['bold', 'italic', 'underline', 'strike'],
  [{ list: 'ordered' }, { list: 'bullet' }],
  ['blockquote', 'code-block'],
  ['link', 'image'],
  ['clean']
]

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
onMounted(cargarLista)

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

const abrir = async (id) => {
  error.value = ''; mensaje.value = ''
  const r = await api(`/api/paginas/${id}`)
  if (!r.ok) return fallo(r)
  pagina.value = await r.json()
  vista.value = 'ver'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
const volver = async () => { vista.value = 'lista'; pagina.value = null; version.value = null; await cargarLista() }

const nueva = () => {
  error.value = ''; mensaje.value = ''
  borrador.value = { id: null, titulo: '', categoria: '', contenido: '' }
  vista.value = 'editar'
}
const editar = () => {
  error.value = ''; mensaje.value = ''
  borrador.value = { id: pagina.value.id, titulo: pagina.value.titulo, categoria: pagina.value.categoria, contenido: pagina.value.contenido }
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

    <!-- LLISTA -->
    <template v-if="vista === 'lista'">
      <div class="cabecera">
        <div>
          <h2>{{ $t('intranet.paginas.titulo') }}</h2>
          <p class="subtitulo">{{ $t('intranet.paginas.subtitulo') }}</p>
        </div>
        <div class="acciones">
          <input v-model="buscador" type="search" class="buscador" :placeholder="$t('intranet.paginas.buscar')">
          <button type="button" class="btn-principal" @click="nueva">{{ $t('intranet.paginas.nueva') }}</button>
        </div>
      </div>
      <p v-if="!paginas.length" class="vacio">{{ $t('intranet.paginas.ninguna') }}</p>
      <p v-else-if="!agrupadas.length" class="vacio">{{ $t('intranet.paginas.sinResultados') }}</p>
      <section v-for="[categoria, lista] in agrupadas" :key="categoria" class="grupo">
        <h3>📂 {{ categoria }}</h3>
        <ul class="lista">
          <li v-for="p in lista" :key="p.id">
            <button type="button" class="item" @click="abrir(p.id)">
              <span class="item-titulo">📝 {{ p.titulo }}</span>
              <span class="item-meta">{{ $t('intranet.paginas.actualizadaPor', { quien: p.actualizado_por, fecha: fecha(p.actualizado) }) }}</span>
            </button>
          </li>
        </ul>
      </section>
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
        </div>
        <div class="contenido-wiki" v-html="limpiarHtml(pagina.contenido)"></div>
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
          <QuillEditor theme="snow" v-model:content="borrador.contenido" contentType="html" :toolbar="TOOLBAR" />
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
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 3px 10px; cursor: pointer; font-size: 0.8rem; }
.btn-volver { background: none; border: none; color: #0086c0; font-weight: bold; cursor: pointer; padding: 0; margin-bottom: 14px; font: inherit; font-weight: bold; }
.aviso-ok { color: #198754; font-weight: bold; }
.aviso-error { color: #b02a37; font-weight: bold; background: #fdecea; padding: 10px 14px; border-radius: 6px; }
.vacio { color: #666; font-style: italic; }

.grupo h3 { color: #012169; font-size: 1.05rem; margin: 18px 0 8px; }
.lista { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; }
.item { width: 100%; text-align: left; display: flex; flex-direction: column; gap: 4px; padding: 12px 14px; background: #f8fafc; border: 1px solid #e3e8ee; border-left: 4px solid #17a2b8; border-radius: 6px; cursor: pointer; font: inherit; }
.item:hover { background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.item-titulo { color: #012169; font-weight: bold; }
.item-meta { color: #777; font-size: 0.8rem; }

.pagina { max-width: 860px; }
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
.contenido-wiki :deep(code) { font-family: 'Courier New', monospace; }
.contenido-wiki :deep(img) { max-width: 100%; height: auto; border-radius: 6px; margin: 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.12); }
.contenido-wiki :deep(a) { color: #0086c0; }
.contenido-wiki :deep(table) { border-collapse: collapse; margin: 0 0 12px; }
.contenido-wiki :deep(td), .contenido-wiki :deep(th) { border: 1px solid #ddd; padding: 6px 10px; }

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
