<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { limpiarHtml } from '../utils/limpiarHtml'

// Projectes i campanyes: comptadors per estat (que fan de filtre), filtre per tipus, cercador,
// graella de fitxes amb portada i finestra amb el projecte sencer («Veure més»).
const { t } = useI18n()
const proyectos = ref([])
const cargando = ref(true)
const errorCarga = ref(false)

// Estat guardat a la base de dades -> grup de la pàgina (en aquest ordre)
const GRUPO_POR_ESTADO = { 'En Curs': 'enCurso', 'Aprovat': 'aprobados', 'Sol·licitat': 'solicitados', 'Finalitzat': 'finalizados' }
const GRUPOS = ['enCurso', 'aprobados', 'solicitados', 'finalizados']
const grupoDe = (p) => GRUPO_POR_ESTADO[p.estado] || 'enCurso'

// Categoria guardada a la base de dades -> clau de traducció, color i icona de la portada
const CATEGORIAS = {
  'Infraestructura': { clave: 'infraestructura', color: '#1e8e4f', icono: '⚓' },
  'Campanya': { clave: 'campanya', color: '#0086c0', icono: '🚢' },
  'Contrato': { clave: 'contrato', color: '#138a9c', icono: '📑' },
  'Plan Nacional': { clave: 'planNacional', color: '#c48a00', icono: '🔬' },
  'I+D+I': { clave: 'idi', color: '#4a5a70', icono: '💡' },
  'Divulgació científica': { clave: 'divulgacion', color: '#6f42c1', icono: '🎭' },
  'Divulgación científica': { clave: 'divulgacion', color: '#6f42c1', icono: '🎭' },
  'Otro': { clave: 'otro', color: '#d9661a', icono: '✨' }
}
const categoria = (p) => CATEGORIAS[p.categoria] || { clave: null, color: '#4a5a70', icono: '🌊' }
const nombreCategoria = (p) => categoria(p).clave ? t(`proyectos.categorias.${categoria(p).clave}`) : (p.categoria || '')

// Portada: la imatge triada a la intranet o, si no n'hi ha, la primera foto de la descripció ampliada
const portada = (p) => {
  if (p.imagen) return p.imagen
  const m = /<img[^>]+src="([^"]+)"/i.exec(limpiarHtml(p.descripcion_ampliada || ''))
  return m ? m[1] : ''
}

const cargarProyectos = async () => {
  try {
    const res = await fetch('/api/proyectos')
    if (!res.ok) throw new Error(res.status)
    proyectos.value = await res.json()
  } catch (error) {
    console.error('Error cargando proyectos:', error)
    errorCarga.value = true
  } finally {
    cargando.value = false
  }
}
onMounted(cargarProyectos)

// ---------- FILTRES ----------
const grupoActivo = ref('todos')
const categoriaActiva = ref('todas')
const busqueda = ref('')
const normalizar = (s) => (s || '').toString().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')

const cuenta = (grupo) => proyectos.value.filter(p => grupoDe(p) === grupo).length
const categoriasPresentes = computed(() => [...new Set(proyectos.value.map(p => p.categoria).filter(Boolean))])

const filtrados = computed(() => {
  const q = normalizar(busqueda.value.trim())
  return proyectos.value
    .filter(p => grupoActivo.value === 'todos' || grupoDe(p) === grupoActivo.value)
    .filter(p => categoriaActiva.value === 'todas' || p.categoria === categoriaActiva.value)
    .filter(p => !q || normalizar([p.titulo, p.descripcion_corta, p.investigador_principal, p.pit, nombreCategoria(p)].join(' ')).includes(q))
    .sort((a, b) => GRUPOS.indexOf(grupoDe(a)) - GRUPOS.indexOf(grupoDe(b)) || a.titulo.localeCompare(b.titulo))
})
const limpiarFiltros = () => { grupoActivo.value = 'todos'; categoriaActiva.value = 'todas'; busqueda.value = '' }

