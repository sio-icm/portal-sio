<script setup>
import { computed } from 'vue'
const fondoInstrumentacion = '/instrumentacion.webp'

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('${fondoInstrumentacion}')`
})

// 📋 DATOS DEL EQUIPO (las fotos se leen de public/fotos/equipo/;
// el cargo y la descripción de cada persona están en src/i18n: equipo.personas.<id>)
const equipo = [
  { id: 'rbardaji', nombre: 'Raül Bardají', tagClase: 'lider', etiqueta: 'liderazgo', fotoSrc: '/fotos/equipo/rbardaji.jpg' },
  { id: 'rferrando', nombre: 'Raül Ferrando', tagClase: 'tecnico', etiqueta: 'ingenieria', fotoSrc: '/fotos/equipo/rferrando.jpg' },
  { id: 'nhoareau', nombre: 'Nina Hoareau', tagClase: 'tecnico', etiqueta: 'soporte', fotoSrc: '/fotos/equipo/nhoareau.jpg' },
  { id: 'bnicolas', nombre: 'Brian Nicolás', tagClase: 'tecnico', etiqueta: 'soporte', fotoSrc: '/fotos/equipo/bnicolas.jpg' },
  { id: 'ksalvador', nombre: 'Kintxo Salvador', tagClase: 'tecnico', etiqueta: 'soporte', fotoSrc: '/fotos/equipo/ksalvador.jpg' },
  { id: 'mlloret', nombre: 'Maribel Lloret', tagClase: 'tecnico', etiqueta: 'soporte', fotoSrc: '/fotos/equipo/mlloret.jpg' }
]
</script>

<template>
  <div class="equipo-page">
    <div class="fondo-equipo" :style="{ backgroundImage: backgroundStyle }"></div>
    
    <div class="contenedor-ancho contenido-equipo">
      <h1 class="titulo-seccion">{{ $t('equipo.titulo') }}</h1>
      <p class="subtitulo">{{ $t('equipo.subtitulo') }}</p>

      <div class="grid-personal">
        
        <!-- BUCLE v-for: CREA UNA TARJETA POR CADA PERSONA EN LA LISTA -->
        <div class="tarjeta-personal" v-for="persona in equipo" :key="persona.id">
          
          <div class="contenedor-foto">
            <!-- La foto carga la ruta, y si falla (aún no la has subido), pone la silueta por defecto -->
            <img :src="persona.fotoSrc" :alt="persona.nombre" class="foto-perfil" onerror="this.onerror=null; this.src='/fotos/equipo/perfil-default.svg'">
          </div>

          <div :class="['rol-tag', persona.tagClase]">{{ $t(`equipo.etiquetas.${persona.etiqueta}`) }}</div>
          <h3>{{ persona.nombre }}</h3>
          <p class="cargo">{{ $t(`equipo.personas.${persona.id}.cargo`) }}</p>
          <div v-if="$t(`equipo.personas.${persona.id}.descripcion`)" class="descripcion-personal">
            {{ $t(`equipo.personas.${persona.id}.descripcion`) }}
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