<script setup>
import { ref, computed } from 'vue'
import fondoInstrumentacion from '../assets/instrumentacion.jpg'

defineEmits(['cambiar-pagina'])

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('${fondoInstrumentacion}')`
})

// 📋 DATOS DEL EQUIPO (Las fotos se leen de la carpeta public/equipo/)
const equipo = ref([
  {
    id: 'rbardaji',
    nombre: 'Raül Bardají',
    cargo: 'Responsable Técnico del SIO',
    tagClase: 'lider',
    tagTexto: 'Liderazgo',
    descripcion: 'Coordinación general de infraestructuras, gestión de campañas oceanográficas y dirección del soporte tecnológico en el ICM-CSIC.',
    fotoSrc: 'equipo/rbardaji.jpg'
  },
  {
    id: 'rferrando',
    nombre: 'Raül Ferrando',
    cargo: 'Personal Técnico de Investigación (PIT)',
    tagClase: 'tecnico',
    tagTexto: 'Ingeniería & Soporte',
    descripcion: 'Diseño industrial, desarrollo de sistemas embebidos, prototipado rápido (Mecanizado/Impresión 3D) y mantenimiento de la flota autónoma.',
    fotoSrc: 'equipo/rferrando.jpg'
  },
  {
    id: 'nhoareau',
    nombre: 'Nina Hoareau',
    cargo: 'Especialista en Instrumentación',
    tagClase: 'tecnico',
    tagTexto: 'Soporte Técnico',
    descripcion: 'Calibración de sensores oceanográficos, análisis físico-químico de muestras de agua (Salinidad) y asistencia técnica en campañas.',
    fotoSrc: 'equipo/nhoareau.jpg'
  },
  {
    id: 'bnicolas',
    nombre: 'Bryan Nicolás',
    cargo: 'Técnico en Electrónica y Sistemas',
    tagClase: 'tecnico',
    tagTexto: 'Soporte Técnico',
    descripcion: 'Mantenimiento preventivo y correctivo de sistemas de telemetría, comunicaciones submarinas y electrónica analógica/digital.',
    fotoSrc: 'equipo/bnicolas.jpg'
  },
  {
    id: 'ksalvador',
    nombre: 'Kintxo Salvador',
    cargo: 'Técnico de Soporte',
    tagClase: 'tecnico',
    tagTexto: 'Soporte Técnico',
    descripcion: 'Escribe aquí la descripción de las tareas, especialidades y soporte que ofrece Kintxo dentro del Servicio de Ingeniería Oceanográfica.',
    fotoSrc: 'equipo/ksalvador.jpg'
  },
  {
    id: 'mlloret',
    nombre: 'Maribel Lloret',
    cargo: 'Técnica de Soporte',
    tagClase: 'tecnico',
    tagTexto: 'Soporte Técnico',
    descripcion: 'Escribe aquí la descripción de las tareas, especialidades y soporte que ofrece Maribel dentro del Servicio de Ingeniería Oceanográfica.',
    fotoSrc: 'equipo/mlloret.jpg'
  }
])
</script>

<template>
  <div class="equipo-page">
    <div class="fondo-equipo" :style="{ backgroundImage: backgroundStyle }"></div>
    
    <div class="contenedor-ancho contenido-equipo">
      <h1 class="titulo-seccion">Equipo SIO</h1>
      <p class="subtitulo">El personal técnico e investigador que da soporte a las ciencias del mar.</p>

      <div class="grid-personal">
        
        <!-- BUCLE v-for: CREA UNA TARJETA POR CADA PERSONA EN LA LISTA -->
        <div class="tarjeta-personal" v-for="persona in equipo" :key="persona.id">
          
          <div class="contenedor-foto">
            <!-- La foto carga la ruta, y si falla (aún no la has subido), pone la silueta por defecto -->
            <img :src="persona.fotoSrc" :alt="persona.nombre" class="foto-perfil" onerror="this.src='perfil-default.jpg'">
          </div>

          <div :class="['rol-tag', persona.tagClase]">{{ persona.tagTexto }}</div>
          <h3>{{ persona.nombre }}</h3>
          <p class="cargo">{{ persona.cargo }}</p>
          <div class="descripcion-personal">
            {{ persona.descripcion }}
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.equipo-page { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-equipo { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-size: cover; background-position: center; z-index: 0; }
.contenido-equipo { position: relative; z-index: 10; padding-top: 120px; }
.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 40px; max-width: 800px; }

/* GRID DE TARJETAS */
.grid-personal { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 20px; }
.tarjeta-personal { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); display: flex; flex-direction: column; position: relative; border-top: 4px solid #012169; }

/* 📸 MAQUETACIÓN DE LA FOTO EN CÍRCULO */
.contenedor-foto { 
  width: 130px; 
  height: 130px; 
  background-color: #e9ecef; 
  border-radius: 50%; /* Esto hace el círculo perfecto */
  margin: 0 auto 20px auto; /* Esto lo centra en la tarjeta */
  overflow: hidden; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  border: 3px solid #8cc63f; /* Un bordecito verde ICM que le dará mucha vida */
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  flex-shrink: 0;
}
.foto-perfil { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; /* Magia pura: rellena el círculo sin deformar tu cara */
  object-position: center; /* Asegura que no te corte la cabeza si la foto es muy alta */
}

.tarjeta-personal h3 { color: #012169; font-size: 1.4rem; margin: 10px 0 5px 0; }
.cargo { color: #0086c0; font-weight: bold; font-size: 0.95rem; margin-bottom: 15px; }
.descripcion-personal { color: #555; font-size: 0.95rem; line-height: 1.5; }

/* BADGES DE ROL */
.rol-tag { align-self: flex-start; font-size: 0.75rem; text-transform: uppercase; font-weight: bold; padding: 4px 10px; border-radius: 20px; letter-spacing: 0.5px; }
.rol-tag.lider { background-color: #e6f2ff; color: #005596; }
.rol-tag.tecnico { background-color: #eaf7ed; color: #257a3c; }

@media (max-width: 768px) { .contenido-equipo { padding-top: 150px; } .grid-personal { grid-template-columns: 1fr; } }
</style>