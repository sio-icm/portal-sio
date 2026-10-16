<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import fondoNoticias from '../assets/instrumentacion.jpg'

const { locale } = useI18n()

// Fecha y foto de cada noticia (título, texto y descripción de la foto: noticias.lista en src/i18n)
const noticias = [
  { fecha: '2026-08-19', imagen: '/fotos/noticias/vehiculos-superficie.webp' },
  { fecha: '2026-07-10', imagen: '/fotos/noticias/impresion-3d.webp' },
  { fecha: '2026-06-28', imagen: '/fotos/noticias/boya-fondeo.webp' }
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
            <img :src="noticia.imagen" :alt="$t(`noticias.lista[${i}].alt`)" loading="lazy">
          </div>
          <div class="fecha-noticia"><time :datetime="noticia.fecha">{{ formatoFecha(noticia.fecha) }}</time></div>
          <h3>{{ $t(`noticias.lista[${i}].titulo`) }}</h3>
          <p class="texto-noticia">{{ $t(`noticias.lista[${i}].texto`) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.noticias-page { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-noticias { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-image: linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('/instrumentacion.jpg'); background-size: cover; background-position: center; z-index: 0; }
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

@media (max-width: 768px) { .contenido-noticias { padding-top: 150px; } .grid-noticias { grid-template-columns: 1fr; } }
</style>