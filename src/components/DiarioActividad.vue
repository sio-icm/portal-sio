<script setup>
import { ref, computed, onMounted } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { TIPOS_NOTA, tipoNota, fechaCorta, hoyIso, peticionIntranet } from '../utils/diario'
import { limpiarHtml } from '../utils/limpiarHtml'

// Diario de actividad del equipo: cada nota es algo que se ha hecho (fecha,
// proyecto opcional, tipo y texto). Sirve para la memoria semestral y, las
// marcadas como públicas, más adelante para el diario de campaña de la web.
const props = defineProps({ sesion: { type: Object, required: true } })
const emit = defineEmits(['sesion-caducada'])
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))

const notas = ref([])
const proyectos = ref([])
const cargando = ref(true)
const error = ref('')

const filtros = ref({ desde: '', hasta: '', proyecto: '', tipo: '', autor: '' })
const notaVacia = () => ({ id: null, fecha: hoyIso(), titulo: '', tipo: 'altres', proyecto_id: '', visibilidad: 'interna', texto: '' })
const formulario = ref(null) // null = cerrado; si no, la nota que se está escribiendo
const guardando = ref(false)
const errorFormulario = ref('')

const opcionsEditor = [
  [{ header: [3, false] }],
  ['bold', 'italic', 'underline'],
  [{ list: 'ordered' }, { list: 'bullet' }],
  ['link'],
  ['clean']
]

const autores = computed(() => [...new Set(notas.value.map(n => n.autor))].sort())

const notasFiltradas = computed(() => notas.value.filter(n => {
  const f = filtros.value
  if (f.desde && n.fecha < f.desde) return false
  if (f.hasta && n.fecha > f.hasta) return false
  if (f.proyecto === 'ninguno' && n.proyecto_id !== null) return false
  if (f.proyecto && f.proyecto !== 'ninguno' && String(n.proyecto_id) !== f.proyecto) return false
  if (f.tipo && n.tipo !== f.tipo) return false
  if (f.autor && n.autor !== f.autor) return false
  return true
}))

const puedeEditar = (nota) => props.sesion.es_admin || (nota.usuario_id !== null && nota.usuario_id === props.sesion.usuario_id)