// ---------- FINESTRA «VEURE MÉS» ----------
const abierto = ref(null)
const alPulsarTecla = (e) => { if (e.key === 'Escape') abierto.value = null }
watch(abierto, (p) => {
  document.body.style.overflow = p ? 'hidden' : ''
  if (p) window.addEventListener('keydown', alPulsarTecla)
  else window.removeEventListener('keydown', alPulsarTecla)
})
onBeforeUnmount(() => { document.body.style.overflow = ''; window.removeEventListener('keydown', alPulsarTecla) })
</script>

<template>
  <div class="proyectos-hub">
    <div class="fondo-proyectos"></div>

    <div class="contenedor-ancho contenido-hub">
      <h1 class="titulo-seccion">{{ $t('proyectos.titulo') }}</h1>
      <p class="subtitulo">{{ $t('proyectos.subtitulo') }}</p>

      <!-- Comptadors per estat: també són el filtre principal -->
      <div class="estadisticas" role="group" :aria-label="$t('proyectos.estado')">
        <button type="button" class="estadistica" :class="{ activa: grupoActivo === 'todos' }" :aria-pressed="grupoActivo === 'todos'" @click="grupoActivo = 'todos'">
          <span class="cifra">{{ proyectos.length }}</span><span class="etiqueta">{{ $t('proyectos.todos') }}</span>
        </button>
        <button v-for="g in GRUPOS" :key="g" type="button" class="estadistica" :class="['estado-' + g, { activa: grupoActivo === g }]"
          :aria-pressed="grupoActivo === g" :disabled="!cuenta(g)" @click="grupoActivo = g">
          <span class="cifra"><i class="punto" aria-hidden="true"></i>{{ cuenta(g) }}</span><span class="etiqueta">{{ $t(`proyectos.grupos.${g}.titulo`) }}</span>
        </button>
      </div>
      <p v-if="grupoActivo !== 'todos'" class="texto-grupo">{{ $t(`proyectos.grupos.${grupoActivo}.texto`) }}</p>

      <!-- Tipus i cercador -->
      <div class="barra-filtros">
        <div class="chips" role="group" :aria-label="$t('proyectos.tipo')">
          <button type="button" class="chip" :class="{ activo: categoriaActiva === 'todas' }" :aria-pressed="categoriaActiva === 'todas'" @click="categoriaActiva = 'todas'">{{ $t('proyectos.todos') }}</button>
          <button v-for="c in categoriasPresentes" :key="c" type="button" class="chip" :class="{ activo: categoriaActiva === c }"
            :style="categoriaActiva === c ? { background: categoria({ categoria: c }).color, borderColor: categoria({ categoria: c }).color } : {}"
            :aria-pressed="categoriaActiva === c" @click="categoriaActiva = c">{{ categoria({ categoria: c }).icono }} {{ nombreCategoria({ categoria: c }) }}</button>
        </div>
        <input v-model="busqueda" type="search" class="buscador" :placeholder="$t('proyectos.buscar')" :aria-label="$t('proyectos.buscar')">
      </div>

      <p v-if="cargando" class="aviso-lista">{{ $t('proyectos.cargando') }}</p>
      <p v-else-if="errorCarga" class="aviso-lista">{{ $t('proyectos.errorCarga') }}</p>
      <p v-else-if="!filtrados.length" class="aviso-lista">{{ $t('proyectos.sinResultados') }} <button type="button" class="enlace-limpiar" @click="limpiarFiltros">{{ $t('proyectos.verTodos') }}</button></p>

      <!-- Fitxes -->
      <div class="grid-proyectos">
        <article v-for="p in filtrados" :key="p.id" class="tarjeta" :style="{ '--color': categoria(p).color }">
          <button type="button" class="portada" :class="{ 'sin-foto': !portada(p) }" @click="abierto = p" :aria-label="$t('proyectos.verMas') + ': ' + p.titulo">
            <img v-if="portada(p)" :src="portada(p)" alt="" loading="lazy">
            <span v-else class="icono-portada" aria-hidden="true">{{ categoria(p).icono }}</span>
            <span class="pastilla-estado" :class="'estado-' + grupoDe(p)"><i class="punto" aria-hidden="true"></i>{{ $t(`proyectos.grupos.${grupoDe(p)}.titulo`) }}</span>
          </button>
          <div class="cuerpo">
            <span class="badge-tipo">{{ nombreCategoria(p) }}</span>
            <h2 class="titulo-tarjeta">{{ p.titulo }}</h2>
            <p class="resumen">{{ p.descripcion_corta }}</p>
            <ul class="personas">
              <li v-if="p.investigador_principal"><span aria-hidden="true">👤</span> <span class="sr">{{ $t('proyectos.ip') }}:</span> {{ p.investigador_principal }}</li>
              <li v-if="p.pit"><span aria-hidden="true">🛠️</span> <span class="sr">{{ $t('proyectos.pit') }}:</span> {{ p.pit }}</li>
            </ul>
            <button type="button" class="ver-mas" @click="abierto = p">{{ $t('proyectos.verMas') }} →</button>
          </div>
        </article>
      </div>
    </div>

    <!-- Finestra amb el projecte sencer -->
    <div v-if="abierto" class="modal-fondo" @click.self="abierto = null">
      <article class="modal" role="dialog" aria-modal="true" aria-labelledby="titulo-proyecto" :style="{ '--color': categoria(abierto).color }">
        <button type="button" class="modal-cerrar" @click="abierto = null" :aria-label="$t('proyectos.cerrar')">✕</button>
        <div class="modal-portada" :class="{ 'sin-foto': !portada(abierto) }">
          <img v-if="portada(abierto)" :src="portada(abierto)" alt="">
          <span v-else class="icono-portada" aria-hidden="true">{{ categoria(abierto).icono }}</span>
        </div>
        <div class="modal-cuerpo">
          <div class="etiquetas">
            <span class="pastilla-estado" :class="'estado-' + grupoDe(abierto)"><i class="punto" aria-hidden="true"></i>{{ $t(`proyectos.grupos.${grupoDe(abierto)}.titulo`) }}</span>
            <span class="badge-tipo">{{ nombreCategoria(abierto) }}</span>
          </div>
          <h2 id="titulo-proyecto">{{ abierto.titulo }}</h2>
          <dl v-if="abierto.investigador_principal || abierto.pit" class="ficha">
            <template v-if="abierto.investigador_principal"><dt>{{ $t('proyectos.ip') }}</dt><dd>{{ abierto.investigador_principal }}</dd></template>
            <template v-if="abierto.pit"><dt>{{ $t('proyectos.pit') }}</dt><dd>{{ abierto.pit }}</dd></template>
          </dl>
          <div v-if="abierto.descripcion_ampliada && limpiarHtml(abierto.descripcion_ampliada).replace(/<[^>]+>/g, '').trim()" class="contenido-html" v-html="limpiarHtml(abierto.descripcion_ampliada)"></div>
          <p v-else class="contenido-html">{{ abierto.descripcion_corta }}</p>
          <a v-if="abierto.wiki_url" :href="abierto.wiki_url" target="_blank" rel="noopener" class="btn-web-proyecto">{{ $t('proyectos.web') }} ↗</a>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.proyectos-hub { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-proyectos { position: absolute; top: 0; left: 0; width: 100%; height: 520px; background-image: linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.88)), url('/pecesaguasalada.webp'); background-size: cover; background-position: center; z-index: 0; }
