<script setup>
import { ref, computed, onMounted } from 'vue'
import { TIPOS_NOTA, tipoNota, fechaCorta, peticionIntranet } from '../utils/diario'
import { limpiarHtml } from '../utils/limpiarHtml'

// Informe semestral a partir del diario de actividad: se elige un periodo y
// sale un documento agrupado por proyecto, con cifras, listo para imprimir o
// guardar en PDF (Imprimir -> Guardar como PDF).
const emit = defineEmits(['sesion-caducada'])
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))

const hoy = new Date()
const anio = hoy.getFullYear()
const periodos = [
  { id: `${anio}-2`, nombre: `2n semestre ${anio}`, desde: `${anio}-07-01`, hasta: `${anio}-12-31` },
  { id: `${anio}-1`, nombre: `1r semestre ${anio}`, desde: `${anio}-01-01`, hasta: `${anio}-06-30` },
  { id: `${anio - 1}-2`, nombre: `2n semestre ${anio - 1}`, desde: `${anio - 1}-07-01`, hasta: `${anio - 1}-12-31` },
  { id: `${anio - 1}-1`, nombre: `1r semestre ${anio - 1}`, desde: `${anio - 1}-01-01`, hasta: `${anio - 1}-06-30` }
]
const periodoActual = periodos.find(p => p.id === `${anio}-${hoy.getMonth() < 6 ? 1 : 2}`)

const desde = ref(periodoActual.desde)
const hasta = ref(periodoActual.hasta)
const notas = ref([])
const generado = ref(false)
const cargando = ref(false)
const error = ref('')

const elegirPeriodo = (p) => { desde.value = p.desde; hasta.value = p.hasta; generado.value = false }

const generar = async () => {
  error.value = ''
  cargando.value = true
  try {
    const r = await api(`/api/notas?desde=${desde.value}&hasta=${hasta.value}`)
    if (!r.ok) throw new Error()
    // En el informe, en orden cronológico
    notas.value = (await r.json()).sort((a, b) => a.fecha.localeCompare(b.fecha) || a.id - b.id)
    generado.value = true
  } catch {
    error.value = "No s'han pogut carregar les notes."
  } finally {
    cargando.value = false
  }
}

onMounted(generar)

// Agrupado por proyecto: primero los que tienen más notas; "sin proyecto" al final
const porProyecto = computed(() => {
  const grupos = new Map()
  for (const n of notas.value) {
    const clave = n.proyecto_id ?? 'ninguno'
    if (!grupos.has(clave)) grupos.set(clave, { titulo: n.proyecto_titulo || 'Activitat general (sense projecte)', notas: [] })
    grupos.get(clave).notas.push(n)
  }
  const sin = grupos.get('ninguno')
  grupos.delete('ninguno')
  const lista = [...grupos.values()].sort((a, b) => b.notas.length - a.notas.length)
  return sin ? [...lista, sin] : lista
})

const cifrasTipo = computed(() => TIPOS_NOTA
  .map(t => ({ ...t, total: notas.value.filter(n => n.tipo === t.valor).length }))
  .filter(t => t.total > 0))

const personas = computed(() => {
  const cuenta = {}
  for (const n of notas.value) cuenta[n.autor] = (cuenta[n.autor] || 0) + 1
  return Object.entries(cuenta).sort((a, b) => b[1] - a[1])
})

const numProyectos = computed(() => porProyecto.value.filter(g => g.titulo !== 'Activitat general (sense projecte)').length)

const imprimir = () => window.print()
</script>

