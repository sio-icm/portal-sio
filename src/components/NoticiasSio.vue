<script setup>
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
const fondoNoticias = '/instrumentacion.webp'

const { locale } = useI18n()

// Fecha y foto de cada noticia (título, texto y descripción de las fotos: noticias.lista en src/i18n,
// en el mismo orden). «ampliada» = foto entera al pulsar; «galeria» = fotos pequeñas debajo del texto;
// «enlace» = botón a una web externa (su texto: noticias.lista[i].enlace);
// «video» = botón a un vídeo externo (su texto: noticias.lista[i].video);
// «videoLocal» = vídeo propio (.mp4 en public/fotos/noticias) que se ve en la misma noticia
// (su descripción: noticias.lista[i].videoLocal).
const noticias = [
  {
    fecha: '2026-11-12', imagen: '/fotos/noticias/sacoso-cami-portada.webp', ampliada: '/fotos/noticias/sacoso-cami.webp',
    galeria: ['/fotos/noticias/sacoso-palets.webp', '/fotos/noticias/sacoso-equip.webp',
      '/fotos/noticias/sacoso-hesperides.webp', '/fotos/noticias/sacoso-fondejos.webp', '/fotos/noticias/sacoso-roseta.webp',
      '/fotos/noticias/sacoso-argo.webp', '/fotos/noticias/sacoso-instruments.webp', '/fotos/noticias/sacoso-iceberg.webp'],
    videoLocal: '/fotos/noticias/sacoso-video.mp4',
    enlace: 'https://saco-so.icm.csic.es/ca/campanyes/sacoso27',
    video: 'https://www.instagram.com/reel/DGqq7iOs9Mx/'
  },
  {
    fecha: '2026-10-26', imagen: '/fotos/noticias/fnob-portada.webp', ampliada: '/fotos/noticias/fnob-cubierta.webp',
    galeria: ['/fotos/noticias/fnob-muestreador.webp', '/fotos/noticias/fnob-muestras.webp', '/fotos/noticias/fnob-equipo.webp']
  },
  {
    fecha: '2026-10-09', imagen: '/fotos/noticias/donana-portada.webp', ampliada: '/fotos/noticias/donana-playa.webp',
    galeria: ['/fotos/noticias/donana-drones.webp', '/fotos/noticias/donana-lidar.webp', '/fotos/noticias/donana-hexacoptero.webp',
      '/fotos/noticias/donana-estacion.webp', '/fotos/noticias/donana-ciervo.webp', '/fotos/noticias/donana-caballos.webp']
  },
  {
    fecha: '2026-08-11', imagen: '/fotos/noticias/somorrostro-portada.webp', ampliada: '/fotos/noticias/somorrostro-boia.webp',
    galeria: ['/fotos/noticias/somorrostro-grua.webp', '/fotos/noticias/somorrostro-fondeig.webp', '/fotos/noticias/somorrostro-zodiac.webp'],
    enlace: 'https://www.icatmar.cat/boiasomorrostro/#SECTION=observations&TIMESCALE=1h&PANEL=compact'
  }
]

const formatoFecha = (iso) => {
  const [a, m, d] = iso.split('-').map(Number)
  return new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' })
    .format(new Date(a, m - 1, d)).toUpperCase()
}

