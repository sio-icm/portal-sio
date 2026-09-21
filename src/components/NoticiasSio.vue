<script setup>
import { computed } from 'vue'
import fondoNoticias from '../assets/instrumentacion.jpg'

defineEmits(['cambiar-pagina'])

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('${fondoNoticias}')`
})

const noticias = [
  { id: 1, fecha: '15 Mayo 2026', titulo: 'Nueva campaña de calibración en la plataforma costera', resumen: 'El equipo del SIO ha completado con éxito la última campaña de mantenimiento y calibración de los perfiladores Doppler en la zona de Blanes.' },
  { id: 2, fecha: '02 Abril 2026', titulo: 'Ampliación del parque de impresión 3D', resumen: 'Incorporamos nueva maquinaria de prototipado rápido en resina y filamento técnico para el desarrollo de carcasas submarinas a medida.' },
  { id: 3, fecha: '18 Marzo 2026', titulo: 'Participación en el proyecto DIGI4ECO', resumen: 'El SIO colaborará aportando soporte técnico en el despliegue de vehículos autónomos para la creación del Gemelo Digital del Océano.' }
]
</script>

<template>
  <div class="noticias-page">
    <div class="fondo-noticias"></div>

    <div class="contenedor-ancho contenido-noticias">
      <h1 class="titulo-seccion">Noticias y Actualidad</h1>
      <p class="subtitulo">Últimas novedades, campañas y avances tecnológicos del Servicio de Ingeniería Oceanográfica.</p>

      <div class="grid-noticias">
        
        <!-- Noticia 1 -->
        <div class="tarjeta-noticia">
          <div class="contenedor-imagen-noticia">
            <img src="https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=600&q=80" alt="Campaña oceanográfica">
          </div>
          <div class="fecha-noticia">19 AGOSTO 2026</div>
          <h3>Nueva misión autónoma con vehículos de superficie en la Costa Brava</h3>
          <p class="texto-noticia">
            Nuestro equipo ha desplegado con éxito la nueva flota de vehículos autónomos para monitorizar corrientes superficiales y parámetros físico-químicos en tiempo real. Esta prueba piloto nos permite validar los algoritmos de navegación adaptativa antes de dar el salto a misiones de larga duración en mar abierto.
          </p>
        </div>

<!-- Noticia 2 (Corregida) -->
        <div class="tarjeta-noticia">
          <div class="contenedor-imagen-noticia">
            <img src="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=600&q=80" alt="Laboratorio e impresión 3D">
          </div>
          <div class="fecha-noticia">10 JULIO 2026</div>
          <h3>Avances en el diseño y fabricación de nuevos sensores submarinos</h3>
          <p class="texto-noticia">
            Gracias a la combinación de nuestras fresadoras de precisión y el nuevo parque de impresión 3D, hemos logrado prototipar carcasas estancas ultraligeras y soportes a medida para instrumentación oceanográfica extrema. Esto reduce drásticamente los costes de desarrollo y acelera nuestras pruebas en laboratorio.
          </p>
        </div>

        <!-- Noticia 3 -->
        <div class="tarjeta-noticia">
          <div class="contenedor-imagen-noticia">
            <img src="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80" alt="Sinergias y cooperación marina">
          </div>
          <div class="fecha-noticia">28 JUNIO 2026</div>
          <h3>Nuevas sinergias estratégicas para la observación costera</h3>
          <p class="texto-noticia">
            Establecemos nuevas líneas de colaboración con instituciones y entidades del sector para compartir recursos náuticos y optimizar el despliegue de redes de boyas y radares HF. Un paso más hacia la consolidación de un sistema de observación marina integrado y de alta eficiencia en el litoral catalán.
          </p>
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