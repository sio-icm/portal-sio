<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import TextAlign from '@tiptap/extension-text-align'
import TextStyle from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'
import Highlight from '@tiptap/extension-highlight'
import Subscript from '@tiptap/extension-subscript'
import Superscript from '@tiptap/extension-superscript'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Placeholder from '@tiptap/extension-placeholder'

// Editor de textos complet per a la documentació (TipTap): títols, format, colors,
// alineació, subíndex/superíndex, llistes i tasques, taules, codi, cites, enllaços i imatges
// (enganxades, arrossegades o triades). Desa HTML a v-model.
const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' }
})
const emit = defineEmits(['update:modelValue'])
const { t } = useI18n()
const MAX_IMG_MB = 3
const avisoImagen = ref('')

// Imatges com a dades dins del document (no cal pujar-les a part)
const leerImagen = (fichero) => new Promise((resolve) => {
  if (!fichero?.type?.startsWith('image/')) return resolve(null)
  if (fichero.size > MAX_IMG_MB * 1048576) { avisoImagen.value = t('intranet.editor.imagenGrande', { max: MAX_IMG_MB }); return resolve(null) }
  const lector = new FileReader()
  lector.onload = () => resolve(lector.result)
  lector.readAsDataURL(fichero)
})
const insertarImagenes = async (vista, ficheros, pos) => {
  let hecho = false
  for (const f of ficheros) {
    const src = await leerImagen(f)
    if (!src) continue
    const nodo = vista.state.schema.nodes.image.create({ src })
    const tr = pos == null ? vista.state.tr.replaceSelectionWith(nodo) : vista.state.tr.insert(pos, nodo)
    vista.dispatch(tr)
    hecho = true
  }
  return hecho
}

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit.configure({ heading: { levels: [1, 2, 3, 4] } }),
    Underline,
    Link.configure({ openOnClick: false, autolink: true, HTMLAttributes: { rel: 'noopener noreferrer', target: '_blank' } }),
    Image.configure({ allowBase64: true }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    TextStyle, Color,
    Highlight.configure({ multicolor: true }),
    Subscript, Superscript,
    Table.configure({ resizable: true }), TableRow, TableHeader, TableCell,
    TaskList, TaskItem.configure({ nested: true }),
    Placeholder.configure({ placeholder: () => props.placeholder })
  ],
  editorProps: {
    handlePaste: (vista, evento) => {
      const ficheros = [...(evento.clipboardData?.files || [])].filter(f => f.type.startsWith('image/'))
      if (!ficheros.length) return false
      insertarImagenes(vista, ficheros)
      return true
    },
    handleDrop: (vista, evento) => {
      const ficheros = [...(evento.dataTransfer?.files || [])].filter(f => f.type.startsWith('image/'))
      if (!ficheros.length) return false
      const pos = vista.posAtCoords({ left: evento.clientX, top: evento.clientY })?.pos
      insertarImagenes(vista, ficheros, pos)
      return true
    }
  },
  onUpdate: ({ editor: e }) => emit('update:modelValue', e.getHTML())
})
watch(() => props.modelValue, (v) => {
  if (editor.value && v !== editor.value.getHTML()) editor.value.commands.setContent(v || '', false)
})
onBeforeUnmount(() => editor.value?.destroy())

// ---------- Accions de la barra ----------
const ed = () => editor.value.chain().focus()
const activo = (nombre, attrs) => editor.value?.isActive(nombre, attrs)
const bloque = ref('p')
const cambiarBloque = (v) => {
  if (v === 'p') ed().setParagraph().run()
  else ed().toggleHeading({ level: Number(v) }).run()
}
const bloqueActual = () => {
  for (const n of [1, 2, 3, 4]) if (activo('heading', { level: n })) return String(n)
  return 'p'
}
const ponerEnlace = () => {
  const previo = editor.value.getAttributes('link').href || 'https://'
  const url = window.prompt(t('intranet.editor.urlEnlace'), previo)
  if (url === null) return
  if (!url || url === 'https://') ed().extendMarkRange('link').unsetLink().run()
  else ed().extendMarkRange('link').setLink({ href: url }).run()
}
const inputImagen = ref(null)
const elegirImagen = async (e) => {
  const ficheros = [...e.target.files]
  e.target.value = ''
  for (const f of ficheros) {
    const src = await leerImagen(f)
    if (src) ed().setImage({ src }).run()
  }
}
const colorTexto = (e) => ed().setColor(e.target.value).run()
const colorFondo = (e) => ed().toggleHighlight({ color: e.target.value }).run()
const enTabla = () => activo('table')
</script>

