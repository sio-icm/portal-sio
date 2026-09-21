<script setup>
import { computed } from 'vue'
import fondoInstrumentacion from '../assets/instrumentacion.jpg'

defineEmits(['cambiar-pagina'])

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('${fondoInstrumentacion}')`
})
</script>

<template>
  <div class="prototipado-page">
    <div class="fondo-prototipado" :style="{ backgroundImage: backgroundStyle }"></div>
    
    <div class="contenedor-ancho contenido-prototipado">
      <h1 class="titulo-seccion">Prototipado Rápido y Fabricación</h1>
      <p class="subtitulo">Diseño CAD avanzado, mecanizado de precisión y producción de componentes mecánicos complejos.</p>

      <div class="tarjeta-contenido">
        
        <!-- 🌟 PRESENTACIÓN DEL SERVICIO -->
        <div class="intro-servicio">
          <p class="texto-destacado">
            El <strong>Servicio de Ingeniería Oceanográfica</strong> cuenta con capacidades avanzadas de fabricación y prototipado rápido para dar soporte directo a la investigación marina. Desde la concepción en diseño CAD, creamos piezas a medida.
          </p>
        </div>

        <!-- ⚙️ TECNOLOGÍAS Y CAPACIDADES -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">Capacidades del Taller</h3>
          <div class="grid-fases">
            <div class="fase-card">
              <span class="fase-num">01</span>
              <h4>Impresión 3D Técnica</h4>
              <p>Fabricación aditiva en materiales de altas prestaciones (resinas técnicas, filamentos avanzados).</p>
            </div>

            <div class="fase-card">
              <span class="fase-num">03</span>
              <h4>Diseño CAD / CAE</h4>
              <p>Modelado 3D paramétrico y validación de geometrías complejas para entornos subacuáticos.</p>
            </div>

          </div>
        </div>

        <!-- 📝 FORMULARIO DE SOLICITUD -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">Solicitar Pieza o Prototipo</h3>
          <form class="formulario-prototipado">
            <div class="grupo-input">
              <input type="text" placeholder="Nombre del Proyecto / Investigador Principal" required>
            </div>
            <div class="grupo-input">
              <input type="text" placeholder="Tipo de pieza o componente requerido (Ej: Carcasa estanca, soporte sensor...)" required>
            </div>
            <div class="grupo-input">
              <textarea rows="4" placeholder="Describe los requisitos técnicos, dimensiones aproximadas o material previsto..." required></textarea>
            </div>
            <button type="submit" class="btn-solicitar">Solicitar Trabajo al SIO</button>
          </form>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.prototipado-page { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-prototipado { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-size: cover; background-position: center; z-index: 0; }
.contenido-prototipado { position: relative; z-index: 10; padding-top: 120px; }

.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 40px; max-width: 800px; }

.tarjeta-contenido { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-top: 4px solid #012169; }
.subtitulo-bloque { color: #012169; font-size: 1.4rem; margin-bottom: 20px; margin-top: 0; border-bottom: 2px solid #eef2f5; padding-bottom: 8px; }
.seccion-bloque { margin-top: 40px; }

.texto-destacado { font-size: 1.05rem; color: #333; line-height: 1.6; margin-bottom: 10px; }

/* Grid Capacidades */
.grid-fases { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 15px; }
.fase-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-top: 3px solid #8cc63f; position: relative; }
.fase-num { position: absolute; top: 10px; right: 15px; font-size: 1.5rem; font-weight: bold; color: #e2e8f0; }
.fase-card h4 { color: #012169; margin: 0 0 8px 0; font-size: 1.1rem; }
.fase-card p { color: #555; font-size: 0.85rem; margin: 0; line-height: 1.4; }

/* Formulario */
.formulario-prototipado { display: flex; flex-direction: column; gap: 20px; margin-top: 15px; }
.grupo-input input, .grupo-input textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; box-sizing: border-box; }
.btn-solicitar { background-color: #0086c0; color: white; border: none; padding: 14px 25px; font-size: 1rem; font-weight: bold; border-radius: 6px; cursor: pointer; transition: background 0.3s; align-self: flex-start; }
.btn-solicitar:hover { background-color: #012169; }

@media (max-width: 768px) { 
  .contenido-prototipado { padding-top: 150px; } 
}
</style>