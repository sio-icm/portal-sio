<script setup>
import { computed } from 'vue'
import fondoInstrumentacion from '../assets/instrumentacion.jpg'

defineEmits(['cambiar-pagina'])

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('${fondoInstrumentacion}')`
})
</script>

<template>
  <div class="memoria-page">
    <div class="fondo-cabecera" :style="{ backgroundImage: backgroundStyle }"></div>
    
    <div class="contenedor-ancho contenido-pagina">
      <h1 class="titulo-seccion">Memoria Anual</h1>
      <p class="subtitulo">Transparencia, métricas e impacto de nuestra actividad científica y técnica durante el último ejercicio.</p>

      <div class="bloque-blanco">
        <h2>Resumen de Actividad 2025</h2>
        <p class="intro-memoria">El Servicio de Ingeniería Oceanográfica ha continuado su labor de soporte a la investigación marina, ampliando sus capacidades operativas y de prototipado rápido. A continuación, se destacan los indicadores clave del año.</p>
        
        <div class="grid-metricas">
          <div class="tarjeta-metrica">
            <span class="numero">24</span>
            <span class="etiqueta">Campañas Soportadas</span>
          </div>
          <div class="tarjeta-metrica">
            <span class="numero">150+</span>
            <span class="etiqueta">Sensores Calibrados</span>
          </div>
          <div class="tarjeta-metrica">
            <span class="numero">12</span>
            <span class="etiqueta">Fondeos Instalados</span>
          </div>
          <div class="tarjeta-metrica">
            <span class="numero">8</span>
            <span class="etiqueta">Proyectos I+D+I</span>
          </div>
        </div>

        <div class="caja-descarga">
          <div class="icono-doc">📄</div>
          <div>
            <h3>Memoria Completa SIO 2025</h3>
            <p>Documento detallado con el balance anual, listado de proyectos y métricas de servicio (PDF, 4.2 MB).</p>
          </div>
          <a href="#" class="btn-descarga">Descargar PDF</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.memoria-page { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-cabecera { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-size: cover; background-position: center; z-index: 0; }
.contenido-pagina { position: relative; z-index: 10; padding-top: 120px; }
.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 40px; max-width: 800px; }

.bloque-blanco { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-top: 4px solid #dc3545; }
.bloque-blanco h2 { color: #012169; margin-top: 0; font-size: 1.8rem; border-bottom: 2px solid #eee; padding-bottom: 10px; }
.intro-memoria { color: #555; font-size: 1.05rem; line-height: 1.6; margin-bottom: 30px; }

.grid-metricas { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
.tarjeta-metrica { background: #f8f9fa; padding: 25px; border-radius: 8px; text-align: center; border: 1px solid #e9ecef; }
.numero { display: block; font-size: 2.5rem; font-weight: bold; color: #dc3545; margin-bottom: 5px; }
.etiqueta { font-size: 0.95rem; color: #666; font-weight: bold; text-transform: uppercase; }

.caja-descarga { display: flex; align-items: center; gap: 20px; background: #eaf2f8; padding: 25px; border-radius: 8px; border-left: 4px solid #0086c0; }
.icono-doc { font-size: 3rem; }
.caja-descarga h3 { margin: 0 0 5px 0; color: #012169; }
.caja-descarga p { margin: 0; color: #555; font-size: 0.95rem; }
.btn-descarga { margin-left: auto; background-color: #0086c0; color: white; padding: 12px 25px; border-radius: 6px; text-decoration: none; font-weight: bold; transition: background 0.3s; white-space: nowrap; }
.btn-descarga:hover { background-color: #012169; }

@media (max-width: 768px) { 
  .contenido-pagina { padding-top: 150px; } 
  .caja-descarga { flex-direction: column; text-align: center; } 
  .btn-descarga { margin-left: 0; margin-top: 15px; width: 100%; text-align: center; } 
}
</style>