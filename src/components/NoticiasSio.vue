<script setup>
import { computed } from 'vue'
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


      <div class="grid-noticias">
        <div v-for="(noticia, i) in noticias" :key="noticia.fecha" class="tarjeta-noticia">
          <div class="contenedor-imagen-noticia">
            <a v-if="noticia.ampliada" :href="noticia.ampliada" target="_blank" rel="noopener">
              <img :src="noticia.imagen" :alt="$t(`noticias.lista[${i}].alt`)" loading="lazy">
            </a>
            <img v-else :src="noticia.imagen" :alt="$t(`noticias.lista[${i}].alt`)" loading="lazy">
          </div>
          <div class="fecha-noticia"><time :datetime="noticia.fecha">{{ formatoFecha(noticia.fecha) }}</time></div>
          <h3>{{ $t(`noticias.lista[${i}].titulo`) }}</h3>
          <p class="texto-noticia">{{ $t(`noticias.lista[${i}].texto`) }}</p>
          <video v-if="noticia.videoLocal" class="video-noticia" :src="noticia.videoLocal" controls preload="metadata" playsinline
            :aria-label="$t(`noticias.lista[${i}].videoLocal`)" :title="$t(`noticias.lista[${i}].videoLocal`)"></video>
          <div v-if="noticia.enlace || noticia.video" class="enlaces-noticia">
            <a v-if="noticia.enlace" :href="noticia.enlace" target="_blank" rel="noopener" class="enlace-noticia">{{ $t(`noticias.lista[${i}].enlace`) }} ↗</a>
            <a v-if="noticia.video" :href="noticia.video" target="_blank" rel="noopener" class="enlace-noticia">▶ {{ $t(`noticias.lista[${i}].video`) }}</a>
          </div>
          <div v-if="noticia.galeria" class="galeria-noticia">
            <a v-for="(foto, j) in noticia.galeria" :key="foto" :href="foto" target="_blank" rel="noopener">
              <img :src="foto" :alt="$t(`noticias.lista[${i}].fotos[${j}]`)" loading="lazy">
            </a>
          </div>
        </div>
      </div>
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

/* GRID DE NOTICIAS */
.grid-noticias { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 30px; margin-top: 20px; }
.tarjeta-noticia { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.08); display: flex; flex-direction: column; position: relative; border-top: 4px solid #012169; padding: 0 0 30px 0; transition: transform 0.3s ease, box-shadow 0.3s ease; }
.tarjeta-noticia:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.12); }

/* 🖼️ CONTENEDOR DE LA IMAGEN DE LA NOTICIA */
.contenedor-imagen-noticia { width: 100%; height: 180px; background-color: #e9ecef; overflow: hidden; }
.contenedor-imagen-noticia img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }
.tarjeta-noticia:hover .contenedor-imagen-noticia img { transform: scale(1.08); }

/* TEXTOS INTERNOS */
.fecha-noticia { color: #8cc63f; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; padding: 25px 30px 5px 30px; }
.tarjeta-noticia h3 { color: #012169; font-size: 1.25rem; margin: 0 0 15px 0; padding: 0 30px; line-height: 1.4; }
.texto-noticia { color: #555; font-size: 0.95rem; line-height: 1.6; padding: 0 30px; margin: 0; }
/* El vídeo pren la seva forma (p. ex. vertical, de mòbil), centrat i sense franges negres als costats */
.video-noticia { display: block; width: auto; height: auto; max-width: calc(100% - 60px); max-height: 460px; margin: 16px auto 0; border-radius: 8px; }
.enlaces-noticia { display: flex; flex-wrap: wrap; gap: 10px; margin: 16px 30px 0; }
.enlace-noticia { background: #012169; color: white; text-decoration: none; font-weight: bold; font-size: 0.9rem; padding: 9px 16px; border-radius: 6px; transition: background 0.2s; }
.enlace-noticia:hover { background: #0086c0; }
.galeria-noticia { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding: 18px 30px 0; }
.galeria-noticia img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 6px; display: block; transition: opacity 0.2s; }
.galeria-noticia a:hover img { opacity: 0.85; }

@media (max-width: 768px) { .contenido-noticias { padding-top: 150px; } .grid-noticias { grid-template-columns: 1fr; } }
</style>