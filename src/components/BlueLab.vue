<script setup>
import { computed } from 'vue'
import portadabluelab from '../assets/portadabluelab.webp'
import logoBlanco from '../assets/logobluelabblanco.png'

// Fotos de la primera prueba de campo de los BlueBoat (abril de 2026),
// reducidas y sin datos EXIF. Los textos alternativos están en bluelab.fotos
const fotos = Object.values(import.meta.glob('../assets/bluelab/blueboat-*.webp', { eager: true, import: 'default' }))

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.7), rgba(1, 33, 105, 0.9)), url('${portadabluelab}')`
})

// Iconos (los textos están en bluelab.*)
const iconosLineas = ['🚤', '🦀', '🐢', '🧠']
const iconosDivisiones = ['🛠️', '🔬', '✅']
// Fase de la hoja de ruta en la que está BLUE Lab (0 = primera)
const FASE_ACTUAL = 1
</script>

<template>
  <div class="bluelab-page">
    <section class="hero-bluelab" :style="{ backgroundImage: backgroundStyle }">
      <div class="contenedor-ancho hero-flex">
        <h1 class="solo-lectores">BLUE Lab</h1>
        <img :src="logoBlanco" alt="" class="logo-hero">
        <div class="hero-text-group">
          <p class="subtitle-hero">{{ $t('bluelab.lema') }}</p>
        </div>
      </div>
    </section>
    <div class="contenedor-ancho">
      <!-- 1. QUÉ ES -->
      <section class="seccion-bloque">
        <h2 class="titulo-seccion">{{ $t('bluelab.queEsTitulo') }}</h2>
        <div class="intro">
          <p v-for="(parrafo, i) in $tm('bluelab.queEs')" :key="i">{{ $rt(parrafo) }}</p>
        </div>
        <div class="grid-3-cols divisiones">
          <div v-for="(d, i) in $tm('bluelab.divisiones')" :key="i" class="card-division">
            <span class="icono-division" aria-hidden="true">{{ iconosDivisiones[i] }}</span>
            <div>
              <h3>{{ $rt(d.titulo) }}</h3>
              <p>{{ $rt(d.texto) }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. LÍNEAS DE INVESTIGACIÓN -->
      <section class="seccion-bloque">
        <h2 class="titulo-seccion">{{ $t('bluelab.lineasTitulo') }}</h2>
        <div class="grid-4-cols">
          <div v-for="(linea, i) in $tm('bluelab.lineas')" :key="i" class="card-area">
            <div class="icon-area" aria-hidden="true">{{ iconosLineas[i] }}</div>
            <h3>{{ $rt(linea.titulo) }}</h3>
            <p>{{ $rt(linea.texto) }}</p>
          </div>
        </div>
      </section>

      <!-- 3. FLOTA E INFRAESTRUCTURA -->
      <section class="seccion-bloque bg-ligero">
        <h2 class="titulo-seccion">{{ $t('bluelab.flotaTitulo') }}</h2>
        <div class="grid-2-cols">
          <div v-for="(grupo, i) in $tm('bluelab.flota')" :key="i" class="card-equipo">
            <h3>{{ $rt(grupo.titulo) }}</h3>
            <ul>
              <li v-for="(item, j) in grupo.items" :key="j"><strong>{{ $rt(item.nombre) }}:</strong> {{ $rt(item.texto) }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 4. GALERÍA -->
      <section class="seccion-bloque">
        <h2 class="titulo-seccion">{{ $t('bluelab.galeriaTitulo') }}</h2>
        <div class="galeria">
          <a v-for="(foto, i) in fotos" :key="foto" :href="foto" target="_blank" rel="noopener" class="foto">
            <img :src="foto" :alt="$tm('bluelab.fotos')[i] ? $rt($tm('bluelab.fotos')[i]) : ''" loading="lazy">
          </a>
        </div>
        <p class="pie-galeria">{{ $t('bluelab.galeriaPie') }}</p>
      </section>

      <!-- 5. PROYECTOS -->
      <section class="seccion-bloque">
        <h2 class="titulo-seccion">{{ $t('bluelab.proyectosTitulo') }}</h2>
        <p class="intro-corta">{{ $t('bluelab.proyectosIntro') }}</p>
        <div v-for="(grupo, i) in $tm('bluelab.gruposProyectos')" :key="i" class="grupo-proyectos">
          <h3 class="subtitulo-grupo">{{ $rt(grupo.titulo) }}</h3>
          <div class="grid-proyectos">
            <div v-for="(p, j) in grupo.proyectos" :key="j" class="card-proyecto">
              <h4>{{ $rt(p.nombre) }}</h4>
              <p>{{ $rt(p.texto) }}</p>
              <p class="ip">IP: {{ $rt(p.ip) }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 6. HOJA DE RUTA -->
      <section class="seccion-bloque bg-ligero">
        <h2 class="titulo-seccion">{{ $t('bluelab.rutaTitulo') }}</h2>
        <p class="intro-corta">{{ $t('bluelab.rutaIntro') }}</p>
        <ol class="ruta">
          <li v-for="(fase, i) in $tm('bluelab.ruta')" :key="i" :class="{ actual: i === FASE_ACTUAL, hecha: i < FASE_ACTUAL }">
            <span class="num-fase">{{ i + 1 }}</span>
            <h3>{{ $rt(fase.titulo) }} <span v-if="i === FASE_ACTUAL" class="en-curso">{{ $t('bluelab.enCurso') }}</span></h3>
            <p>{{ $rt(fase.texto) }}</p>
          </li>
        </ol>
      </section>

      <!-- 7. IMPACTO -->
      <section class="seccion-bloque">
        <h2 class="titulo-seccion">{{ $t('bluelab.impactoTitulo') }}</h2>
        <div class="grid-3-cols">
          <div v-for="(bloque, i) in $tm('bluelab.impacto')" :key="i" class="card-impacto">
            <h3>{{ $rt(bloque.titulo) }}</h3>
            <ul>
              <li v-for="(punto, j) in bloque.puntos" :key="j">{{ $rt(punto) }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 8. COLABORACIONES -->
      <section class="seccion-bloque">
        <h2 class="titulo-seccion">{{ $t('bluelab.colaboracionesTitulo') }}</h2>
        <dl class="colaboraciones">
          <div v-for="(c, i) in $tm('bluelab.colaboraciones')" :key="i">
            <dt>{{ $rt(c.titulo) }}</dt>
            <dd>{{ $rt(c.texto) }}</dd>
          </div>
        </dl>
      </section>

      <!-- 9. EQUIPO -->
      <section class="seccion-bloque">
        <h2 class="titulo-seccion">{{ $t('bluelab.equipoTitulo') }}</h2>
        <div class="equipo-container">
          <div v-for="(grupo, i) in $tm('bluelab.equipo')" :key="i" class="equipo-grupo">
            <h3>{{ $rt(grupo.titulo) }}</h3>
            <ul>
              <li v-for="(persona, j) in grupo.personas" :key="j">{{ $rt(persona) }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 10. CONTACTO -->
      <section class="cta">
        <h2>{{ $t('bluelab.ctaTitulo') }}</h2>
        <p>{{ $t('bluelab.ctaTexto') }}</p>
        <router-link :to="{ name: 'contacto' }" class="btn-cta">{{ $t('bluelab.ctaBoton') }}</router-link>
      </section>
    </div>
  </div>
</template>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

.bluelab-page {
  width: 100%;
  background-color: #fdfdfd;
  padding-bottom: 50px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* HERO SECTION */
.hero-bluelab {
  /* Eliminamos la línea background que tenías antes con la URL externa */
  background-size: cover;
  background-position: center;
  padding: 125px 0 25px 0;
  text-align: left;
  color: white;
  margin-bottom: 35px;
}

.titulo-hero {
  font-size: 2.8rem;
  margin: 0 0 20px 0;
  display: inline-block;
  border-bottom: 4px solid #0086c0;
  padding-bottom: 10px;
  font-weight: bold;
}

.subtitle-hero {
  font-family: 'Montserrat', sans-serif !important;
  font-size: 1.6rem !important;      
  color: #e0e0e0 !important;         
  letter-spacing: 1.5px !important;  
  font-weight: 400 !important;       
  text-transform: none !important; /* Forzamos minúsculas sí o sí */
  margin: 0 !important;
}
/* ESTRUCTURA GENERAL */
.seccion-bloque {
  margin-bottom: 60px;
}

.bg-ligero {
  background-color: #f4f7f9;
  padding: 40px;
  border-radius: 8px;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.02);
}

.titulo-seccion {
  color: #012169;
  font-size: 24px;
  border-bottom: 2px solid #0086c0;
  padding-bottom: 10px;
  margin-bottom: 30px;
  display: inline-block;
}

/* GRIDS */
.grid-4-cols {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.grid-3-cols {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.grid-2-cols {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

/* TARJETAS */
.card-area {
  background: white;
  padding: 25px 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  border-top: 4px solid #0086c0;
  transition: transform 0.3s;
}

.card-area:hover {
  transform: translateY(-5px);
}

.icon-area {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.card-area h3 {
  color: #012169;
  margin-top: 0;
  font-size: 1.1rem;
}

.card-area p {
  font-size: 0.95rem;
  color: #555;
  line-height: 1.5;
}

.card-equipo, .card-proyecto {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.card-equipo h4, .card-proyecto h4 {
  color: #0086c0;
  margin-top: 0;
  font-size: 1.2rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.card-equipo ul {
  padding-left: 20px;
  color: #444;
  line-height: 1.6;
}

.card-equipo li {
  margin-bottom: 10px;
}

.card-proyecto p {
  color: #555;
  line-height: 1.5;
}

/* EQUIPO */
.equipo-container {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.equipo-grupo {
  flex: 1;
  min-width: 250px;
}

.equipo-grupo h4 {
  color: #012169;
  margin-top: 0;
}

.equipo-grupo p {
  color: #555;
  line-height: 1.6;
}

.border-left {
  border-left: 1px solid #eee;
  padding-left: 30px;
}

@media (max-width: 768px) {
  .equipo-grupo.border-left {
    border-left: none;
    padding-left: 0;
  }
}
.hero-flex {
  display: flex;
  flex-direction: row;      /* Cambiamos a fila (logo a la izq, texto a la dcha) */
  align-items: center;      /* Alinea verticalmente al centro */
  justify-content: center; /* ¡ESTO LO PEGA A LA IZQUIERDA! */
  gap: 40px;                /* Espacio entre logo y texto */
  text-align: left;         /* Asegura que el texto esté a la izquierda */
}

/* Ajuste para el grupo de texto */
.hero-text-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* Alinea los elementos internos a la izquierda */
}

.logo-hero {
  /* Si antes tenías 100px, 150% serían 150px */
  height: 100px;
  width: auto;
  transition: transform 0.3s ease;
}

.subtitle-hero {
  font-size: 1.3rem;      /* Un poco más grande para compensar */
  color: #ffffff;
  letter-spacing: 2px;
  font-weight: bold;
  text-transform: uppercase;
  margin: 0;
}

/* QUÉ ES */
.intro { max-width: 900px; margin-bottom: 25px; }
.intro p { color: #444; font-size: 1.05rem; line-height: 1.7; margin: 0 0 14px; }
.intro-corta { color: #555; margin: -15px 0 20px; }
.card-division { display: flex; gap: 15px; align-items: flex-start; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 4px solid #8cc63f; }
.icono-division { font-size: 1.8rem; }
.card-division h3 { margin: 0 0 6px; color: #012169; font-size: 1.1rem; }
.card-division p { margin: 0; color: #555; line-height: 1.5; font-size: 0.95rem; }
.card-equipo h3 { color: #0086c0; margin-top: 0; font-size: 1.2rem; border-bottom: 1px solid #eee; padding-bottom: 10px; }

/* GALERÍA */
.galeria { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }
.galeria .foto { display: block; border-radius: 8px; overflow: hidden; aspect-ratio: 4 / 3; background: #e9eef3; }
.galeria img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s; display: block; }
.galeria .foto:hover img { transform: scale(1.05); }
.pie-galeria { color: #666; font-size: 0.9rem; font-style: italic; margin-top: 10px; }

/* PROYECTOS */
.grupo-proyectos { margin-bottom: 25px; }
.subtitulo-grupo { color: #012169; font-size: 1.1rem; margin: 0 0 12px; }
.grid-proyectos { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }
.card-proyecto h4 { font-size: 1.05rem; }
.card-proyecto p { font-size: 0.92rem; margin: 0 0 8px; }
.card-proyecto .ip { color: #0086c0; font-size: 0.82rem; font-weight: bold; margin: 0; }

/* HOJA DE RUTA */
.ruta { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 20px; counter-reset: fase; }
.ruta li { background: white; border-radius: 8px; padding: 20px; position: relative; border-top: 4px solid #c9d3dd; box-shadow: 0 4px 10px rgba(0,0,0,0.04); }
.ruta li.hecha { border-top-color: #8cc63f; }
.ruta li.actual { border-top-color: #0086c0; box-shadow: 0 6px 18px rgba(0,134,192,0.18); }
.num-fase { display: inline-flex; width: 30px; height: 30px; border-radius: 50%; background: #012169; color: white; align-items: center; justify-content: center; font-weight: bold; }
.ruta h3 { color: #012169; margin: 10px 0 6px; font-size: 1.1rem; }
.ruta p { color: #555; line-height: 1.5; font-size: 0.93rem; margin: 0; }
.en-curso { background: #0086c0; color: white; border-radius: 10px; padding: 2px 8px; font-size: 0.72rem; vertical-align: middle; margin-left: 6px; }

/* IMPACTO */
.card-impacto { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 4px solid #012169; }
.card-impacto h3 { color: #012169; margin-top: 0; font-size: 1.15rem; }
.card-impacto ul { padding-left: 20px; margin: 0; color: #444; line-height: 1.6; }
.card-impacto li { margin-bottom: 8px; }

/* COLABORACIONES */
.colaboraciones { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin: 0; }
.colaboraciones dt { font-weight: bold; color: #0086c0; margin-bottom: 4px; }
.colaboraciones dd { margin: 0; color: #444; line-height: 1.5; }

/* EQUIPO */
.equipo-grupo h3 { color: #012169; margin-top: 0; font-size: 1.05rem; }
.equipo-grupo ul { list-style: none; padding: 0; margin: 0; color: #555; line-height: 1.7; font-size: 0.93rem; }

/* CONTACTO */
.cta { background: #012169; color: white; border-radius: 12px; padding: 40px; text-align: center; margin-bottom: 20px; }
.cta h2 { margin: 0 0 10px; }
.cta p { color: #dce4ee; max-width: 700px; margin: 0 auto 20px; line-height: 1.6; }
.btn-cta { display: inline-block; background: #8cc63f; color: #012169; font-weight: bold; padding: 12px 26px; border-radius: 6px; text-decoration: none; }
.btn-cta:hover { background: #a5d65f; }

@media (max-width: 768px) {
  .hero-bluelab { padding-top: 150px; }
  .hero-flex { flex-direction: column; gap: 12px; text-align: center; }
  .hero-text-group { align-items: center; }
  .logo-hero { height: 75px; }
  .subtitle-hero { font-size: 1.15rem !important; text-align: center; }
  .bg-ligero { padding: 20px; }
  .grid-2-cols { grid-template-columns: 1fr; }
  .cta { padding: 28px 18px; }
}
</style>