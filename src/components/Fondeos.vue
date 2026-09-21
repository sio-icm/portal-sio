<script setup>
import { computed } from 'vue'
import fondoInstrumentacion from '../assets/instrumentacion.jpg'

defineEmits(['cambiar-pagina'])

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('${fondoInstrumentacion}')`
})
</script>

<template>
  <div class="fondeos-page">
    <div class="fondo-fondeos" :style="{ backgroundImage: backgroundStyle }"></div>
    
    <div class="contenedor-ancho contenido-fondeos">
      <h1 class="titulo-seccion">Gestión de Fondeos Oceanográficos</h1>
      <p class="subtitulo">Planificación técnica, diseño, instalación y seguimiento de fondeos y trípodes instrumentados.</p>

      <div class="tarjeta-contenido">
        
        <!-- 🌟 PRESENTACIÓN DEL SERVICIO (NUEVO) -->
        <div class="intro-servicio">
          <p class="texto-destacado">
            El <strong>Servicio de Ingeniería Oceanográfica</strong> participa en el diseño, preparación e instalación de fondeos y trípodes oceanográficos instrumentados. Nos encargamos de la planificación técnica completa, asegurando que todos los componentes sean óptimos para obtener datos de alta calidad en tus estudios oceanográficos.
          </p>
          <p class="nota-usuario">
            <em>Nota: Los instrumentos y material auxiliar necesarios, en función del tipo de estudio requerido, serán aportados por el usuario.</em>
          </p>
        </div>

        <!-- ⚙️ FASES DEL SERVICIO -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">Fases del Servicio</h3>
          <div class="grid-fases">
            <div class="fase-card">
              <span class="fase-num">01</span>
              <h4>Diseño</h4>
              <p>Análisis de necesidades científicas y configuración óptima del fondeo.</p>
            </div>
            <div class="fase-card">
              <span class="fase-num">02</span>
              <h4>Preparación</h4>
              <p>Integración, calibración de instrumentos y ensamblaje de componentes.</p>
            </div>
            <div class="fase-card">
              <span class="fase-num">03</span>
              <h4>Despliegue</h4>
              <p>Instalación en el campo con equipo especializado y experto.</p>
            </div>
            <div class="fase-card">
              <span class="fase-num">04</span>
              <h4>Seguimiento</h4>
              <p>Control y monitoreo continuo del fondeo durante su operación.</p>
            </div>
          </div>
        </div>

        <!-- 📊 TIPOS DE INSTRUMENTACIÓN INTEGRABLE -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">Instrumentación Integrable</h3>
          <p class="texto-explicativo">Nuestros sistemas pueden integrar una amplia variedad de sensores según los parámetros que necesites medir:</p>
          <div class="grid-instrumentos">
            <div class="inst-item">🌊 Correntímetros y Perfiladores Doppler <span class="inst-desc">Velocidades y direcciones de corrientes</span></div>
            <div class="inst-item">🌡️ Sensores de Temperatura <span class="inst-desc">Monitoreo térmico del agua</span></div>
            <div class="inst-item">🧂 Sensores de Conductividad <span class="inst-desc">Medición de salinidad</span></div>
            <div class="inst-item">🔵 Sensores de Presión <span class="inst-desc">Determinación de profundidad</span></div>
            <div class="inst-item">📊 Turbidímetros <span class="inst-desc">Concentración de partículas y turbidez</span></div>
            <div class="inst-item">🟢 Sensores de Oxígeno <span class="inst-desc">Oxígeno disuelto en el agua</span></div>
            <div class="inst-item">🌿 Fluorómetros <span class="inst-desc">Clorofila y materia orgánica</span></div>
            <div class="inst-item">🧪 Sensores de pH <span class="inst-desc">Acidez y alcalinidad</span></div>
            <div class="inst-item">🌀 Sensores de Turbulencia <span class="inst-desc">Caracterización de procesos turbulentos</span></div>
            <div class="inst-item">🪣 Trampas de Sedimento <span class="inst-desc">Recogida de partículas en suspensión</span></div>
          </div>
        </div>

        <!-- 📝 FORMULARIO DE SOLICITUD -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">Solicitar Instalación de Fondeo</h3>
          <form class="formulario-fondeo">
            <div class="grupo-input">
              <input type="text" placeholder="Nombre del Proyecto / Investigador Principal" required>
            </div>
            <div class="fila-fechas">
              <div class="input-fecha-box">
                <label>Fecha de inicio prevista:</label>
                <input type="date" required>
              </div>
              <div class="input-fecha-box">
                <label>Fecha de retirada prevista:</label>
                <input type="date" required>
              </div>
            </div>
            <div class="grupo-input">
              <textarea rows="4" placeholder="Breve explicación de la campaña, objetivos e instrumentos que aportarás..." required></textarea>
            </div>
            <button type="submit" class="btn-solicitar">Solicitar Reserva al SIO</button>
          </form>
        </div>

        <!-- ⚓ ESTADO ACTUAL DE FONDEOS -->
        <div class="seccion-bloque" style="margin-top: 40px;">
          <h3 class="subtitulo-bloque">Estado Actual de Fondeos</h3>
          <div class="estados-container">
            <div class="estado-grupo">
              <span class="punto-verde"></span> <strong>Activos en el mar</strong>
              <div class="item-estado">
                <strong>FND-001</strong> - Cañón de Blanes <br><small>IP: Ivan Masmitja</small>
              </div>
            </div>
            <div class="estado-grupo">
              <span class="punto-gris"></span> <strong>Retirados / Histórico</strong>
              <div class="item-estado gris">
                <strong>FND-000</strong> - Plataforma B
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.fondeos-page { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-fondeos { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-size: cover; background-position: center; z-index: 0; }
.contenido-fondeos { position: relative; z-index: 10; padding-top: 120px; }

.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 40px; max-width: 800px; }

.tarjeta-contenido { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-top: 4px solid #012169; }
.subtitulo-bloque { color: #012169; font-size: 1.4rem; margin-bottom: 20px; margin-top: 0; border-bottom: 2px solid #eef2f5; padding-bottom: 8px; }
.seccion-bloque { margin-top: 40px; }

/* Intro servicio */
.texto-destacado { font-size: 1.05rem; color: #333; line-height: 1.6; margin-bottom: 10px; }
.nota-usuario { font-size: 0.95rem; color: #666; background: #f8f9fa; padding: 10px 15px; border-left: 3px solid #0086c0; border-radius: 4px; display: inline-block; }

/* Grid Fases */
.grid-fases { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 15px; }
.fase-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-top: 3px solid #8cc63f; position: relative; }
.fase-num { position: absolute; top: 10px; right: 15px; font-size: 1.5rem; font-weight: bold; color: #e2e8f0; }
.fase-card h4 { color: #012169; margin: 0 0 8px 0; font-size: 1.1rem; }
.fase-card p { color: #555; font-size: 0.85rem; margin: 0; line-height: 1.4; }

/* Grid Instrumentos */
.texto-explicativo { color: #555; font-size: 0.95rem; margin-bottom: 15px; }
.grid-instrumentos { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.inst-item { background: #fdfdfd; border: 1px solid #e2e8f0; padding: 10px 15px; border-radius: 6px; font-size: 0.9rem; font-weight: bold; color: #012169; display: flex; flex-direction: column; gap: 2px; }
.inst-desc { font-weight: normal; font-size: 0.8rem; color: #666; }

/* Formulario */
.formulario-fondeo { display: flex; flex-direction: column; gap: 20px; margin-top: 15px; }
.grupo-input input, .grupo-input textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; box-sizing: border-box; }
.fila-fechas { display: flex; gap: 20px; }
.input-fecha-box { width: 100%; display: flex; flex-direction: column; gap: 5px; }
.input-fecha-box label { font-size: 0.85rem; font-weight: bold; color: #555; }
.input-fecha-box input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
.btn-solicitar { background-color: #0086c0; color: white; border: none; padding: 14px 25px; font-size: 1rem; font-weight: bold; border-radius: 6px; cursor: pointer; transition: background 0.3s; align-self: flex-start; }
.btn-solicitar:hover { background-color: #012169; }

/* Estados */
.estados-container { display: flex; flex-direction: column; gap: 15px; }
.estado-grupo { display: flex; align-items: center; gap: 10px; font-size: 0.95rem; flex-wrap: wrap; }
.punto-verde { width: 10px; height: 10px; background-color: #28a745; border-radius: 50%; display: inline-block; }
.punto-gris { width: 10px; height: 10px; background-color: #6c757d; border-radius: 50%; display: inline-block; }
.item-estado { background: #f8f9fa; border: 1px solid #e9ecef; padding: 10px 15px; border-radius: 6px; width: 100%; margin-top: 5px; font-size: 0.9rem; }
.item-estado.gris { background: #fdfdfd; color: #6c757d; }

@media (max-width: 768px) { 
  .contenido-fondeos { padding-top: 150px; } 
  .fila-fechas { flex-direction: column; gap: 15px; } 
}
</style>