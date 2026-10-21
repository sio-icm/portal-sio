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

// Filtros de proyecto, tipo y autor (sirven para las dos vistas)
const cumpleFiltros = (n) => {
  const f = filtros.value
  if (f.proyecto === 'ninguno' && n.proyecto_id !== null) return false
  if (f.proyecto && f.proyecto !== 'ninguno' && String(n.proyecto_id) !== f.proyecto) return false
  if (f.tipo && n.tipo !== f.tipo) return false
  if (f.autor && n.autor !== f.autor) return false
  return true
}

// Vista de lista: además, filtro por fechas
const notasFiltradas = computed(() => notas.value.filter(n => {
  const f = filtros.value
  if (f.desde && n.fecha < f.desde) return false
  if (f.hasta && n.fecha > f.hasta) return false
  return cumpleFiltros(n)
}))

// ---------- VISTA DE CALENDARIO ----------
const CLAVE_VISTA = 'sio_diario_vista'
const leerVista = () => { try { return localStorage.getItem(CLAVE_VISTA) || 'calendario' } catch { return 'calendario' } }
const vista = ref(leerVista()) // 'calendario' o 'lista'
const cambiarVista = (v) => { vista.value = v; try { localStorage.setItem(CLAVE_VISTA, v) } catch { /* sin almacenamiento */ } }

const hoy = hoyIso()
const aIso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
const primerDiaMes = (iso) => { const [a, m] = iso.split('-').map(Number); return new Date(a, m - 1, 1) }
const mesVisible = ref(primerDiaMes(hoy))
const diaSeleccionado = ref(hoy)

const nombreMes = computed(() => {
  const t = new Intl.DateTimeFormat('ca', { month: 'long', year: 'numeric' }).format(mesVisible.value)
  return t.charAt(0).toUpperCase() + t.slice(1)
})
const fechaLarga = (iso) => {
  const [a, m, d] = iso.split('-').map(Number)
  return new Intl.DateTimeFormat('ca', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(a, m - 1, d))
}
const DIAS_SEMANA = ['Dl', 'Dt', 'Dc', 'Dj', 'Dv', 'Ds', 'Dg']

const moverMes = (salto) => {
  const d = mesVisible.value
  mesVisible.value = new Date(d.getFullYear(), d.getMonth() + salto, 1)
}
const irAHoy = () => { mesVisible.value = primerDiaMes(hoy); diaSeleccionado.value = hoy }

const notasPorDia = computed(() => {
  const mapa = {}
  for (const n of notas.value) if (cumpleFiltros(n)) (mapa[n.fecha] ||= []).push(n)
  return mapa
})

// Celdas del mes, empezando en lunes (con los días del mes anterior/siguiente para completar semanas)
const celdas = computed(() => {
  const primero = mesVisible.value
  const desfase = (primero.getDay() + 6) % 7
  const diasMes = new Date(primero.getFullYear(), primero.getMonth() + 1, 0).getDate()
  const total = Math.ceil((desfase + diasMes) / 7) * 7
  return Array.from({ length: total }, (_, i) => {
    const d = new Date(primero.getFullYear(), primero.getMonth(), 1 - desfase + i)
    const iso = aIso(d)
    return { iso, dia: d.getDate(), delMes: d.getMonth() === primero.getMonth(), notas: notasPorDia.value[iso] || [] }
  })
})

const seleccionarDia = (celda) => {
  diaSeleccionado.value = celda.iso
  if (!celda.delMes) mesVisible.value = primerDiaMes(celda.iso)
}

// Notas que se muestran debajo: en lista, las filtradas; en calendario, las del día elegido
const notasMostradas = computed(() => vista.value === 'lista'
  ? notasFiltradas.value
  : (notasPorDia.value[diaSeleccionado.value] || []))

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