const cargar = async () => {
  cargando.value = true
  error.value = ''
  try {
    const [rn, rp] = await Promise.all([api('/api/notas'), api('/api/proyectos')])
    if (!rn.ok || !rp.ok) throw new Error()
    notas.value = await rn.json()
    proyectos.value = (await rp.json()).sort((a, b) => a.titulo.localeCompare(b.titulo))
  } catch {
    error.value = "No s'han pogut carregar les notes."
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

const nuevaNota = () => {
  errorFormulario.value = ''
  formulario.value = notaVacia()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const editarNota = (nota) => {
  errorFormulario.value = ''
  formulario.value = {
    id: nota.id, fecha: nota.fecha, titulo: nota.titulo, tipo: nota.tipo,
    proyecto_id: nota.proyecto_id === null ? '' : String(nota.proyecto_id),
    visibilidad: nota.visibilidad, texto: nota.texto
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const guardar = async () => {
  errorFormulario.value = ''
  if (!formulario.value.titulo.trim()) {
    errorFormulario.value = 'Cal posar un títol.'
    return
  }
  guardando.value = true
  try {
    const { id, ...datos } = formulario.value
    const respuesta = await api(id ? `/api/notas/${id}` : '/api/notas', {
      method: id ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    })
    if (!respuesta.ok) {
      const d = await respuesta.json().catch(() => ({}))
      errorFormulario.value = d.error || "No s'ha pogut desar la nota."
      return
    }
    formulario.value = null
    await cargar()
  } catch {
    errorFormulario.value = "No s'ha pogut connectar amb el servidor."
  } finally {
    guardando.value = false
  }
}

const borrar = async (nota) => {
  if (!confirm(`Segur que vols esborrar la nota «${nota.titulo}»?`)) return
  const respuesta = await api(`/api/notas/${nota.id}`, { method: 'DELETE' })
  if (respuesta.ok) await cargar()
  else alert("No s'ha pogut esborrar la nota.")
}

const limpiarFiltros = () => { filtros.value = { desde: '', hasta: '', proyecto: '', tipo: '', autor: '' } }
</script>

<template>
  <div class="diario">
    <div class="cabecera">
      <h2>📓 Diari d'activitat</h2>
      <button v-if="!formulario" class="btn-principal" @click="nuevaNota">+ Nova nota</button>
    </div>
    <p class="ayuda">Apunta aquí el que fem: campanyes, desenvolupaments, manteniments, calibratges... Les notes serveixen per fer la memòria semestral.</p>

    <!-- FORMULARIO -->
    <form v-if="formulario" class="formulario" @submit.prevent="guardar">
      <h3>{{ formulario.id ? 'Editar nota' : 'Nova nota' }}</h3>
      <div class="fila">
        <label>Data
          <input type="date" v-model="formulario.fecha" required>
        </label>
        <label class="ancho">Títol
          <input type="text" v-model="formulario.titulo" maxlength="200" placeholder="Ex.: Preparació del material per a la campanya a l'Antàrtida" required>
        </label>
      </div>
      <div class="fila">
        <label>Tipus
          <select v-model="formulario.tipo">
            <option v-for="t in TIPOS_NOTA" :key="t.valor" :value="t.valor">{{ t.etiqueta }}</option>
          </select>
        </label>
        <label class="ancho">Projecte
          <select v-model="formulario.proyecto_id">
            <option value="">Sense projecte (general)</option>
            <option v-for="p in proyectos" :key="p.id" :value="String(p.id)">{{ p.titulo }}</option>
          </select>
        </label>
        <label>Visibilitat
          <select v-model="formulario.visibilidad">
            <option value="interna">Interna (només l'equip)</option>
            <option value="publica">Pública (pot sortir a la web)</option>
          </select>
        </label>
      </div>
      <label>Text</label>
      <QuillEditor theme="snow" v-model:content="formulario.texto" contentType="html" :toolbar="opcionsEditor" class="editor" />
      <p v-if="errorFormulario" class="error">{{ errorFormulario }}</p>
      <div class="botones">
        <button type="submit" class="btn-principal" :disabled="guardando">{{ guardando ? 'Desant...' : '💾 Desar nota' }}</button>
        <button type="button" class="btn-secundario" @click="formulario = null">Cancel·lar</button>
      </div>
    </form>

    <!-- FILTROS -->
    <div class="filtros">
      <label>Des de <input type="date" v-model="filtros.desde"></label>
      <label>Fins a <input type="date" v-model="filtros.hasta"></label>
      <label>Projecte
        <select v-model="filtros.proyecto">
          <option value="">Tots</option>
          <option value="ninguno">Sense projecte</option>
          <option v-for="p in proyectos" :key="p.id" :value="String(p.id)">{{ p.titulo }}</option>
        </select>
      </label>
      <label>Tipus
        <select v-model="filtros.tipo">
          <option value="">Tots</option>
          <option v-for="t in TIPOS_NOTA" :key="t.valor" :value="t.valor">{{ t.etiqueta }}</option>
        </select>
      </label>
      <label>Autor
        <select v-model="filtros.autor">
          <option value="">Tothom</option>
          <option v-for="a in autores" :key="a" :value="a">{{ a }}</option>
        </select>
      </label>
      <button type="button" class="btn-secundario" @click="limpiarFiltros">Netejar</button>
    </div>

    <!-- LISTADO -->
    <p v-if="cargando" class="aviso">Carregant notes...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="notasFiltradas.length === 0" class="aviso">
      {{ notas.length === 0 ? 'Encara no hi ha cap nota. Comença amb «+ Nova nota».' : 'Cap nota coincideix amb els filtres.' }}
    </p>
    <p v-else class="contador">{{ notasFiltradas.length }} {{ notasFiltradas.length === 1 ? 'nota' : 'notes' }}</p>

    <article v-for="nota in notasFiltradas" :key="nota.id" class="nota">
      <div class="nota-cabecera">
        <span class="fecha">{{ fechaCorta(nota.fecha) }}</span>
        <span class="etiqueta" :style="{ background: tipoNota(nota.tipo).color }">{{ tipoNota(nota.tipo).etiqueta }}</span>
        <span v-if="nota.visibilidad === 'publica'" class="etiqueta publica">Pública</span>
        <span class="autor">{{ nota.autor }}</span>
      </div>
      <h4>{{ nota.titulo }}</h4>
      <p class="proyecto">{{ nota.proyecto_titulo || 'Sense projecte' }}</p>
      <div v-if="nota.texto" class="texto" v-html="limpiarHtml(nota.texto)"></div>
      <div v-if="puedeEditar(nota)" class="acciones">
        <button class="btn-mini" @click="editarNota(nota)">✏️ Editar</button>
        <button class="btn-mini peligro" @click="borrar(nota)">🗑️ Esborrar</button>
      </div>
    </article>
  </div>
</template>

<style scoped>
.diario { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #0086c0; }
.cabecera { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }
.cabecera h2 { margin: 0; color: #012169; }
.ayuda { color: #666; font-size: 0.9rem; margin: 8px 0 20px; }
.formulario { background: #f4f7f9; border-radius: 8px; padding: 20px; margin-bottom: 25px; display: flex; flex-direction: column; gap: 12px; }
.formulario h3 { margin: 0; color: #012169; }
.fila { display: flex; gap: 12px; flex-wrap: wrap; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; font-weight: bold; color: #444; }
.ancho { flex: 1; min-width: 220px; }
input, select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font: inherit; font-weight: normal; }
.editor { background: white; min-height: 140px; }
.botones { display: flex; gap: 10px; }
.btn-principal { background: #012169; color: white; border: none; padding: 10px 18px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-principal:disabled { opacity: 0.6; cursor: wait; }
.btn-secundario { background: white; color: #012169; border: 1px solid #012169; padding: 8px 14px; border-radius: 4px; cursor: pointer; }
.filtros { display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end; padding: 15px 0; border-top: 1px solid #eee; border-bottom: 1px solid #eee; margin-bottom: 15px; }
.aviso { color: #666; font-style: italic; }
.error { color: #b02a37; font-weight: bold; }
.contador { color: #666; font-size: 0.85rem; }
.nota { border: 1px solid #e3e8ee; border-left: 4px solid #0086c0; border-radius: 6px; padding: 15px 18px; margin-bottom: 12px; }
.nota-cabecera { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font-size: 0.8rem; }
.fecha { font-weight: bold; color: #012169; }
.etiqueta { color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; }
.etiqueta.publica { background: #8cc63f; }
.autor { margin-left: auto; color: #666; }
.nota h4 { margin: 8px 0 2px; color: #222; }
.proyecto { margin: 0 0 8px; font-size: 0.85rem; color: #0086c0; }
.texto { font-size: 0.92rem; color: #333; line-height: 1.5; }
.acciones { display: flex; gap: 8px; margin-top: 10px; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.8rem; }
.btn-mini.peligro { color: #b02a37; }
</style>