// Notícia oberta a la finestra «Llegir més» (índex dins de «noticias»), o null
const abierta = ref(null)
const abrir = (i) => { abierta.value = i }
const cerrar = () => { abierta.value = null }
const alPulsarTecla = (e) => { if (e.key === 'Escape') cerrar() }
watch(abierta, (i) => {
  // Mentre la finestra és oberta, la pàgina de sota no es desplaça i Esc la tanca
  document.body.style.overflow = i === null ? '' : 'hidden'
  if (i === null) window.removeEventListener('keydown', alPulsarTecla)
  else window.addEventListener('keydown', alPulsarTecla)
})
onBeforeUnmount(() => { document.body.style.overflow = ''; window.removeEventListener('keydown', alPulsarTecla) })

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('${fondoNoticias}')`
})
</script>

<template>
  <div class="noticias-page">
    <div class="fondo-noticias"></div>

    <div class="contenedor-ancho contenido-noticias">
      <h1 class="titulo-seccion">{{ $t('noticias.titulo') }}</h1>
      <p class="subtitulo">{{ $t('noticias.subtitulo') }}</p>


      <!-- Totes les fitxes fan la mateixa alçada: foto, data, títol (2 línies), resum (4 línies) i «Llegir més» -->
      <div class="grid-noticias">
        <article v-for="(noticia, i) in noticias" :key="noticia.fecha" class="tarjeta-noticia">
          <button type="button" class="contenedor-imagen-noticia" @click="abrir(i)" :aria-label="$t('noticias.leerMas') + ': ' + $t(`noticias.lista[${i}].titulo`)">
            <img :src="noticia.imagen" :alt="$t(`noticias.lista[${i}].alt`)" loading="lazy">
          </button>
          <div class="fecha-noticia"><time :datetime="noticia.fecha">{{ formatoFecha(noticia.fecha) }}</time></div>
          <h3>{{ $t(`noticias.lista[${i}].titulo`) }}</h3>
          <p class="texto-noticia resumen">{{ $t(`noticias.lista[${i}].texto`) }}</p>
          <button type="button" class="leer-mas" @click="abrir(i)">{{ $t('noticias.leerMas') }} →</button>
        </article>
      </div>
    </div>

    <!-- Finestra amb la notícia sencera -->
    <div v-if="abierta !== null" class="modal-fondo" @click.self="cerrar">
      <article class="modal-noticia" role="dialog" aria-modal="true" :aria-labelledby="'titulo-noticia-' + abierta">
        <button type="button" class="modal-cerrar" @click="cerrar" :aria-label="$t('noticias.cerrar')">✕</button>
        <a v-if="noticias[abierta].ampliada" :href="noticias[abierta].ampliada" target="_blank" rel="noopener" class="modal-imagen">
          <img :src="noticias[abierta].imagen" :alt="$t(`noticias.lista[${abierta}].alt`)">
        </a>
        <div v-else class="modal-imagen"><img :src="noticias[abierta].imagen" :alt="$t(`noticias.lista[${abierta}].alt`)"></div>
        <div class="fecha-noticia"><time :datetime="noticias[abierta].fecha">{{ formatoFecha(noticias[abierta].fecha) }}</time></div>
        <h3 :id="'titulo-noticia-' + abierta">{{ $t(`noticias.lista[${abierta}].titulo`) }}</h3>
        <p class="texto-noticia">{{ $t(`noticias.lista[${abierta}].texto`) }}</p>
        <video v-if="noticias[abierta].videoLocal" class="video-noticia" :src="noticias[abierta].videoLocal" controls preload="metadata" playsinline
          :aria-label="$t(`noticias.lista[${abierta}].videoLocal`)" :title="$t(`noticias.lista[${abierta}].videoLocal`)"></video>
        <div v-if="noticias[abierta].enlace || noticias[abierta].video || noticias[abierta].enlaces" class="enlaces-noticia">
          <a v-if="noticias[abierta].enlace" :href="noticias[abierta].enlace" target="_blank" rel="noopener" class="enlace-noticia">{{ $t(`noticias.lista[${abierta}].enlace`) }} ↗</a>
          <a v-if="noticias[abierta].video" :href="noticias[abierta].video" target="_blank" rel="noopener" class="enlace-noticia">▶ {{ $t(`noticias.lista[${abierta}].video`) }}</a>
        </div>
        <div v-if="noticias[abierta].galeria" class="galeria-noticia">
          <a v-for="(foto, j) in noticias[abierta].galeria" :key="foto" :href="foto" target="_blank" rel="noopener">
            <img :src="foto" :alt="$t(`noticias.lista[${abierta}].fotos[${j}]`)" loading="lazy">
          </a>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.noticias-page { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-noticias { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-image: linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('/instrumentacion.webp'); background-size: cover; background-position: center; z-index: 0; }
.contenido-noticias { position: relative; z-index: 10; padding-top: 120px; }
.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 40px; max-width: 800px; }

/* GRID DE NOTICIAS: fitxes iguals */
.grid-noticias { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px; margin-top: 20px; align-items: start; }
.tarjeta-noticia { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.08); display: flex; flex-direction: column; border-top: 4px solid #012169; padding: 0 0 24px 0; transition: transform 0.3s ease, box-shadow 0.3s ease; }
.tarjeta-noticia:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.12); }

/* 🖼️ IMATGE */
.contenedor-imagen-noticia { display: block; width: 100%; height: 180px; padding: 0; border: none; background-color: #e9ecef; overflow: hidden; cursor: pointer; }
.contenedor-imagen-noticia img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }
.tarjeta-noticia:hover .contenedor-imagen-noticia img { transform: scale(1.08); }

/* TEXTOS */
.fecha-noticia { color: #8cc63f; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; padding: 25px 30px 5px 30px; }
.tarjeta-noticia h3, .modal-noticia h3 { color: #012169; font-size: 1.25rem; margin: 0 0 12px 0; padding: 0 30px; line-height: 1.4; }
/* Títol de la fitxa: sempre 2 línies d'alt (si és més llarg, «…») */
.tarjeta-noticia h3 { display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: calc(1.25rem * 1.4 * 2); }
.texto-noticia { color: #555; font-size: 0.95rem; line-height: 1.6; padding: 0 30px; margin: 0; white-space: pre-line; }
/* Resum de la fitxa: sempre 4 línies d'alt */
.texto-noticia.resumen { display: -webkit-box; -webkit-line-clamp: 4; line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; height: calc(0.95rem * 1.6 * 4); white-space: normal; }
.leer-mas { align-self: flex-start; margin: 16px 30px 0; background: none; border: none; padding: 0; color: #0086c0; font-weight: bold; font-size: 0.95rem; cursor: pointer; }
.leer-mas:hover { color: #012169; text-decoration: underline; }

/* FINESTRA «LLEGIR MÉS» */
.modal-fondo { position: fixed; inset: 0; z-index: 1000; background: rgba(1, 20, 60, 0.7); display: flex; align-items: flex-start; justify-content: center; padding: 40px 16px; overflow-y: auto; }
.modal-noticia { position: relative; width: 100%; max-width: 760px; background: white; border-radius: 12px; border-top: 4px solid #012169; padding: 0 0 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.3); }
.modal-cerrar { position: absolute; top: 10px; right: 10px; z-index: 2; width: 36px; height: 36px; border-radius: 50%; border: none; background: rgba(255,255,255,0.92); color: #012169; font-size: 1.1rem; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.modal-cerrar:hover { background: white; }
.modal-imagen { display: block; width: 100%; max-height: 380px; overflow: hidden; background: #e9ecef; border-radius: 8px 8px 0 0; }
.modal-imagen img { display: block; width: 100%; max-height: 380px; object-fit: cover; }
/* El vídeo pren la seva forma (p. ex. vertical, de mòbil), centrat i sense franges negres als costats */
.video-noticia { display: block; width: auto; height: auto; max-width: calc(100% - 60px); max-height: 460px; margin: 18px auto 0; border-radius: 8px; }
.enlaces-noticia { display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 30px 0; }
.enlace-noticia { background: #012169; color: white; text-decoration: none; font-weight: bold; font-size: 0.9rem; padding: 9px 16px; border-radius: 6px; transition: background 0.2s; }
.enlace-noticia:hover { background: #0086c0; }
.galeria-noticia { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding: 18px 30px 0; }
.galeria-noticia img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 6px; display: block; transition: opacity 0.2s; }
.galeria-noticia a:hover img { opacity: 0.85; }

@media (max-width: 768px) {
  .contenido-noticias { padding-top: 150px; }
  .grid-noticias { grid-template-columns: 1fr; }
  .modal-fondo { padding: 12px; }
  .tarjeta-noticia h3, .modal-noticia h3, .texto-noticia, .fecha-noticia { padding-left: 18px; padding-right: 18px; }
  .leer-mas, .enlaces-noticia { margin-left: 18px; margin-right: 18px; }
  .galeria-noticia { padding: 14px 18px 0; }
  .video-noticia { max-width: calc(100% - 36px); }
}
</style>