<script setup>
import { ref } from 'vue'
import { useCalendarioReservas } from '../composables/useCalendarioReservas'
import fondoTanques from '../assets/tanques.jpg'

const {
  nombreMes, diasMesVisible, hayMesAnterior, hayMesSiguiente, mesAnterior, mesSiguiente,
  diasSeleccionados, esOcupado, toggleDia, estaSeleccionado, fechasSeleccionadas
} = useCalendarioReservas()

// --- FORMULARIO ---
const proposito = ref('')
const necesitaGrua = ref('No')

// Enviar el correo
const enviarSolicitud = () => {
  if (diasSeleccionados.value.length === 0 || proposito.value.trim() === '') {
    alert('Por favor, selecciona al menos un día en el calendario y escribe el propósito.')
    return
  }

  const destinatario = "sio@icm.csic.es"
  const asunto = encodeURIComponent("Solicitud de Uso - Tanques de Pruebas SIO")
  
  // Construimos el cuerpo del mensaje
  const cuerpo = encodeURIComponent(
    `Hola equipo del SIO,\n\n` +
    `Me gustaría solicitar el uso de los Tanques de Pruebas.\n\n` +
    `📅 DÍAS SOLICITADOS:\n- ${fechasSeleccionadas.value.join('\n- ')}\n\n` +
    `📋 PROPÓSITO DE LAS PRUEBAS:\n${proposito.value}\n\n` +
    `🏗️ USO DE GRÚA DE CARGA:\n${necesitaGrua.value}\n\n` +
    `Quedo a la espera de vuestra confirmación para coordinarnos.\n\nUn saludo.`
  )

  // Abrir el cliente de correo del usuario
  window.location.href = `mailto:${destinatario}?subject=${asunto}&body=${cuerpo}`
}
</script>

