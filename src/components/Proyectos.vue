<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { limpiarHtml } from '../utils/limpiarHtml'

// Projectes i campanyes en carrusel: cada projecte ocupa tota l'amplada amb la seva imatge.
// Fletxes, lliscar (mòbil), tecles ← → i miniatures per saltar. «Llegir més» obre el projecte
// sencer a pantalla completa, amb les seves fotos també en carrusel.
const { t } = useI18n()
const proyectos = ref([])
const cargando = ref(true)
const errorCarga = ref(false)

// Estat guardat a la base de dades -> grup (en aquest ordre)
const GRUPO_POR_ESTADO = { 'En Curs': 'enCurso', 'Aprovat': 'aprobados', 'Sol·licitat': 'solicitados', 'Finalitzat': 'finalizados' }
const GRUPOS = ['enCurso', 'aprobados', 'solicitados', 'finalizados']
const grupoDe = (p) => GRUPO_POR_ESTADO[p.estado] || 'enCurso'

// Categoria -> clau de traducció, color i icona (per als projectes sense foto)
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
const categoria = (p) => CATEGORIAS[p?.categoria] || { clave: null, color: '#4a5a70', icono: '🌊' }
const nombreCategoria = (p) => categoria(p).clave ? t(`proyectos.categorias.${categoria(p).clave}`) : (p?.categoria || '')

// Fotos d'un projecte: la portada triada a la intranet i les de la descripció ampliada
const fotosDe = (p) => {
  const html = limpiarHtml(p?.descripcion_ampliada || '')
  const delTexto = [...html.matchAll(/<img[^>]+src="([^"]+)"/gi)].map(m => m[1])
  return [...new Set([p?.imagen, ...delTexto].filter(Boolean))]
}
const portada = (p) => fotosDe(p)[0] || ''
// Descripció ampliada sense les fotos (es mostren a part, al carrusel de la finestra)
const textoAmpliado = (p) => limpiarHtml(p?.descripcion_ampliada || '').replace(/<p>\s*(<img[^>]*>\s*)+<\/p>/gi, '').replace(/<img[^>]*>/gi, '')
const tieneTexto = (html) => html.replace(/<[^>]+>/g, '').trim().length > 0

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

// ---------- FILTRE PER ESTAT ----------
const grupoActivo = ref('todos')
const cuenta = (g) => proyectos.value.filter(p => grupoDe(p) === g).length
// Primer els que tenen foto (llueixen més) dins de cada estat; després per títol
const lista = computed(() => proyectos.value
  .filter(p => grupoActivo.value === 'todos' || grupoDe(p) === grupoActivo.value)
  .sort((a, b) => GRUPOS.indexOf(grupoDe(a)) - GRUPOS.indexOf(grupoDe(b))
    || (portada(b) ? 1 : 0) - (portada(a) ? 1 : 0) || a.titulo.localeCompare(b.titulo)))

// ---------- CARRUSEL ----------
const actual = ref(0)
const direccion = ref(1) // 1 = endavant, -1 = enrere (per a l'animació)
const proyecto = computed(() => lista.value[actual.value])
watch(grupoActivo, () => { actual.value = 0 })
const ir = (i) => {
  const n = lista.value.length
  if (!n) return
  direccion.value = i > actual.value ? 1 : -1
  actual.value = (i + n) % n
}
const siguiente = () => { direccion.value = 1; actual.value = (actual.value + 1) % lista.value.length }
const anterior = () => { direccion.value = -1; actual.value = (actual.value - 1 + lista.value.length) % lista.value.length }

// Lliscar amb el dit
let inicioX = null
const tocarInicio = (e) => { inicioX = e.touches[0].clientX }
const tocarFin = (e) => {
  if (inicioX === null) return
  const dx = e.changedTouches[0].clientX - inicioX
  if (Math.abs(dx) > 50) (dx < 0 ? siguiente : anterior)()
  inicioX = null
}

// Miniatures: la seleccionada sempre a la vista
const tira = ref(null)
watch(actual, () => {
  // Només desplaça la tira de costat (scrollIntoView també mouria la pàgina amunt o avall)
  const el = tira.value?.children[actual.value]
  if (el) tira.value.scrollTo({ left: el.offsetLeft - (tira.value.clientWidth - el.clientWidth) / 2, behavior: 'smooth' })
})

