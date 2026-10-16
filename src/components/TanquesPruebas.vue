<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCalendarioReservas } from '../composables/useCalendarioReservas'
import fondoTanques from '../assets/tanques.jpg'

const { t } = useI18n()
const {
  nombreMes, diasMesVisible, hayMesAnterior, hayMesSiguiente, mesAnterior, mesSiguiente,
  diasSeleccionados, esOcupado, toggleDia, estaSeleccionado, fechasSeleccionadas
} = useCalendarioReservas()

// --- FORMULARIO ---
const proposito = ref('')
const necesitaGrua = ref('no')

// Abre el correo del usuario con la solicitud preparada
const enviarSolicitud = () => {
  if (diasSeleccionados.value.length === 0 || proposito.value.trim() === '') {
    alert(t('tanques.faltanDatos'))
    return
  }
  const destinatario = "sio@icm.csic.es"
  const asunto = encodeURIComponent(t('tanques.correo.asunto'))
  const grua = necesitaGrua.value === 'si' ? t('tanques.correo.gruaSi') : t('tanques.correo.gruaNo')
  const cuerpo = encodeURIComponent(
    `${t('tanques.correo.saludo')}\n\n` +
    `${t('tanques.correo.intro')}\n\n` +
    `📅 ${t('tanques.correo.dias')}:\n- ${fechasSeleccionadas.value.join('\n- ')}\n\n` +
    `📋 ${t('tanques.correo.proposito')}:\n${proposito.value}\n\n` +
    `🏗️ ${t('tanques.correo.grua')}:\n${grua}\n\n` +
    `${t('tanques.correo.despedida')}`
  )
  window.location.href = `mailto:${destinatario}?subject=${asunto}&body=${cuerpo}`
}
</script>

<template>
  <div class="pagina-detalle">
    
    <div class="hero-detalle hero-tanques" :style="{ backgroundImage: `linear-gradient(rgba(1, 33, 105, 0.7), rgba(1, 33, 105, 0.8)), url(${fondoTanques})`, backgroundSize: 'cover', backgroundPosition: 'center' }">
      <div class="contenedor-ancho contenido-hero">
        <h1 class="titulo-hero">{{ $t('tanques.titulo') }}</h1>
        <p class="subtitulo-hero">{{ $t('tanques.subtitulo') }}</p>
      </div>
    </div>

    <div class="contenedor-ancho seccion-principal">
      <div class="grid-dos-columnas">
        
        <div class="columna-ficha">
          <h2 class="titulo-seccion-pequeno">{{ $t('tanques.ficha') }}</h2>
          
          <div class="bloque-info">
            <h3>{{ $t('tanques.descripcionTitulo') }}</h3>
            <p>{{ $t('tanques.descripcion') }}</p>
          </div>

          <div class="bloque-info">
            <h3>{{ $t('tanques.especificaciones') }}</h3>
            <ul class="lista-especificaciones">
              <!-- Volumen total y rango de temperatura: pendientes de los datos reales -->
              <li><strong>{{ $t('tanques.salinidad') }}:</strong> {{ $t('tanques.salinidadTexto') }}</li>
              <li><strong>{{ $t('tanques.iluminacion') }}:</strong> {{ $t('tanques.iluminacionTexto') }}</li>
              <li><strong>{{ $t('tanques.filtracion') }}:</strong> {{ $t('tanques.filtracionTexto') }}</li>
            </ul>
          </div>
        </div>

        <div class="columna-reserva">
          <div class="tarjeta-reserva">
            <div class="cabecera-reserva">
              <h2>{{ $t('tanques.solicitud') }}</h2>
              <span class="badge-operativa">{{ $t('tanques.operativa') }}</span>
            </div>
            
            <div class="paso-reserva">
              <p><strong>{{ $t('tanques.paso1') }}</strong></p>
              <p class="texto-explicativo">{{ $t('tanques.paso1Texto') }}</p>
              
              <div class="calendario-placeholder mt-3">
                <div class="cabecera-mes">
                  <button type="button" class="btn-mes" @click="mesAnterior" :class="{ 'oculto': !hayMesAnterior }" :aria-label="$t('tanques.mesAnterior')">❮</button>
                  <span class="mes-actual">{{ nombreMes }}</span>
                  <button type="button" class="btn-mes" @click="mesSiguiente" :class="{ 'oculto': !hayMesSiguiente }" :aria-label="$t('tanques.mesSiguiente')">❯</button>
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
              <p><strong>{{ $t('tanques.paso2') }}</strong></p>
              
              <form @submit.prevent="enviarSolicitud" class="formulario-tanques">
                
                <div class="grupo-input">
                  <label>{{ $t('tanques.diasMarcados') }}:</label>
                  <div class="contenedor-tags">
                    <span v-for="fecha in fechasSeleccionadas" :key="fecha" class="tag-dia">{{ fecha }}</span>
                  </div>
                </div>

                <div class="grupo-input mt-3">
                  <label for="proposito">{{ $t('tanques.proposito') }}:</label>
                  <textarea id="proposito" v-model="proposito" rows="3" :placeholder="$t('tanques.propositoPh')" required></textarea>
                </div>

                <div class="grupo-input mt-3">
                  <label for="grua">{{ $t('tanques.grua') }}</label>
                  <select id="grua" v-model="necesitaGrua">
                    <option value="no">{{ $t('tanques.gruaNo') }}</option>
                    <option value="si">{{ $t('tanques.gruaSi') }}</option>
                  </select>
                </div>

                <button type="submit" class="btn-enviar mt-4">{{ $t('tanques.enviar') }}</button>
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