const nuevaNota = (fecha) => {
  errorFormulario.value = ''
  formulario.value = notaVacia()
  if (typeof fecha === 'string') formulario.value.fecha = fecha
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
    // En el calendario, se va al día de la nota guardada
    diaSeleccionado.value = datos.fecha
    mesVisible.value = primerDiaMes(datos.fecha)
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

// Aprobar o retirar de la web (solo administradores)
const cambiarPublicacion = async (nota, publicada) => {
  const respuesta = await api(`/api/notas/${nota.id}/publicacion`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ publicada })
  })
  if (respuesta.ok) await cargar()
  else alert("No s'ha pogut canviar la publicació.")
}

// Fotos: se añaden a una nota ya guardada
const subiendoFotos = ref(null) // id de la nota a la que se están subiendo
const subirFotos = async (nota, evento) => {
  const ficheros = [...evento.target.files]
  evento.target.value = ''
  if (!ficheros.length) return
  const datos = new FormData()
  ficheros.forEach(f => datos.append('fotos', f))
  subiendoFotos.value = nota.id
  try {
    const respuesta = await api(`/api/notas/${nota.id}/fotos`, { method: 'POST', body: datos })
    const d = await respuesta.json().catch(() => ({}))
    if (!respuesta.ok) alert(d.error || (respuesta.status === 413 ? 'Les fotos pesen massa (màxim 40 MB en total).' : "No s'han pogut pujar les fotos."))
    else if (d.rechazadas?.length) alert(`Aquests fitxers no són imatges i no s'han pujat: ${d.rechazadas.join(', ')}`)
    await cargar()
  } finally {
    subiendoFotos.value = null
  }
}

const borrarFoto = async (fotoId) => {
  if (!confirm('Esborrar aquesta foto?')) return
  const respuesta = await api(`/api/fotos/${fotoId}`, { method: 'DELETE' })
  if (respuesta.ok) await cargar()
  else alert("No s'ha pogut esborrar la foto.")
}

const limpiarFiltros = () => { filtros.value = { desde: '', hasta: '', proyecto: '', tipo: '', autor: '' } }
</script>