// ---------- FINESTRA «LLEGIR MÉS» ----------
const abierto = ref(false)
const fotoActual = ref(0)
const abrir = () => { fotoActual.value = 0; abierto.value = true }
watch(abierto, (v) => { document.body.style.overflow = v ? 'hidden' : '' })

const alPulsarTecla = (e) => {
  if (e.target.closest?.('input, textarea')) return
  if (abierto.value) {
    const n = fotosDe(proyecto.value).length
    if (e.key === 'Escape') abierto.value = false
    else if (e.key === 'ArrowRight' && n > 1) fotoActual.value = (fotoActual.value + 1) % n
    else if (e.key === 'ArrowLeft' && n > 1) fotoActual.value = (fotoActual.value - 1 + n) % n
  } else if (lista.value.length > 1) {
    if (e.key === 'ArrowRight') siguiente()
    else if (e.key === 'ArrowLeft') anterior()
  }
}
onMounted(() => { cargarProyectos(); window.addEventListener('keydown', alPulsarTecla) })
onBeforeUnmount(() => { document.body.style.overflow = ''; window.removeEventListener('keydown', alPulsarTecla) })
</script>

<template>
  <div class="proyectos-page">
    <!-- Capçalera: títol i pestanyes d'estat -->
    <div class="cabecera-proyectos">
      <div class="contenedor-ancho">
        <h1 class="titulo-seccion">{{ $t('proyectos.titulo') }}</h1>
        <p class="subtitulo">{{ $t('proyectos.subtitulo') }}</p>
        <div class="pestanas" role="group" :aria-label="$t('proyectos.estado')">
          <button type="button" class="pestana" :class="{ activa: grupoActivo === 'todos' }" :aria-pressed="grupoActivo === 'todos'" @click="grupoActivo = 'todos'">
            {{ $t('proyectos.todos') }} <b>{{ proyectos.length }}</b>
          </button>
          <button v-for="g in GRUPOS" :key="g" type="button" class="pestana" :class="['estado-' + g, { activa: grupoActivo === g }]"
            :aria-pressed="grupoActivo === g" :disabled="!cuenta(g)" @click="grupoActivo = g">
            <i class="punto" aria-hidden="true"></i>{{ $t(`proyectos.grupos.${g}.titulo`) }} <b>{{ cuenta(g) }}</b>
          </button>
        </div>
      </div>
    </div>

    <p v-if="cargando" class="contenedor-ancho aviso-lista">{{ $t('proyectos.cargando') }}</p>
    <p v-else-if="errorCarga" class="contenedor-ancho aviso-lista">{{ $t('proyectos.errorCarga') }}</p>

    <!-- Carrusel: un projecte a tota l'amplada -->
    <section v-else-if="proyecto" class="carrusel" :aria-roledescription="$t('proyectos.carrusel')" :aria-label="$t('proyectos.titulo')"
      @touchstart.passive="tocarInicio" @touchend="tocarFin">
      <Transition :name="direccion > 0 ? 'desliza-izq' : 'desliza-der'">
        <article :key="proyecto.id" class="diapositiva" :style="{ '--color': categoria(proyecto).color }"
          :aria-label="`${actual + 1} / ${lista.length}: ${proyecto.titulo}`">
          <div class="fondo" :class="{ 'sin-foto': !portada(proyecto) }">
            <img v-if="portada(proyecto)" :src="portada(proyecto)" alt="">
            <span v-else class="icono-fondo" aria-hidden="true">{{ categoria(proyecto).icono }}</span>
          </div>
          <div class="contenedor-ancho texto-diapositiva">
            <div class="etiquetas">
              <span class="pastilla-estado" :class="'estado-' + grupoDe(proyecto)"><i class="punto" aria-hidden="true"></i>{{ $t(`proyectos.grupos.${grupoDe(proyecto)}.titulo`) }}</span>
              <span class="pastilla-tipo">{{ categoria(proyecto).icono }} {{ nombreCategoria(proyecto) }}</span>
            </div>
            <h2 class="titulo-proyecto">{{ proyecto.titulo }}</h2>
            <p class="resumen">{{ proyecto.descripcion_corta }}</p>
            <ul class="personas">
              <li v-if="proyecto.investigador_principal"><span class="rol">{{ $t('proyectos.ip') }}</span> {{ proyecto.investigador_principal }}</li>
              <li v-if="proyecto.pit"><span class="rol">{{ $t('proyectos.pit') }}</span> {{ proyecto.pit }}</li>
            </ul>
            <div class="acciones">
              <button type="button" class="btn-leer" @click="abrir">{{ $t('proyectos.verMas') }} →</button>
              <span class="contador">{{ actual + 1 }} / {{ lista.length }}</span>
            </div>
          </div>
        </article>
      </Transition>
      <template v-if="lista.length > 1">
        <button type="button" class="flecha izq" @click="anterior" :aria-label="$t('proyectos.anterior')">‹</button>
        <button type="button" class="flecha der" @click="siguiente" :aria-label="$t('proyectos.siguiente')">›</button>
      </template>
    </section>

    <!-- Miniatures de tots els projectes -->
    <div v-if="lista.length > 1" class="contenedor-ancho">
      <ol ref="tira" class="miniaturas">
        <li v-for="(p, i) in lista" :key="p.id">
          <button type="button" class="miniatura" :class="{ activa: i === actual }" :aria-current="i === actual ? 'true' : null"
            :style="{ '--color': categoria(p).color }" @click="ir(i)">
            <span class="mini-imagen" :class="{ 'sin-foto': !portada(p) }">
              <img v-if="portada(p)" :src="portada(p)" alt="" loading="lazy">
              <span v-else aria-hidden="true">{{ categoria(p).icono }}</span>
            </span>
            <span class="mini-texto">
              <span class="mini-titulo">{{ p.titulo }}</span>
              <span class="mini-estado" :class="'estado-' + grupoDe(p)"><i class="punto" aria-hidden="true"></i>{{ $t(`proyectos.grupos.${grupoDe(p)}.titulo`) }}</span>
            </span>
          </button>
        </li>
      </ol>
    </div>

    <!-- Projecte sencer a pantalla completa -->
    <div v-if="abierto && proyecto" class="modal-fondo" @click.self="abierto = false">
      <article class="modal" role="dialog" aria-modal="true" aria-labelledby="titulo-modal" :style="{ '--color': categoria(proyecto).color }">
        <button type="button" class="modal-cerrar" @click="abierto = false" :aria-label="$t('proyectos.cerrar')">✕</button>
        <div class="galeria" :class="{ 'sin-foto': !fotosDe(proyecto).length }">
          <img v-if="fotosDe(proyecto).length" :key="fotoActual" :src="fotosDe(proyecto)[fotoActual]" alt="" class="foto-galeria">
          <span v-else class="icono-fondo" aria-hidden="true">{{ categoria(proyecto).icono }}</span>
          <template v-if="fotosDe(proyecto).length > 1">
            <button type="button" class="flecha izq" @click="fotoActual = (fotoActual - 1 + fotosDe(proyecto).length) % fotosDe(proyecto).length" :aria-label="$t('proyectos.anterior')">‹</button>
            <button type="button" class="flecha der" @click="fotoActual = (fotoActual + 1) % fotosDe(proyecto).length" :aria-label="$t('proyectos.siguiente')">›</button>
            <div class="puntos">
              <button v-for="(f, i) in fotosDe(proyecto)" :key="f" type="button" :class="{ activo: i === fotoActual }" @click="fotoActual = i" :aria-label="`${i + 1}`"></button>
            </div>
          </template>
        </div>
        <div class="modal-cuerpo">
          <div class="etiquetas">
            <span class="pastilla-estado oscura" :class="'estado-' + grupoDe(proyecto)"><i class="punto" aria-hidden="true"></i>{{ $t(`proyectos.grupos.${grupoDe(proyecto)}.titulo`) }}</span>
            <span class="pastilla-tipo clara">{{ nombreCategoria(proyecto) }}</span>
          </div>
          <h2 id="titulo-modal">{{ proyecto.titulo }}</h2>
          <dl v-if="proyecto.investigador_principal || proyecto.pit" class="ficha">
            <template v-if="proyecto.investigador_principal"><dt>{{ $t('proyectos.ip') }}</dt><dd>{{ proyecto.investigador_principal }}</dd></template>
            <template v-if="proyecto.pit"><dt>{{ $t('proyectos.pit') }}</dt><dd>{{ proyecto.pit }}</dd></template>
          </dl>
          <div v-if="tieneTexto(textoAmpliado(proyecto))" class="contenido-html" v-html="textoAmpliado(proyecto)"></div>
          <p v-else class="contenido-html">{{ proyecto.descripcion_corta }}</p>
          <a v-if="proyecto.wiki_url" :href="proyecto.wiki_url" target="_blank" rel="noopener" class="btn-web-proyecto">{{ $t('proyectos.web') }} ↗</a>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.proyectos-page { min-height: 100vh; padding-bottom: 70px; background: #f4f7f9; }
.aviso-lista { color: #555; font-style: italic; padding: 30px 15px; }

/* Capçalera */
.cabecera-proyectos { background: linear-gradient(rgba(1, 33, 105, 0.75), rgba(1, 33, 105, 0.92)), url('/pecesaguasalada.webp') center / cover; padding: 120px 0 22px; }
.titulo-seccion { color: white; font-size: 2.2rem; margin: 0 0 12px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.05rem; margin: 0 0 18px; max-width: 800px; }
.pestanas { display: flex; flex-wrap: wrap; gap: 8px; }
.pestana { padding: 7px 14px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.4); background: rgba(255, 255, 255, 0.08); color: white; font: inherit; font-size: 0.88rem; cursor: pointer; }
.pestana b { margin-left: 4px; opacity: 0.8; }
.pestana:hover:not(:disabled) { background: rgba(255, 255, 255, 0.2); }
.pestana:disabled { opacity: 0.4; cursor: default; }
.pestana.activa { background: white; color: #012169; border-color: white; font-weight: bold; }

/* Colors dels estats */
.estado-enCurso { --estado: #8cc63f; }
.estado-aprobados { --estado: #3db2ff; }
.estado-solicitados { --estado: #ffb020; }
.estado-finalizados { --estado: #aab4bf; }
.punto { display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: var(--estado, #fff); margin-right: 7px; vertical-align: 1px; flex-shrink: 0; }
.pastilla-estado.estado-enCurso .punto { animation: latido 2s infinite; }
@keyframes latido { 0% { box-shadow: 0 0 0 0 rgba(140, 198, 63, 0.7); } 70%, 100% { box-shadow: 0 0 0 7px rgba(140, 198, 63, 0); } }
@media (prefers-reduced-motion: reduce) { .punto { animation: none !important; } }

/* Carrusel */
.carrusel { position: relative; overflow: hidden; height: clamp(480px, 72vh, 680px); background: #012169; }
.diapositiva { position: absolute; inset: 0; display: flex; align-items: flex-end; }
.fondo { position: absolute; inset: 0; background: var(--color); }
.fondo img { width: 100%; height: 100%; object-fit: cover; animation: acercar 12s ease-out forwards; }
@keyframes acercar { from { transform: scale(1.06); } to { transform: scale(1); } }
.fondo::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, rgba(1, 16, 50, 0.95) 0%, rgba(1, 16, 50, 0.6) 40%, rgba(1, 16, 50, 0.05) 75%), linear-gradient(to right, rgba(1, 16, 50, 0.55), transparent 60%); }
.sin-foto { background: radial-gradient(circle at 80% 25%, rgba(255, 255, 255, 0.25), transparent 40%), linear-gradient(135deg, var(--color), #012169 75%); }
.sin-foto::before { content: ''; position: absolute; inset: 0; opacity: 0.14; background: repeating-radial-gradient(circle at 100% 0%, transparent 0 26px, rgba(255, 255, 255, 0.9) 27px 28px); }
.icono-fondo { position: absolute; right: 8%; top: 18%; font-size: clamp(6rem, 16vw, 11rem); line-height: 1; opacity: 0.9; filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.3)); }
.texto-diapositiva { position: relative; z-index: 1; width: 100%; padding-bottom: 46px; color: white; }
.etiquetas { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.pastilla-estado, .pastilla-tipo { display: inline-flex; align-items: center; padding: 6px 12px; border-radius: 20px; font-size: 0.82rem; font-weight: bold; }
.pastilla-estado { background: rgba(255, 255, 255, 0.16); backdrop-filter: blur(4px); color: white; }
.pastilla-tipo { background: var(--color); color: white; }
.titulo-proyecto { font-size: clamp(2rem, 4.5vw, 3.4rem); line-height: 1.1; margin: 16px 0 12px; max-width: 900px; text-shadow: 0 2px 16px rgba(0, 0, 0, 0.35); }
.resumen { font-size: 1.12rem; line-height: 1.55; max-width: 720px; margin: 0; color: #e8eef6; display: -webkit-box; -webkit-line-clamp: 3; line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.personas { list-style: none; padding: 0; margin: 14px 0 0; display: flex; flex-wrap: wrap; gap: 6px 24px; font-size: 0.92rem; color: #dbe4f0; max-width: 900px; }
.rol { display: block; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; color: #8cc63f; font-weight: bold; }
.acciones { display: flex; align-items: center; gap: 18px; margin-top: 22px; }
.btn-leer { background: #8cc63f; color: #012169; border: none; padding: 12px 24px; border-radius: 8px; font: inherit; font-weight: bold; font-size: 1rem; cursor: pointer; transition: background 0.2s, transform 0.2s; }
.btn-leer:hover { background: #a5d65f; transform: translateY(-2px); }
.contador { color: #b9c6d8; font-size: 0.9rem; letter-spacing: 1px; }
.flecha { position: absolute; top: 50%; transform: translateY(-50%); z-index: 2; width: 50px; height: 50px; border-radius: 50%; border: 1px solid rgba(255, 255, 255, 0.5);
  background: rgba(1, 16, 50, 0.4); color: white; font-size: 2rem; line-height: 1; cursor: pointer; backdrop-filter: blur(4px); transition: background 0.2s; }
.flecha:hover { background: rgba(255, 255, 255, 0.25); }
.flecha.izq { left: 18px; }
.flecha.der { right: 18px; }

/* Transicions entre diapositives */
.desliza-izq-enter-active, .desliza-izq-leave-active, .desliza-der-enter-active, .desliza-der-leave-active { transition: transform 0.55s ease, opacity 0.55s ease; }
.desliza-izq-enter-from { transform: translateX(8%); opacity: 0; }
.desliza-izq-leave-to { transform: translateX(-8%); opacity: 0; }
.desliza-der-enter-from { transform: translateX(-8%); opacity: 0; }
.desliza-der-leave-to { transform: translateX(8%); opacity: 0; }
@media (prefers-reduced-motion: reduce) {
  .desliza-izq-enter-active, .desliza-izq-leave-active, .desliza-der-enter-active, .desliza-der-leave-active { transition: opacity 0.2s; transform: none; }
  .fondo img { animation: none; }
}

/* Miniatures */
.miniaturas { position: relative; list-style: none; display: flex; gap: 12px; overflow-x: auto; padding: 18px 2px 8px; margin: 0; scroll-snap-type: x proximity; }
.miniatura { display: flex; flex-direction: column; width: 190px; padding: 0; border: 2px solid transparent; border-radius: 10px; overflow: hidden; background: white; cursor: pointer;
  font: inherit; text-align: left; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); scroll-snap-align: center; transition: transform 0.2s, border-color 0.2s; }
.miniatura:hover { transform: translateY(-3px); }
.miniatura.activa { border-color: #8cc63f; box-shadow: 0 6px 18px rgba(1, 33, 105, 0.2); }
.mini-imagen { position: relative; display: flex; width: 100%; align-self: stretch; align-items: center; justify-content: center; height: 96px; background: var(--color); color: white; font-size: 2.2rem; overflow: hidden; }
.mini-imagen img { width: 100%; height: 100%; object-fit: cover; }
.mini-texto { display: flex; flex-direction: column; gap: 4px; padding: 8px 10px 10px; }
.mini-titulo { color: #012169; font-weight: bold; font-size: 0.86rem; line-height: 1.25; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.5em; }
.mini-estado { color: #666; font-size: 0.75rem; }

/* Finestra «Llegir més» */
.modal-fondo { position: fixed; inset: 0; z-index: 1000; background: rgba(1, 16, 50, 0.82); display: flex; align-items: flex-start; justify-content: center; padding: 30px 16px; overflow-y: auto; }
.modal { position: relative; width: 100%; max-width: 980px; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 24px 60px rgba(0, 0, 0, 0.4); }
.modal-cerrar { position: absolute; top: 14px; right: 14px; z-index: 3; width: 40px; height: 40px; border-radius: 50%; border: none; background: rgba(255, 255, 255, 0.92); color: #012169; font-size: 1.1rem; cursor: pointer; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25); }
.galeria { position: relative; height: clamp(260px, 52vh, 520px); background: #0a1630; }
.foto-galeria { width: 100%; height: 100%; object-fit: contain; display: block; animation: aparecer 0.35s ease; }
@keyframes aparecer { from { opacity: 0; } to { opacity: 1; } }
.galeria .flecha { width: 44px; height: 44px; font-size: 1.7rem; }
.puntos { position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px; }
.puntos button { width: 10px; height: 10px; border-radius: 50%; border: 2px solid white; background: transparent; padding: 0; cursor: pointer; }
.puntos button.activo { background: white; }
.modal-cuerpo { padding: 24px 36px 36px; }
.pastilla-estado.oscura { background: #012169; }
.pastilla-tipo.clara { background: color-mix(in srgb, var(--color) 14%, white); color: var(--color); }
.modal h2 { color: #012169; font-size: 1.9rem; margin: 12px 0 16px; }
.ficha { display: grid; grid-template-columns: auto 1fr; gap: 6px 18px; margin: 0 0 20px; padding: 14px 18px; background: #f4f7f9; border-radius: 8px; border-left: 4px solid var(--color); font-size: 0.94rem; }
.ficha dt { font-weight: bold; color: #012169; }
.ficha dd { margin: 0; color: #333; }
.contenido-html { font-size: 1rem; color: #333; line-height: 1.7; }
.contenido-html :deep(p) { margin: 0 0 12px; }
.contenido-html :deep(ul), .contenido-html :deep(ol) { margin: 0 0 12px 20px; }
.contenido-html :deep(a) { color: #0086c0; }
.btn-web-proyecto { display: inline-block; margin-top: 12px; background: #012169; color: white; text-decoration: none; font-weight: bold; padding: 11px 20px; border-radius: 8px; }
.btn-web-proyecto:hover { background: #0086c0; }

@media (max-width: 768px) {
  .cabecera-proyectos { padding: 150px 0 16px; }
  .titulo-seccion { font-size: 1.8rem; }
  .subtitulo { font-size: 0.98rem; margin-bottom: 14px; }
  .pestanas { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; padding-bottom: 2px; }
  .pestanas::-webkit-scrollbar { display: none; }
  .pestana { flex: 0 0 auto; }
  .carrusel { height: clamp(520px, 82vh, 640px); }
  .texto-diapositiva { padding-bottom: 28px; }
  .resumen { font-size: 1rem; -webkit-line-clamp: 4; line-clamp: 4; }
  .personas { flex-direction: column; gap: 8px; }
  .flecha { top: 34%; width: 42px; height: 42px; font-size: 1.6rem; }
  .flecha.izq { left: 10px; }
  .flecha.der { right: 10px; }
  .icono-fondo { top: 12%; }
  .miniatura { width: 150px; }
  .mini-imagen { height: 80px; }
  .modal-fondo { padding: 0; }
  .modal { border-radius: 0; min-height: 100vh; }
  .galeria { height: 46vh; }
  .modal-cuerpo { padding: 18px 18px 30px; }
  .modal h2 { font-size: 1.45rem; }
}
</style>