<template>
  <div class="editor-rico">
    <div v-if="editor" class="barra" role="toolbar" :aria-label="$t('intranet.editor.barra')">
      <select :value="bloqueActual()" @change="cambiarBloque($event.target.value)" :title="$t('intranet.editor.estilo')" class="sel-bloque">
        <option value="p">{{ $t('intranet.editor.parrafo') }}</option>
        <option v-for="n in [1, 2, 3, 4]" :key="n" :value="String(n)">{{ $t('intranet.editor.titulo', { n }) }}</option>
      </select>
      <span class="sep"></span>
      <button type="button" :class="{ on: activo('bold') }" @click="ed().toggleBold().run()" :title="$t('intranet.editor.negrita')"><b>B</b></button>
      <button type="button" :class="{ on: activo('italic') }" @click="ed().toggleItalic().run()" :title="$t('intranet.editor.cursiva')"><i>I</i></button>
      <button type="button" :class="{ on: activo('underline') }" @click="ed().toggleUnderline().run()" :title="$t('intranet.editor.subrayado')"><u>U</u></button>
      <button type="button" :class="{ on: activo('strike') }" @click="ed().toggleStrike().run()" :title="$t('intranet.editor.tachado')"><s>S</s></button>
      <button type="button" :class="{ on: activo('subscript') }" @click="ed().toggleSubscript().run()" :title="$t('intranet.editor.subindice')">X<sub>2</sub></button>
      <button type="button" :class="{ on: activo('superscript') }" @click="ed().toggleSuperscript().run()" :title="$t('intranet.editor.superindice')">X<sup>2</sup></button>
      <label class="color" :title="$t('intranet.editor.colorTexto')">A<input type="color" @input="colorTexto"></label>
      <label class="color fondo" :title="$t('intranet.editor.colorFondo')">▍<input type="color" value="#fff59d" @input="colorFondo"></label>
      <button type="button" @click="ed().unsetAllMarks().clearNodes().run()" :title="$t('intranet.editor.limpiar')">⌫</button>
      <span class="sep"></span>
      <button type="button" :class="{ on: activo({ textAlign: 'left' }) }" @click="ed().setTextAlign('left').run()" :title="$t('intranet.editor.izquierda')">⟸</button>
      <button type="button" :class="{ on: activo({ textAlign: 'center' }) }" @click="ed().setTextAlign('center').run()" :title="$t('intranet.editor.centro')">≡</button>
      <button type="button" :class="{ on: activo({ textAlign: 'right' }) }" @click="ed().setTextAlign('right').run()" :title="$t('intranet.editor.derecha')">⟹</button>
      <button type="button" :class="{ on: activo({ textAlign: 'justify' }) }" @click="ed().setTextAlign('justify').run()" :title="$t('intranet.editor.justificar')">☰</button>
      <span class="sep"></span>
      <button type="button" :class="{ on: activo('bulletList') }" @click="ed().toggleBulletList().run()" :title="$t('intranet.editor.vinetas')">• ―</button>
      <button type="button" :class="{ on: activo('orderedList') }" @click="ed().toggleOrderedList().run()" :title="$t('intranet.editor.numerada')">1.―</button>
      <button type="button" :class="{ on: activo('taskList') }" @click="ed().toggleTaskList().run()" :title="$t('intranet.editor.tareas')">☑</button>
      <button type="button" :class="{ on: activo('blockquote') }" @click="ed().toggleBlockquote().run()" :title="$t('intranet.editor.cita')">❝</button>
      <button type="button" :class="{ on: activo('codeBlock') }" @click="ed().toggleCodeBlock().run()" :title="$t('intranet.editor.codigo')">&lt;/&gt;</button>
      <button type="button" @click="ed().setHorizontalRule().run()" :title="$t('intranet.editor.separador')">―</button>
      <span class="sep"></span>
      <button type="button" :class="{ on: activo('link') }" @click="ponerEnlace" :title="$t('intranet.editor.enlace')">🔗</button>
      <button type="button" @click="inputImagen.click()" :title="$t('intranet.editor.imagen')">🖼</button>
      <input ref="inputImagen" type="file" accept="image/*" multiple hidden @change="elegirImagen">
      <button type="button" @click="ed().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()" :title="$t('intranet.editor.tabla')">▦</button>
      <span class="sep"></span>
      <button type="button" @click="ed().undo().run()" :disabled="!editor.can().undo()" :title="$t('intranet.editor.deshacer')">↶</button>
      <button type="button" @click="ed().redo().run()" :disabled="!editor.can().redo()" :title="$t('intranet.editor.rehacer')">↷</button>
    </div>
    <!-- Accions de taula: només quan el cursor és dins d'una taula -->
    <div v-if="editor && enTabla()" class="barra barra-tabla">
      <span class="etiqueta">▦ {{ $t('intranet.editor.tabla') }}:</span>
      <button type="button" @click="ed().addRowAfter().run()">{{ $t('intranet.editor.filaMas') }}</button>
      <button type="button" @click="ed().addColumnAfter().run()">{{ $t('intranet.editor.columnaMas') }}</button>
      <button type="button" @click="ed().deleteRow().run()">{{ $t('intranet.editor.filaMenos') }}</button>
      <button type="button" @click="ed().deleteColumn().run()">{{ $t('intranet.editor.columnaMenos') }}</button>
      <button type="button" @click="ed().mergeOrSplit().run()">{{ $t('intranet.editor.unir') }}</button>
      <button type="button" @click="ed().toggleHeaderRow().run()">{{ $t('intranet.editor.cabecera') }}</button>
      <button type="button" class="peligro" @click="ed().deleteTable().run()">{{ $t('intranet.editor.borrarTabla') }}</button>
    </div>
    <p v-if="avisoImagen" class="aviso" role="alert" @click="avisoImagen = ''">{{ avisoImagen }}</p>
    <EditorContent :editor="editor" class="area" />
  </div>