.contenido-hub { position: relative; z-index: 10; padding-top: 120px; }
.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 28px; max-width: 800px; }
.aviso-lista { color: #555; font-style: italic; margin: 10px 0 20px; }
.enlace-limpiar { background: none; border: none; color: #0086c0; font-weight: bold; cursor: pointer; text-decoration: underline; font: inherit; font-style: normal; }

/* Colors dels estats */
.estado-enCurso { --estado: #8cc63f; }
.estado-aprobados { --estado: #3db2ff; }
.estado-solicitados { --estado: #ffb020; }
.estado-finalizados { --estado: #aab4bf; }
.punto { display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: var(--estado, #fff); margin-right: 7px; vertical-align: 1px; }
.estado-enCurso .punto { box-shadow: 0 0 0 0 rgba(140, 198, 63, 0.7); animation: latido 2s infinite; }
@keyframes latido { 70% { box-shadow: 0 0 0 7px rgba(140, 198, 63, 0); } 100% { box-shadow: 0 0 0 0 rgba(140, 198, 63, 0); } }
@media (prefers-reduced-motion: reduce) { .estado-enCurso .punto { animation: none; } }

/* Comptadors */
.estadisticas { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 10px; }
.estadistica { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; padding: 14px 16px; border-radius: 12px; cursor: pointer; text-align: left;
  background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.25); color: white; font: inherit; backdrop-filter: blur(4px); transition: background 0.2s, transform 0.2s; }
.estadistica:hover:not(:disabled) { background: rgba(255, 255, 255, 0.2); transform: translateY(-2px); }
.estadistica:disabled { opacity: 0.45; cursor: default; }
.estadistica.activa { background: white; color: #012169; border-color: white; }
.cifra { font-size: 2rem; font-weight: bold; line-height: 1.1; }
.etiqueta { font-size: 0.85rem; opacity: 0.9; }
.texto-grupo { color: #e0e6ed; margin: 4px 0 0; }

/* Tipus i cercador */
.barra-filtros { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between; margin: 18px 0 26px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 7px 14px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.45); background: rgba(1, 33, 105, 0.35); color: white; font: inherit; font-size: 0.85rem; cursor: pointer; }
.chip:hover { background: rgba(255, 255, 255, 0.18); }
.chip.activo { background: #8cc63f; border-color: #8cc63f; color: white; font-weight: bold; }
.buscador { flex: 0 1 280px; padding: 10px 14px; border-radius: 22px; border: none; font: inherit; font-size: 0.92rem; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15); }

/* Graella de fitxes */
.grid-proyectos { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 26px; }
.tarjeta { background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); display: flex; flex-direction: column; transition: transform 0.25s, box-shadow 0.25s; }
.tarjeta:hover { transform: translateY(-5px); box-shadow: 0 16px 36px rgba(0, 0, 0, 0.16); }
.portada { position: relative; display: block; width: 100%; height: 170px; padding: 0; border: none; cursor: pointer; overflow: hidden; background: var(--color); }
.portada img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
.tarjeta:hover .portada img { transform: scale(1.06); }
.portada::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(1, 20, 60, 0.35), transparent 45%); pointer-events: none; }
.sin-foto { background: radial-gradient(circle at 75% 20%, rgba(255, 255, 255, 0.28), transparent 45%), linear-gradient(135deg, var(--color), #012169); }
.sin-foto::before { content: ''; position: absolute; inset: 0; opacity: 0.18; pointer-events: none;
  background: repeating-radial-gradient(circle at 0% 100%, transparent 0 18px, rgba(255, 255, 255, 0.9) 19px 20px); }
.icono-portada { position: absolute; right: 22px; bottom: 14px; font-size: 3.6rem; line-height: 1; filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.25)); }
.pastilla-estado { display: inline-flex; align-items: center; padding: 5px 11px; border-radius: 20px; font-size: 0.78rem; font-weight: bold; color: white; background: rgba(1, 20, 60, 0.75); backdrop-filter: blur(3px); }
.portada .pastilla-estado { position: absolute; top: 12px; left: 12px; z-index: 1; }
.cuerpo { display: flex; flex-direction: column; flex: 1; padding: 18px 22px 20px; }
.badge-tipo { align-self: flex-start; font-size: 0.74rem; font-weight: bold; padding: 3px 10px; border-radius: 20px; color: var(--color); background: color-mix(in srgb, var(--color) 13%, white); }
.titulo-tarjeta { color: #012169; font-size: 1.2rem; line-height: 1.3; margin: 10px 0 8px; }
.resumen { color: #555; font-size: 0.93rem; line-height: 1.55; margin: 0; display: -webkit-box; -webkit-line-clamp: 3; line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.personas { list-style: none; padding: 0; margin: 12px 0 0; font-size: 0.84rem; color: #444; display: flex; flex-direction: column; gap: 4px; }
.personas li { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.ver-mas { margin-top: auto; padding-top: 14px; align-self: flex-start; background: none; border: none; color: #0086c0; font: inherit; font-weight: bold; cursor: pointer; }
.ver-mas:hover { color: #012169; text-decoration: underline; }

/* Finestra */
.modal-fondo { position: fixed; inset: 0; z-index: 1000; background: rgba(1, 20, 60, 0.7); display: flex; align-items: flex-start; justify-content: center; padding: 40px 16px; overflow-y: auto; }
.modal { position: relative; width: 100%; max-width: 780px; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3); }
.modal-cerrar { position: absolute; top: 12px; right: 12px; z-index: 2; width: 38px; height: 38px; border-radius: 50%; border: none; background: rgba(255, 255, 255, 0.92); color: #012169; font-size: 1.1rem; cursor: pointer; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2); }
.modal-portada { position: relative; height: 240px; background: var(--color); }
.modal-portada img { width: 100%; height: 100%; object-fit: cover; display: block; }
.modal-portada .icono-portada { font-size: 5rem; right: 34px; bottom: 22px; }
.modal-cuerpo { padding: 24px 32px 32px; }
.etiquetas { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.modal .pastilla-estado { background: #012169; }
.modal h2 { color: #012169; font-size: 1.6rem; margin: 12px 0 14px; }
.ficha { display: grid; grid-template-columns: auto 1fr; gap: 6px 16px; margin: 0 0 18px; padding: 14px 16px; background: #f4f7f9; border-radius: 8px; border-left: 4px solid var(--color); font-size: 0.92rem; }
.ficha dt { font-weight: bold; color: #012169; }
.ficha dd { margin: 0; color: #333; }
.contenido-html { font-size: 0.97rem; color: #333; line-height: 1.65; }
.contenido-html :deep(img) { max-width: 100%; height: auto; border-radius: 8px; margin: 15px 0; display: block; }
.contenido-html :deep(p) { margin: 0 0 12px; }
.contenido-html :deep(ul), .contenido-html :deep(ol) { margin: 0 0 12px 20px; }
.contenido-html :deep(a) { color: #0086c0; }
.btn-web-proyecto { display: inline-block; margin-top: 10px; background: #012169; color: white; text-decoration: none; font-weight: bold; padding: 10px 18px; border-radius: 6px; }
.btn-web-proyecto:hover { background: #0086c0; }

@media (max-width: 992px) {
  .estadisticas { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 768px) {
  .contenido-hub { padding-top: 150px; }
  .titulo-seccion { font-size: 1.8rem; }
  .subtitulo { font-size: 1rem; margin-bottom: 18px; }
  /* Al mòbil, els comptadors en una fila que es pot lliscar */
  .estadisticas { display: flex; overflow-x: auto; gap: 8px; padding-bottom: 4px; scrollbar-width: none; }
  .estadisticas::-webkit-scrollbar { display: none; }
  .estadistica { flex: 0 0 auto; padding: 10px 14px; }
  .cifra { font-size: 1.5rem; }
  .barra-filtros { margin: 14px 0 20px; }
  .chips { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; width: 100%; padding-bottom: 2px; }
  .chips::-webkit-scrollbar { display: none; }
  .chip { flex: 0 0 auto; }
  .buscador { flex: 1 1 100%; }
  .grid-proyectos { grid-template-columns: 1fr; gap: 18px; }
  .modal-fondo { padding: 12px; }
  .modal-portada { height: 180px; }
  .modal-cuerpo { padding: 18px 18px 24px; }
  .modal h2 { font-size: 1.35rem; }
}
</style>
