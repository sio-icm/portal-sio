<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const indiceActual = ref(0)
const conTransicion = ref(true)

let temporizador = null
const inicioX = ref(0)
const arrastrando = ref(false)

const slides = [
  {
    imagen: 'peces.png', 
    texto: 'Apoyo técnico especializado en el ámbito de las ciencias del mar'
  },
  {
    imagen: 'niskin.png', 
    texto: 'Equipo cualificado, con una amplia gama de instrumentación y recursos',
    posicion: 'center top'
  },
  {
    imagen: 'marmarejada.jpeg', 
    texto: 'Asesoramiento y soluciones técnicas adaptadas a las necesidades específicas'
  },
  {
    imagen: 'pelagia.jpg', 
    texto: 'Embarcación y apoyo logístico en el litoral para trabajos científicos',
    posicion: 'center bottom' 
  },
    {
    imagen: 'reflexesmar.jpeg', 
    texto: 'Innovar, desarrollar, diseñar, desplegar, implementar i personalizar equipos '
  },
  {
    imagen: 'fondeo.jpeg', 
    texto: 'Diseño y despliegue de fondeos instrumentados para la observación y recolección de datos marinos de forma continuada',
    posicion: 'center bottom'
  },
  {
  imagen: 'rov.jpeg',
    texto: 'Integración de sensores en plataformas robóticas para muestreos de precisión'
  },
  {
    imagen: 'oficinatecnica.jpeg', 
    texto: 'Herramientas y técnicas específicas de verificación para garantizar la calidad de los datos obtenidos en los estudios oceanográficos.'
  },
]

const iniciarAutoplay = () => {
  detenerAutoplay()
  temporizador = setInterval(() => {
    moverCarrusel('siguiente')
  }, 6000)
}

const detenerAutoplay = () => {
  if (temporizador) {
    clearInterval(temporizador)
    temporizador = null
  }
}

onMounted(() => {
  iniciarAutoplay()
})

onBeforeUnmount(() => {
  detenerAutoplay()
})

const moverCarrusel = (direccion) => {
  if (direccion === 'siguiente') {
    if (indiceActual.value === slides.length - 1) {
      conTransicion.value = false;
      indiceActual.value = 0; 
      setTimeout(() => { conTransicion.value = true; }, 50); 
    } else {
      conTransicion.value = true;
      indiceActual.value++;
    }
  } else if (direccion === 'anterior') {
    if (indiceActual.value === 0) {
      conTransicion.value = false;
      indiceActual.value = slides.length - 1;
      setTimeout(() => { conTransicion.value = true; }, 50);
    } else {
      conTransicion.value = true;
      indiceActual.value--;
    }
  }
}

const irASlide = (index) => {
  conTransicion.value = true; 
  indiceActual.value = index;
  iniciarAutoplay() 
}

const iniciarArrastre = (evento) => {
  detenerAutoplay() 
  arrastrando.value = true
  inicioX.value = evento.type.includes('mouse') ? evento.pageX : evento.touches[0].clientX
}

const finalizarArrastre = (evento) => {
  if (!arrastrando.value) return
  arrastrando.value = false

  if (evento.type !== 'mouseleave') {
    const finX = evento.type.includes('mouse') ? evento.pageX : evento.changedTouches[0].clientX
    const distancia = inicioX.value - finX

    if (distancia > 50) {
      moverCarrusel('siguiente') 
    } else if (distancia < -50) {
      moverCarrusel('anterior') 
    }
  }

  iniciarAutoplay() 
}
</script>