<template>
  <div class="informe-panel">
    <div class="controles no-imprimir">
      <h2>🧾 Informe semestral</h2>
      <p class="ayuda">Tria el període i genera l'informe a partir del diari d'activitat. Per desar-lo en PDF: «Imprimir» i després «Desar com a PDF».</p>
      <div class="periodos">
        <button v-for="p in periodos" :key="p.id" type="button" class="btn-periodo"
                :class="{ activo: desde === p.desde && hasta === p.hasta }" @click="elegirPeriodo(p)">{{ p.nombre }}</button>
      </div>
      <div class="fila">
        <label>Des de <input type="date" v-model="desde" @change="generado = false"></label>
        <label>Fins a <input type="date" v-model="hasta" @change="generado = false"></label>
        <button type="button" class="btn-principal" @click="generar" :disabled="cargando">{{ cargando ? 'Generant...' : 'Generar informe' }}</button>
        <button v-if="generado && notas.length" type="button" class="btn-secundario" @click="imprimir">🖨️ Imprimir / Desar PDF</button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <section v-if="generado" class="informe-imprimible">
      <header class="informe-cabecera">
        <p class="institucion">Servei d'Enginyeria Oceanogràfica (SIO) · ICM-CSIC</p>
        <h1>Memòria d'activitat</h1>
        <p class="periodo">Del {{ fechaCorta(desde) }} al {{ fechaCorta(hasta) }}</p>
      </header>

      <p v-if="notas.length === 0" class="aviso">No hi ha notes en aquest període.</p>

      <template v-else>
        <h2>Resum</h2>
        <div class="cifras">
          <div class="cifra"><span class="numero">{{ notas.length }}</span><span>activitats registrades</span></div>
          <div class="cifra"><span class="numero">{{ numProyectos }}</span><span>projectes amb activitat</span></div>
          <div class="cifra"><span class="numero">{{ personas.length }}</span><span>persones de l'equip</span></div>
        </div>
        <table class="tabla">
          <thead><tr><th>Tipus d'activitat</th><th>Nombre</th></tr></thead>
          <tbody><tr v-for="t in cifrasTipo" :key="t.valor"><td>{{ t.etiqueta }}</td><td>{{ t.total }}</td></tr></tbody>
        </table>

        <h2>Activitat per projecte</h2>
        <section v-for="grupo in porProyecto" :key="grupo.titulo" class="grupo">
          <h3>{{ grupo.titulo }} <span class="cuenta">({{ grupo.notas.length }})</span></h3>
          <article v-for="n in grupo.notas" :key="n.id" class="entrada">
            <p class="entrada-cabecera"><strong>{{ fechaCorta(n.fecha) }}</strong> · {{ tipoNota(n.tipo).etiqueta }} · {{ n.autor }}</p>
            <p class="entrada-titulo">{{ n.titulo }}</p>
            <div v-if="n.texto" class="entrada-texto" v-html="limpiarHtml(n.texto)"></div>
            <div v-if="n.fotos && n.fotos.length" class="entrada-fotos">
              <img v-for="f in n.fotos.slice(0, 4)" :key="f" :src="`/api/fotos/${f}?mini=1`" alt="">
            </div>
          </article>
        </section>
      </template>
    </section>
  </div>
</template>

<style scoped>
.informe-panel { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #8cc63f; }
.controles h2 { margin: 0; color: #012169; }
.ayuda { color: #666; font-size: 0.9rem; margin: 8px 0 15px; }
.periodos { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.btn-periodo { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 15px; padding: 5px 12px; cursor: pointer; }
.btn-periodo.activo { background: #012169; color: white; border-color: #012169; }
.fila { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; font-weight: bold; color: #444; }
input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font: inherit; }
.btn-principal { background: #012169; color: white; border: none; padding: 10px 18px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-secundario { background: white; color: #012169; border: 1px solid #012169; padding: 9px 14px; border-radius: 4px; cursor: pointer; }
.error { color: #b02a37; font-weight: bold; }
.aviso { color: #666; font-style: italic; }

.informe-imprimible { margin-top: 25px; border-top: 2px solid #012169; padding-top: 20px; color: #222; }
.informe-cabecera { text-align: center; margin-bottom: 20px; }
.institucion { color: #0086c0; font-weight: bold; margin: 0; }
.informe-cabecera h1 { color: #012169; margin: 6px 0; }
.periodo { margin: 0; color: #555; }
.informe-imprimible h2 { color: #012169; border-bottom: 1px solid #ccd; padding-bottom: 4px; margin-top: 25px; }
.cifras { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 15px; }
.cifra { flex: 1; min-width: 140px; background: #f4f7f9; border-radius: 6px; padding: 12px; text-align: center; display: flex; flex-direction: column; font-size: 0.85rem; color: #444; }
.cifra .numero { font-size: 1.8rem; font-weight: bold; color: #012169; }
.tabla { border-collapse: collapse; min-width: 320px; }
.tabla th, .tabla td { border: 1px solid #d0d7de; padding: 6px 12px; text-align: left; }
.tabla th { background: #f4f7f9; }
.grupo { margin-bottom: 18px; }
.grupo h3 { color: #0086c0; margin-bottom: 8px; }
.cuenta { color: #888; font-weight: normal; font-size: 0.9rem; }
.entrada { border-left: 3px solid #d0d7de; padding: 4px 0 4px 12px; margin-bottom: 10px; break-inside: avoid; }
.entrada-cabecera { margin: 0; font-size: 0.85rem; color: #555; }
.entrada-titulo { margin: 2px 0; font-weight: bold; }
.entrada-texto { font-size: 0.92rem; line-height: 1.5; }
.entrada-fotos { display: flex; gap: 6px; margin-top: 6px; }
.entrada-fotos img { width: 150px; height: 105px; object-fit: cover; border-radius: 3px; }
</style>

<style>
/* Al imprimir solo sale el informe (sin el menú de la intranet ni los botones) */
@media print {
  body * { visibility: hidden; }
  .informe-imprimible, .informe-imprimible * { visibility: visible; }
  .informe-imprimible { position: absolute; left: 0; top: 0; width: 100%; margin: 0; border: none; }
  .no-imprimir { display: none; }
}
</style>
