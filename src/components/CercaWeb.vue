<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

// Resultats de la cerca de la barra de dalt. Els textos fixos de la web (serveis, notícies,
// memòria...) es busquen aquí mateix als missatges de cada idioma; la resta (projectes,
// instruments, equip i, amb sessió, documentació interna, PDF, actes i diari) els busca el servidor.
const route = useRoute()
const router = useRouter()
const { t, tm, rt, locale } = useI18n()

const q = ref(String(route.query.q || ''))
const consulta = computed(() => String(route.query.q || '').trim())
const servidor = ref([])
const cargando = ref(false)

const normalizar = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
const palabras = computed(() => normalizar(consulta.value).split(/\s+/).filter(p => p.length >= 2).slice(0, 8))

// ---------- Pàgines de la web (textos de src/i18n) ----------
const PAGINAS = [
  ['inicio', 'inicio'], ['servicios', 'servicios'], ['instrumentacion', 'instrumentacion'], ['pelagia', 'pelagia'],
  ['tanques', 'tanques'], ['salinidad', 'salinidad'], ['fondeos', 'fondeos'], ['prototipado', 'prototipado'],
  ['proyectos', 'proyectos'], ['idi', 'idi'], ['bluelab', 'bluelab'], ['equipo', 'equipo'], ['memoria', 'memoria'],
  ['contacto', 'contacto']
]
// Tots els textos d'una branca dels missatges
const textos = (nodo) => {
  if (nodo == null) return []
  if (typeof nodo === 'string') return [nodo]
  if (typeof nodo === 'object' && (nodo.type !== undefined || nodo.loc !== undefined || nodo.b !== undefined || nodo.s !== undefined)) {
    try { return [rt(nodo)] } catch { return [] }
  }
  if (typeof nodo === 'function') { try { return [rt(nodo)] } catch { return [] } }
  if (Array.isArray(nodo)) return nodo.flatMap(textos)
  if (typeof nodo === 'object') return Object.values(nodo).flatMap(textos)
  return []
}
const limpio = (s) => String(s).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
const coincide = (texto) => { const n = normalizar(texto); return palabras.value.every(p => n.includes(p)) }
const extracto = (texto, largo = 220) => {
  const plano = limpio(texto)
  const n = normalizar(plano)
  const pos = Math.min(...palabras.value.map(p => n.indexOf(p)).filter(i => i >= 0), plano.length)
  const ini = Math.max(0, pos - Math.floor(largo / 3))
  return (ini ? '…' : '') + plano.slice(ini, ini + largo) + (ini + largo < plano.length ? '…' : '')
}
const deLaWeb = computed(() => {
  if (!palabras.value.length) return []
  locale.value // dependència: canviar d'idioma torna a buscar
  const res = []
  for (const [ruta, clave] of PAGINAS) {
    const lista = textos(tm(clave)).map(limpio).filter(Boolean)
    const todo = lista.join(' · ')
    if (!coincide(todo)) continue
    // El tros que millor coincideix: el text que conté més paraules
    const mejor = lista.map(s => [s, palabras.value.filter(p => normalizar(s).includes(p)).length]).sort((a, b) => b[1] - a[1] || Math.min(b[0].length, 400) - Math.min(a[0].length, 400))[0][0]
    res.push({ tipo: 'web', titulo: ruta === 'inicio' ? t('comun.inicio') : t(`rutas.${ruta}`), enlace: { name: ruta }, extracto: extracto(mejor) })
  }
  // Notícies: cadascuna a part
  const noticias = tm('noticias.lista') || []
  ;(Array.isArray(noticias) ? noticias : []).forEach((n, i) => {
    const lista = textos(n).map(limpio)
    if (coincide(lista.join(' '))) {
      res.push({ tipo: 'noticia', titulo: lista[0] || t('rutas.noticias'), enlace: { name: 'noticias', query: { n: i } }, extracto: extracto(lista.slice(1).join(' ')) })
    }
  })
  return res
})

const buscarServidor = async () => {
  servidor.value = []
  if (!palabras.value.length) return
  cargando.value = true
  try {
    const r = await fetch(`/api/buscar?q=${encodeURIComponent(consulta.value)}&idioma=${locale.value}`)
    if (r.ok) servidor.value = await r.json()
  } catch { /* sense connexió */ } finally { cargando.value = false }
}
watch([consulta, locale], () => { q.value = consulta.value; buscarServidor() }, { immediate: true })

const GRUPOS = [
  { clave: 'web', tipos: ['web', 'noticia'], icono: '🌐' },
  { clave: 'proyectos', tipos: ['proyecto'], icono: '📁' },
  { clave: 'instrumentos', tipos: ['instrumento'], icono: '🔧' },
  { clave: 'equipo', tipos: ['equipo'], icono: '👥' },
  { clave: 'documentacion', tipos: ['carpeta', 'pagina'], icono: '📚', interno: true },
  { clave: 'pdf', tipos: ['adjunto'], icono: '📄', interno: true },
  { clave: 'actas', tipos: ['acta'], icono: '📝', interno: true },
  { clave: 'diario', tipos: ['nota'], icono: '📓', interno: true }
]
const todos = computed(() => [...deLaWeb.value, ...servidor.value])
const grupos = computed(() => GRUPOS.map(g => ({ ...g, items: todos.value.filter(r => g.tipos.includes(r.tipo)) })).filter(g => g.items.length))
const total = computed(() => todos.value.length)

