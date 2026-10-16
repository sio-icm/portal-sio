<script setup>
// IMPORTACIÓN DE TUS FONDOS PNG
import bgRoig from '../assets/roig.png'
import bgVerd from '../assets/verd.png'
import bgBlue from '../assets/blue.png'
import bgGroc from '../assets/groc.png'
import logoBlueLab from '../assets/logobluelab.png'

// 🗑️ Hemos borrado las fotos de Unsplash porque ya no las necesitamos
</script>

<template>
  <section class="seccion-fichas-sio">
    <div class="contenedor-ancho">
      <div class="fichas-grid">

        <RouterLink :to="{ name: 'memoria' }" class="ficha-sio text-white" :style="{ backgroundImage: `url(${bgRoig})` }">
          <div class="contenido">
            <h3>Memoria anual</h3>
          </div>
        </RouterLink>

        <RouterLink :to="{ name: 'noticias' }" class="ficha-sio text-white" :style="{ backgroundImage: `url(${bgVerd})` }">
          <div class="contenido">
            <h3>Noticias</h3>
          </div>
        </RouterLink>

        <RouterLink :to="{ name: 'equipo' }" class="ficha-sio text-white" :style="{ backgroundImage: `url(${bgGroc})` }">
          <div class="contenido">
            <h3>Equipo SIO</h3>
          </div>
        </RouterLink>

        <RouterLink :to="{ name: 'bluelab' }" class="ficha-sio" style="background-image: none; padding: 0; display: flex; justify-content: center; align-items: center; background-color: #02097c;">
          <img :src="logoBlueLab" alt="BLUE Lab" style="max-width: 100%; max-height: 110%; object-fit: cover;">
        </RouterLink>

      </div>
    </div>
  </section>
</template>

<style scoped>
.seccion-fichas-sio {
  margin-top: -50px;
  position: relative;
  z-index: 50;
  width: 100%;
  padding-bottom: 40px;
}

.fichas-grid {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.ficha-sio {
  display: block;
  text-decoration: none;
  width: 250px;
  height: 120px;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  transition: all 0.4s ease;
  /* Transición suave para todos los efectos */

  /* FONDO PNG */
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;

  /* 🔵 ESTADO NORMAL: Atenuado con el azul del SIO para legibilidad */
  background-blend-mode: overlay;
  background-color: rgba(1, 33, 105, 0.3);
}

/* ✨ ESTADO HOVER: ¡A todo color! ✨ */
.ficha-sio:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.25);
  /* Al quitar el color de fondo, la atenuación desaparece */
  background-blend-mode: normal;
  background-color: transparent;
}

.ficha-sio:focus-visible {
  outline: 3px solid #0086c0;
  outline-offset: 3px;
}

/* ✍️ AJUSTES DE TEXTO */
.contenido {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.contenido h3 {
  margin: 0;
  font-size: 1.1rem;
  letter-spacing: 1px;
  font-weight: bold;
  transition: transform 0.3s ease;
}

/* Que el texto crezca un pelín al pasar el ratón */
.ficha-sio:hover .contenido h3 {
  transform: scale(1.05);
}

.text-white h3 {
  color: white;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);
}

.text-dark-navy h3 {
  color: #012169;
  text-shadow: none;
}

@media (max-width: 768px) {
  .ficha-sio {
    width: 45%;
    height: 100px;
  }

  .seccion-fichas-sio {
    margin-top: -30px;
  }
}
</style>