</template>

<style scoped>
.editor-rico { border: 1px solid #ccd5df; border-radius: 6px; background: white; }
.barra { display: flex; flex-wrap: wrap; align-items: center; gap: 2px; padding: 6px; border-bottom: 1px solid #e3e8ee; background: #f8fafc; position: sticky; top: 0; z-index: 2; border-radius: 6px 6px 0 0; }
.barra button, .barra .color { min-width: 32px; height: 32px; padding: 0 7px; border: 1px solid transparent; border-radius: 4px; background: none; cursor: pointer; font: inherit; font-size: 0.92rem; color: #24324a; display: inline-flex; align-items: center; justify-content: center; gap: 2px; }
.barra button:hover, .barra .color:hover { background: #e6eef6; }
.barra button.on { background: #012169; color: white; }
.barra button:disabled { opacity: 0.35; cursor: default; }
.sel-bloque { height: 32px; border: 1px solid #ccd5df; border-radius: 4px; font: inherit; font-size: 0.88rem; padding: 0 6px; background: white; }
.sep { width: 1px; height: 22px; background: #d5dbe2; margin: 0 4px; }
.color { position: relative; font-weight: bold; }
.color input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
.color.fondo { color: #e3c000; }
.barra-tabla { background: #eef7fb; position: static; border-radius: 0; }
.barra-tabla .etiqueta { font-size: 0.85rem; color: #0b4f5c; font-weight: bold; margin-right: 4px; }
.barra-tabla button { font-size: 0.82rem; border: 1px solid #c7dbe6; background: white; }
.barra-tabla button.peligro { color: #b02a37; }
.aviso { margin: 6px; padding: 6px 10px; background: #fdecea; color: #a12622; border-radius: 4px; cursor: pointer; }

/* Àrea d'escriptura */
.area :deep(.ProseMirror) { min-height: 380px; padding: 16px 18px; outline: none; line-height: 1.6; font-size: 0.98rem; color: #222; }
.area :deep(.ProseMirror p.is-editor-empty:first-child::before) { content: attr(data-placeholder); color: #9aa5b1; float: left; height: 0; pointer-events: none; }
.area :deep(h1) { font-size: 1.6rem; color: #012169; margin: 18px 0 8px; }
.area :deep(h2) { font-size: 1.35rem; color: #012169; margin: 16px 0 6px; }
.area :deep(h3) { font-size: 1.15rem; color: #012169; margin: 14px 0 6px; }
.area :deep(h4) { font-size: 1rem; color: #012169; margin: 12px 0 4px; }
.area :deep(p) { margin: 0 0 8px; }
.area :deep(ul), .area :deep(ol) { padding-left: 24px; margin: 0 0 8px; }
.area :deep(blockquote) { border-left: 4px solid #8cc63f; background: #f6faf0; margin: 0 0 8px; padding: 6px 12px; }
.area :deep(pre) { background: #0f1b2d; color: #e6edf3; padding: 10px 12px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 0.88rem; white-space: pre-wrap; }
.area :deep(code) { background: #eef1f4; padding: 1px 4px; border-radius: 3px; font-family: 'Courier New', monospace; }
.area :deep(pre code) { background: none; padding: 0; color: inherit; }
.area :deep(hr) { border: none; border-top: 2px solid #d5dbe2; margin: 14px 0; }
.area :deep(img) { max-width: 100%; height: auto; border-radius: 4px; }
.area :deep(img.ProseMirror-selectednode) { outline: 3px solid #0086c0; }
.area :deep(a) { color: #0086c0; }
.area :deep(mark) { padding: 0 2px; border-radius: 2px; }
.area :deep(table) { border-collapse: collapse; width: 100%; margin: 8px 0; table-layout: fixed; }
.area :deep(td), .area :deep(th) { border: 1px solid #c9d1d9; padding: 6px 8px; vertical-align: top; position: relative; min-width: 40px; }
.area :deep(th) { background: #eef3f8; font-weight: bold; text-align: left; }
.area :deep(.selectedCell::after) { content: ''; position: absolute; inset: 0; background: rgba(0, 134, 192, 0.15); pointer-events: none; }
.area :deep(.column-resize-handle) { position: absolute; right: -2px; top: 0; bottom: 0; width: 4px; background: #0086c0; pointer-events: none; }
.area :deep(ul[data-type="taskList"]) { list-style: none; padding-left: 4px; }
.area :deep(ul[data-type="taskList"] li) { display: flex; gap: 8px; align-items: flex-start; }
.area :deep(ul[data-type="taskList"] li > label) { margin-top: 3px; }
.area :deep(ul[data-type="taskList"] li > div) { flex: 1; }
</style>