<template>
  <div class="diario">
    <div class="cabecera">
      <h2>📓 Diari d'activitat</h2>
      <div class="cabecera-botones">
        <div class="selector-vista" role="group" aria-label="Vista">
          <button type="button" :class="{ activo: vista === 'calendario' }" :aria-pressed="vista === 'calendario'" @click="cambiarVista('calendario')">📅 Calendari</button>
          <button type="button" :class="{ activo: vista === 'lista' }" :aria-pressed="vista === 'lista'" @click="cambiarVista('lista')">☰ Llista</button>
        </div>
        <button v-if="!formulario" class="btn-principal" @click="nuevaNota(vista === 'calendario' ? diaSeleccionado : undefined)">+ Nova nota</button>
      </div>
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
      <p class="nota-ayuda">Les fotos s'afegeixen des de la nota, un cop desada.
        <span v-if="formulario.visibilidad === 'publica'"> Les notes públiques només surten a la web quan un administrador les aprova.</span></p>
      <p v-if="errorFormulario" class="error">{{ errorFormulario }}</p>
      <div class="botones">
        <button type="submit" class="btn-principal" :disabled="guardando">{{ guardando ? 'Desant...' : '💾 Desar nota' }}</button>
        <button type="button" class="btn-secundario" @click="formulario = null">Cancel·lar</button>
      </div>
    </form>

    <!-- FILTROS -->
    <div class="filtros">
      <template v-if="vista === 'lista'">
        <label>Des de <input type="date" v-model="filtros.desde"></label>
        <label>Fins a <input type="date" v-model="filtros.hasta"></label>
      </template>
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

    <p v-if="cargando" class="aviso">Carregant notes...</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <!-- CALENDARIO -->
    <template v-else-if="vista === 'calendario'">
      <div class="calendario">
        <div class="cal-cabecera">
          <button type="button" class="btn-mes" aria-label="Mes anterior" @click="moverMes(-1)">‹</button>
          <span class="cal-mes">{{ nombreMes }}</span>
          <button type="button" class="btn-mes" aria-label="Mes següent" @click="moverMes(1)">›</button>
          <button type="button" class="btn-secundario btn-hoy" @click="irAHoy">Avui</button>
        </div>
        <div class="cal-grid">
          <div v-for="d in DIAS_SEMANA" :key="d" class="cal-dia-semana">{{ d }}</div>
          <button v-for="c in celdas" :key="c.iso" type="button" class="cal-celda"
                  :class="{ fuera: !c.delMes, hoy: c.iso === hoy, elegido: c.iso === diaSeleccionado }"
                  :aria-label="`${fechaLarga(c.iso)}: ${c.notas.length} notes`" @click="seleccionarDia(c)">
            <span class="cal-numero">{{ c.dia }}</span>
            <span v-for="n in c.notas.slice(0, 3)" :key="n.id" class="cal-chip" :style="{ background: tipoNota(n.tipo).color }" :title="n.titulo">{{ n.titulo }}</span>
            <span v-if="c.notas.length > 3" class="cal-mas">+{{ c.notas.length - 3 }}</span>
          </button>
        </div>
      </div>
      <div class="dia-cabecera">
        <h3>{{ fechaLarga(diaSeleccionado) }}</h3>
        <button v-if="!formulario" class="btn-secundario" @click="nuevaNota(diaSeleccionado)">+ Nova nota per a aquest dia</button>
      </div>
      <p v-if="notasMostradas.length === 0" class="aviso">Cap nota aquest dia.</p>
    </template>

    <!-- LISTA -->
    <template v-else>
      <p v-if="notasFiltradas.length === 0" class="aviso">
        {{ notas.length === 0 ? 'Encara no hi ha cap nota. Comença amb «+ Nova nota».' : 'Cap nota coincideix amb els filtres.' }}
      </p>
      <p v-else class="contador">{{ notasFiltradas.length }} {{ notasFiltradas.length === 1 ? 'nota' : 'notes' }}</p>
    </template>

    <article v-for="nota in (cargando || error ? [] : notasMostradas)" :key="nota.id" class="nota">
      <div class="nota-cabecera">
        <span class="fecha">{{ fechaCorta(nota.fecha) }}</span>
        <span class="etiqueta" :style="{ background: tipoNota(nota.tipo).color }">{{ tipoNota(nota.tipo).etiqueta }}</span>
        <span v-if="nota.visibilidad === 'publica' && nota.publicada" class="etiqueta publica">Publicada a la web</span>
        <span v-else-if="nota.visibilidad === 'publica'" class="etiqueta pendiente">Pública · pendent d'aprovació</span>
        <span class="autor">{{ nota.autor }}</span>
      </div>
      <h4>{{ nota.titulo }}</h4>
      <p class="proyecto">{{ nota.proyecto_titulo || 'Sense projecte' }}</p>
      <div v-if="nota.texto" class="texto" v-html="limpiarHtml(nota.texto)"></div>
      <div v-if="nota.fotos.length" class="fotos">
        <div v-for="f in nota.fotos" :key="f" class="foto">
          <a :href="`/api/fotos/${f}`" target="_blank" rel="noopener"><img :src="`/api/fotos/${f}?mini=1`" alt="" loading="lazy"></a>
          <button v-if="puedeEditar(nota)" class="foto-borrar" title="Esborrar la foto" @click="borrarFoto(f)">✕</button>
        </div>
      </div>
      <div class="acciones">
        <template v-if="puedeEditar(nota)">
          <button class="btn-mini" @click="editarNota(nota)">✏️ Editar</button>
          <label class="btn-mini" :class="{ ocupado: subiendoFotos === nota.id }">
            {{ subiendoFotos === nota.id ? 'Pujant...' : '📷 Afegir fotos' }}
            <input type="file" accept="image/*" multiple hidden :disabled="subiendoFotos !== null" @change="subirFotos(nota, $event)">
          </label>
          <button class="btn-mini peligro" @click="borrar(nota)">🗑️ Esborrar</button>
        </template>
        <template v-if="sesion.es_admin && nota.visibilidad === 'publica'">
          <button v-if="!nota.publicada" class="btn-mini aprobar" @click="cambiarPublicacion(nota, true)">✅ Publicar a la web</button>
          <button v-else class="btn-mini" @click="cambiarPublicacion(nota, false)">↩️ Retirar de la web</button>
        </template>
      </div>
    </article>
  </div>