<template>
  <div class="pagina-detalle">
    
    <div class="hero-detalle hero-tanques" :style="{ backgroundImage: `linear-gradient(rgba(1, 33, 105, 0.7), rgba(1, 33, 105, 0.8)), url(${fondoTanques})`, backgroundSize: 'cover', backgroundPosition: 'center' }">
      <div class="contenedor-ancho contenido-hero">
        <h1 class="titulo-hero">Tanques de Pruebas</h1>
        <p class="subtitulo-hero">Instalaciones experimentales para ensayos controlados, calibración y biología.</p>
      </div>
    </div>

    <div class="contenedor-ancho seccion-principal">
      <div class="grid-dos-columnas">
        
        <div class="columna-ficha">
          <h2 class="titulo-seccion-pequeno">Ficha Técnica</h2>
          
          <div class="bloque-info">
            <h3>Descripción General</h3>
            <p>El SIO dispone de tanques de pruebas de alta capacidad diseñados para la calibración de sensores, ensayos de fatiga de materiales y simulaciones de condiciones marinas controladas.</p>
          </div>

          <div class="bloque-info">
            <h3>Especificaciones Principales</h3>
            <ul class="lista-especificaciones">
              <!-- Volumen total y rango de temperatura: pendientes de los datos reales -->
              <li><strong>Control de Salinidad:</strong> Sistema automatizado</li>
              <li><strong>Iluminación:</strong> Espectro regulable para fotosíntesis</li>
              <li><strong>Filtración:</strong> Filtros UV y biológicos integrados</li>
            </ul>
          </div>
        </div>

        <div class="columna-reserva">
          <div class="tarjeta-reserva">
            <div class="cabecera-reserva">
              <h2>Solicitud de Uso</h2>
              <span class="badge-operativa">OPERATIVA</span>
            </div>
            
            <div class="paso-reserva">
              <p><strong>Paso 1: Selecciona los días</strong></p>
              <p class="texto-explicativo">Haz clic en los días disponibles (en blanco) del calendario que necesites reservar.</p>
              
              <div class="calendario-placeholder mt-3">
                <div class="cabecera-mes">
                  <button type="button" class="btn-mes" @click="mesAnterior" :class="{ 'oculto': !hayMesAnterior }">❮</button>
                  <span class="mes-actual">{{ nombreMes }}</span>
                  <button type="button" class="btn-mes" @click="mesSiguiente" :class="{ 'oculto': !hayMesSiguiente }">❯</button>
                </div>

                <div class="grid-calendario">
                   <div v-for="dia in diasMesVisible" :key="dia" 
                        class="dia" 
                        :class="{ 
                          'ocupado': esOcupado(dia), 
                          'seleccionado': estaSeleccionado(dia) 
                        }"
                        @click="toggleDia(dia)">
                     {{ dia }}
                   </div>
                </div>
              </div>
            </div>

            <div class="paso-reserva mt-4 formulario-animado" v-if="diasSeleccionados.length > 0">
              <p><strong>Paso 2: Detalles de la solicitud</strong></p>
              
              <form @submit.prevent="enviarSolicitud" class="formulario-tanques">
                
                <div class="grupo-input">
                  <label>Días marcados:</label>
                  <div class="contenedor-tags">
                    <span v-for="fecha in fechasSeleccionadas" :key="fecha" class="tag-dia">{{ fecha }}</span>
                  </div>
                </div>

                <div class="grupo-input mt-3">
                  <label for="proposito">Propósito de las pruebas:</label>
                  <textarea id="proposito" v-model="proposito" rows="3" placeholder="Ej: Calibración de sensores de oxígeno PREsens..." required></textarea>
                </div>

                <div class="grupo-input mt-3">
                  <label for="grua">¿Vas a utilizar la grúa de carga?</label>
                  <select id="grua" v-model="necesitaGrua">
                    <option value="No">No, no será necesaria</option>
                    <option value="Sí">Sí, necesitaremos la grúa</option>
                  </select>
                </div>

                <button type="submit" class="btn-enviar mt-4">ENVIAR SOLICITUD AL SIO</button>
              </form>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.pagina-detalle { background-color: #f4f7f9; min-height: 100vh; padding-bottom: 80px; }

.hero-detalle { padding: 120px 0 60px 0; color: white; }
.contenido-hero { position: relative; display: flex; flex-direction: column; align-items: flex-start; }
.titulo-hero { font-size: 3rem; font-weight: bold; margin: 0 0 15px 0; position: relative; display: inline-block; padding-bottom: 10px; }
.titulo-hero::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 5px; background-color: #8cc63f; }
.subtitulo-hero { font-size: 1.15rem; color: #e0e6ed; max-width: 800px; margin: 0; }

.seccion-principal { margin-top: 40px; }
.grid-dos-columnas { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }

.columna-ficha { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); height: fit-content; }
.titulo-seccion-pequeno { color: #012169; font-size: 1.8rem; border-bottom: 2px solid #0086c0; padding-bottom: 10px; margin-bottom: 30px; margin-top: 0; }
.bloque-info { margin-bottom: 30px; }
.bloque-info h3 { color: #0086c0; font-size: 1.2rem; margin-bottom: 15px; }
.bloque-info p { color: #444; line-height: 1.6; }
.lista-especificaciones { list-style-type: none; padding: 0; }
.lista-especificaciones li { margin-bottom: 12px; color: #444; line-height: 1.5; padding-left: 15px; position: relative; }
.lista-especificaciones li::before { content: '•'; color: #0086c0; font-weight: bold; position: absolute; left: 0; }

.tarjeta-reserva { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
.cabecera-reserva { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 25px; }
.cabecera-reserva h2 { color: #012169; font-size: 1.5rem; margin: 0; }
.badge-operativa { background-color: #e6f4ea; color: #1e8e3e; padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; border: 1px solid #1e8e3e; }

.paso-reserva p { color: #444; margin-bottom: 15px; }
.texto-explicativo { color: #555; font-size: 0.95rem; margin-bottom: 10px; }

.mt-3 { margin-top: 15px; }
.mt-4 { margin-top: 30px; }

/* CALENDARIO INTERACTIVO */
.cabecera-mes { display: flex; justify-content: space-between; align-items: center; background-color: #012169; color: white; padding: 10px 15px; border-radius: 8px 8px 0 0; }
.mes-actual { font-weight: bold; font-size: 1.1rem; }
.btn-mes { background: transparent; border: none; color: white; font-size: 1.2rem; cursor: pointer; transition: transform 0.2s; }
.btn-mes:hover { transform: scale(1.2); }
.oculto { visibility: hidden; }

.grid-calendario { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; text-align: center; padding: 10px; background: #fbfbfb; border: 1px solid #eee; border-top: none; border-radius: 0 0 8px 8px; }
.dia { background: #f4f7f9; padding: 10px 0; border-radius: 4px; color: #555; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; }

/* Estados del día */
.dia:hover:not(.ocupado) { background: #e0f2fe; }
.dia.ocupado { background: #ffebee; color: #d32f2f; font-weight: bold; cursor: not-allowed; opacity: 0.7; }
.dia.seleccionado { background: #0086c0; color: white; font-weight: bold; transform: scale(1.05); box-shadow: 0 2px 5px rgba(0,0,0,0.2); }

/* ESTILOS DEL FORMULARIO */
.formulario-animado { animation: fadeIn 0.4s ease-out; border-top: 2px dashed #eee; padding-top: 25px; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

.grupo-input { display: flex; flex-direction: column; gap: 8px; }
.grupo-input label { font-size: 0.95rem; font-weight: bold; color: #012169; }
.grupo-input textarea, .grupo-input select { padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-family: inherit; font-size: 0.95rem; }
.grupo-input textarea:focus, .grupo-input select:focus { outline: none; border-color: #0086c0; }

.contenedor-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-dia { background-color: #e8f4fd; color: #0086c0; border: 1px solid #bce0fd; padding: 4px 10px; border-radius: 15px; font-size: 0.85rem; font-weight: bold; }

.btn-enviar { background-color: #0086c0; color: white; padding: 14px; border: none; border-radius: 6px; font-weight: bold; width: 100%; cursor: pointer; transition: background 0.3s; font-size: 1rem; }
.btn-enviar:hover { background-color: #012169; }

@media (max-width: 900px) { .grid-dos-columnas { grid-template-columns: 1fr; } }
</style>