<template>
  <div class="carrusel-wrapper"
       @mousedown="iniciarArrastre"
       @mouseup="finalizarArrastre"
       @mouseleave="finalizarArrastre" 
       @touchstart="iniciarArrastre"
       @touchend="finalizarArrastre"
  >
    
    <div 
      class="carrusel-inner" 
      :style="{ 
        transform: `translateX(-${indiceActual * 100}%)`,
        transition: conTransicion ? 'transform 1s ease-in-out' : 'none' 
      }"
    >
      <div class="carrusel-slide" v-for="(slide, index) in slides" :key="index">
        
        <img 
          :src="slide.imagen" 
          alt="Slide del SIO" 
          class="carrusel-img"
          :style="{ 'object-position': slide.posicion ? slide.posicion : 'center center' }"
        >
        
        <div class="carrusel-overlay"></div>
        
        <div class="carrusel-contenido">
          <div class="contenedor-ancho">
            <p class="texto-slide">{{ slide.texto }}</p>
          </div>
        </div>

      </div>
    </div>

    <div class="contenedor-puntos">
      <span 
        v-for="(slide, index) in slides" 
        :key="'punto-' + index"
        class="punto" 
        :class="{ activo: indiceActual === index }"
        @click.stop="irASlide(index)"
      ></span>
    </div>

  </div>
</template>

<style scoped>
.carrusel-wrapper {
  position: relative !important;
  width: 100%;
  overflow: hidden;
  margin-top: -140px !important; 
  top: 0;
  left: 0;
  height: 750px; 
  z-index: 1 !important; 
  cursor: grab; 
  /* Fuerza al contenedor a comportarse como un bloque 3D rígido */
  transform: translateZ(0);
}

.carrusel-wrapper:active {
  cursor: grabbing;
}

.carrusel-inner {
  display: flex;
  height: 100%;
  touch-action: pan-y; 
  
  /* ARTILLERÍA ANTI-DIFUMINADO (Nivel Contenedor) */
  will-change: transform; 
  -webkit-transform-style: preserve-3d;
  transform-style: preserve-3d;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.carrusel-slide {
  min-width: 100%;
  height: 100%;
  position: relative;
  user-select: none;
  -webkit-user-drag: none;
  
  /* ARTILLERÍA ANTI-DIFUMINADO (Nivel Diapositiva) */
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  transform: translate3d(0, 0, 0);
}

.carrusel-img {
  width: 100%;
  height: 100%;
  object-fit: cover; 
  pointer-events: none;
  
  /* EL COMBO DEFINITIVO PARA LA FOTO */
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  /* translate3d(0,0,0) fuerza la GPU, scale(1) evita reescalados fantasma */
  transform: translate3d(0, 0, 0) scale(1);
  -webkit-transform: translate3d(0, 0, 0) scale(1);
  /* Le dice al navegador que priorice el contraste y la nitidez */
  image-rendering: -webkit-optimize-contrast; 
  /* Un hack que a veces obliga a Chrome a no difuminar */
  filter: blur(0); 
}

.carrusel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(rgba(1, 33, 105, 0.4), rgba(1, 33, 105, 0.8)); 
  pointer-events: none; 
}

.carrusel-contenido {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 5; 
  pointer-events: none; 
}

.texto-slide {
  position: absolute;
  bottom: 140px; 
  left: 50%;
  transform: translateX(-50%); 
  
  width: 95%; 
  color: rgba(255, 255, 255, 0.80); 
  font-size: 1.25rem; 
  line-height: 1.5;
  text-align: center; 
  margin: 0;
  padding: 0; 
  
  text-shadow: 1px 1px 4px rgba(0,0,0,0.9), 0px 0px 15px rgba(0,0,0,0.6); 
  font-weight: 400;
  letter-spacing: 0.5px;
}

.contenedor-puntos {
  position: absolute;
  bottom: 100px; 
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 15px;
  z-index: 999; 
  pointer-events: auto;
}

.punto {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  border: 1px solid white;
  background-color: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.5); 
}

.punto.activo {
  background-color: white;
  transform: scale(1.2);
}

.punto:hover {
  background-color: rgba(255, 255, 255, 0.8);
}

@media (max-width: 768px) {
.carrusel-wrapper {
    height: 650px !important; 
  }
  .contenedor-puntos {
    bottom: 70px; 
  }
.texto-slide {
    font-size: 0.95rem; 
    bottom: 110px; 
    width: 95%; 
  }
}
</style>