// Marcar les paraules trobades (el text s'escapa abans)
const esc = (s) => String(s || '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
const resaltar = (texto) => {
  let html = esc(texto)
  if (!palabras.value.length) return html
  const plano = String(texto || '')
  const n = normalizar(plano)
  const marcas = []
  for (const p of palabras.value) { let i = n.indexOf(p); while (i >= 0) { marcas.push([i, i + p.length]); i = n.indexOf(p, i + p.length) } }
  if (!marcas.length || n.length !== plano.length) return html
  marcas.sort((a, b) => a[0] - b[0])
  let out = '', ult = 0
  for (const [a, b] of marcas) { if (a < ult) continue; out += esc(plano.slice(ult, a)) + '<mark>' + esc(plano.slice(a, b)) + '</mark>'; ult = b }
  return out + esc(plano.slice(ult))
}

const enviar = () => { if (q.value.trim()) router.push({ name: 'cerca', query: { q: q.value.trim() } }) }
</script>

<template>
  <div class="pagina-cerca">
    <div class="contenedor-ancho">
      <h1>🔍 {{ $t('cerca.titulo') }}</h1>
      <form class="caja" role="search" @submit.prevent="enviar">
        <input v-model="q" type="search" :placeholder="$t('cerca.placeholder')" :aria-label="$t('cerca.titulo')" autofocus>
        <button type="submit">{{ $t('cerca.buscar') }}</button>
      </form>

      <p v-if="!palabras.length" class="nota">{{ $t('cerca.escribe') }}</p>
      <template v-else>
        <p class="nota" role="status">
          <template v-if="cargando && !total">{{ $t('cerca.buscando') }}</template>
          <template v-else>{{ $t('cerca.resultados', { n: total, q: consulta }) }}</template>
        </p>

        <section v-for="g in grupos" :key="g.clave" class="grupo">
          <h2>{{ g.icono }} {{ $t(`cerca.grupos.${g.clave}`) }} <small>({{ g.items.length }})</small>
            <span v-if="g.interno" class="interno">🔒 {{ $t('cerca.interno') }}</span></h2>
          <ul>
            <li v-for="(r, i) in g.items" :key="g.clave + i">
              <a v-if="r.externo" :href="r.enlace" target="_blank" rel="noopener" class="titulo" v-html="resaltar(r.titulo)"></a>
              <RouterLink v-else :to="r.enlace" class="titulo" v-html="resaltar(r.titulo)"></RouterLink>
              <span class="meta">
                <template v-if="r.carpeta">📂 {{ r.carpeta }}</template>
                <template v-if="r.pagina"> · 📄 {{ r.pagina }}</template>
                <template v-if="r.pagina_pdf"> · {{ $t('cerca.paginaPdf', { n: r.pagina_pdf }) }}</template>
                <template v-if="r.fecha"> · {{ r.fecha }}</template>
              </span>
              <p v-if="r.extracto" class="extracto" v-html="resaltar(r.extracto)"></p>
            </li>
          </ul>
        </section>
        <p v-if="!cargando && !total" class="vacio">{{ $t('cerca.nada') }}</p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.pagina-cerca { background: #f4f7f9; min-height: 70vh; padding: 40px 0 60px; }
h1 { color: #012169; margin: 0 0 16px; font-size: 1.8rem; }
.caja { display: flex; gap: 8px; max-width: 720px; margin-bottom: 10px; }
.caja input { flex: 1; font: inherit; font-size: 1.05rem; padding: 11px 14px; border: 2px solid #012169; border-radius: 8px; min-width: 0; }
.caja button { background: #012169; color: white; border: none; border-radius: 8px; padding: 0 20px; font-weight: bold; cursor: pointer; }
.nota { color: #555; }
.vacio { color: #666; font-style: italic; }
.grupo { background: white; border-radius: 10px; padding: 16px 20px; margin: 14px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.grupo h2 { margin: 0 0 8px; font-size: 1.15rem; color: #012169; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.grupo h2 small { color: #777; font-weight: normal; }
.interno { margin-left: auto; font-size: 0.75rem; font-weight: normal; color: #7a4300; background: #fff4e5; border-radius: 10px; padding: 2px 8px; }
.grupo ul { list-style: none; margin: 0; padding: 0; }
.grupo li { padding: 10px 0; border-top: 1px solid #eef1f4; }
.grupo li:first-child { border-top: none; }
.titulo { font-weight: bold; color: #0060a0; text-decoration: none; font-size: 1.02rem; }
.titulo:hover { text-decoration: underline; }
.meta { display: block; color: #777; font-size: 0.82rem; margin-top: 2px; }
.extracto { margin: 4px 0 0; color: #333; font-size: 0.92rem; line-height: 1.45; }
:deep(mark) { background: #fff1a8; color: inherit; padding: 0 1px; border-radius: 2px; }
@media (max-width: 768px) {
  .pagina-cerca { padding-top: 24px; }
  .grupo { padding: 12px 14px; }
}
</style>