</template>

<style scoped>
.diario { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #0086c0; }
.cabecera { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }
.cabecera h2 { margin: 0; color: #012169; }
.cabecera-botones { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.selector-vista { display: flex; border: 1px solid #012169; border-radius: 4px; overflow: hidden; }
.selector-vista button { background: white; color: #012169; border: none; padding: 8px 12px; cursor: pointer; font: inherit; font-size: 0.85rem; }
.selector-vista button.activo { background: #012169; color: white; }
.calendario { border: 1px solid #e3e8ee; border-radius: 8px; padding: 12px; margin-bottom: 18px; }
.cal-cabecera { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.cal-mes { font-weight: bold; color: #012169; font-size: 1.1rem; min-width: 170px; text-align: center; }
.btn-mes { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; width: 32px; height: 32px; cursor: pointer; font-size: 1.1rem; }
.btn-hoy { margin-left: auto; padding: 5px 12px; }
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.cal-dia-semana { text-align: center; font-size: 0.75rem; font-weight: bold; color: #666; padding: 4px 0; }
.cal-celda { min-height: 86px; border: 1px solid #e3e8ee; border-radius: 6px; background: white; padding: 4px; display: flex; flex-direction: column; gap: 2px; align-items: stretch; text-align: left; cursor: pointer; font: inherit; overflow: hidden; }
.cal-celda:hover { border-color: #0086c0; }
.cal-celda.fuera { background: #fafbfc; color: #aaa; }
.cal-celda.hoy .cal-numero { background: #0086c0; color: white; border-radius: 10px; padding: 0 6px; }
.cal-celda.elegido { border: 2px solid #012169; box-shadow: 0 0 0 2px rgba(1,33,105,0.12); }
.cal-numero { font-size: 0.8rem; font-weight: bold; align-self: flex-start; }
.cal-chip { color: white; font-size: 0.7rem; border-radius: 3px; padding: 1px 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cal-mas { font-size: 0.7rem; color: #666; }
.dia-cabecera { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
.dia-cabecera h3 { margin: 0; color: #012169; font-size: 1.05rem; }
.dia-cabecera h3::first-letter { text-transform: uppercase; }
@media (max-width: 700px) {
  .diario { padding: 14px; }
  .calendario { padding: 6px; }
  .cal-grid { gap: 2px; }
  .cal-mes { min-width: 0; font-size: 1rem; }
  .cal-celda { min-height: 48px; padding: 3px; }
  .cal-chip { font-size: 0; height: 6px; padding: 0; }
}
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
.etiqueta.publica { background: #198754; }
.etiqueta.pendiente { background: #fd7e14; }
.nota-ayuda { margin: 0; font-size: 0.8rem; color: #666; }
.fotos { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.foto { position: relative; }
.foto img { width: 120px; height: 90px; object-fit: cover; border-radius: 4px; display: block; }
.foto-borrar { position: absolute; top: 3px; right: 3px; background: rgba(0,0,0,0.6); color: white; border: none; border-radius: 50%; width: 22px; height: 22px; cursor: pointer; font-size: 0.75rem; }
.btn-mini.aprobar { background: #e6f4ea; color: #1e6b34; border-color: #a8d5b5; }
label.btn-mini { display: inline-block; font-weight: normal; color: inherit; }
label.btn-mini.ocupado { opacity: 0.6; cursor: wait; }
.autor { margin-left: auto; color: #666; }
.nota h4 { margin: 8px 0 2px; color: #222; }
.proyecto { margin: 0 0 8px; font-size: 0.85rem; color: #0086c0; }
.texto { font-size: 0.92rem; color: #333; line-height: 1.5; }
.acciones { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.8rem; }
.btn-mini.peligro { color: #b02a37; }
</style>
