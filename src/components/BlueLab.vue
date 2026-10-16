<script setup>
import { computed } from 'vue'
import portadabluelab from '../assets/portadabluelab.png'
import logoBlanco from '../assets/logobluelabblanco.png'

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.7), rgba(1, 33, 105, 0.9)), url('${portadabluelab}')`
})

// Icono de cada línea de innovación (los textos están en bluelab.lineas)
const iconosLineas = ['🚤', '🦀', '🐢', '🧠']
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
      <!-- 2. LAS 4 ÁREAS DE INVESTIGACIÓN -->
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

      <!-- 3. LA FLOTA Y EL GARAJE (Equipamiento) -->
      <section class="seccion-bloque bg-ligero">
        <h2 class="titulo-seccion">{{ $t('bluelab.flotaTitulo') }}</h2>
        <div class="grid-2-cols">
          <div v-for="(grupo, i) in $tm('bluelab.flota')" :key="i" class="card-equipo">
            <h4>{{ $rt(grupo.titulo) }}</h4>
            <ul>
              <li v-for="(item, j) in grupo.items" :key="j"><strong>{{ $rt(item.nombre) }}:</strong> {{ $rt(item.texto) }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 4. CASOS DE ÉXITO -->
      <section class="seccion-bloque">
        <h2 class="titulo-seccion">{{ $t('bluelab.proyectosTitulo') }}</h2>
        <div class="grid-3-cols">
          <div v-for="(proyecto, i) in $tm('bluelab.proyectos')" :key="i" class="card-proyecto">
            <h4>{{ $rt(proyecto.nombre) }}</h4>
            <p>{{ $rt(proyecto.texto) }}</p>
          </div>
        </div>
      </section>

      <!-- 5. EL EQUIPO -->
      <section class="seccion-bloque">
        <h2 class="titulo-seccion">{{ $t('bluelab.equipoTitulo') }}</h2>
        <div class="equipo-container">
          <div class="equipo-grupo">
            <h4>{{ $t('bluelab.liderazgo') }}</h4>
            <p>Raül Bardají (SIO), Ivan Masmitja (DOFT), Giacomo Picardi (REC), Isabel Afán (REC), Ruth Durán (GEO).</p>
          </div>
          <div class="equipo-grupo border-left">
            <h4>{{ $t('bluelab.equipoSio') }}</h4>
            <p>Raül Ferrando, Nina Hoareau, Brian Nicolás.</p>
          </div>
          <div class="equipo-grupo border-left">
            <h4>{{ $t('bluelab.predoctorales') }}</h4>
            <p>M. Gallici, G. Batet, P. Agundez, J. Aguirregomezcorta, M. Ferrari, M. González, A. Sánchez-Márquez, A. Idiondo-Molina.</p>
          </div>
        </div>
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
  padding: 160px 0 60px 0;
  text-align: left;
  color: white;
  margin-bottom: 50px;
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
  height: 150px;          
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
</style>