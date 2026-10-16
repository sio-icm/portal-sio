<script setup>
import { useI18n } from 'vue-i18n'
import { useCalendarioReservas } from '../composables/useCalendarioReservas'
import fondoPelagia from '../assets/Pelagia.jpg'

const { t } = useI18n()
const {
  nombreMes, diasMesVisible, hayMesAnterior, hayMesSiguiente, mesAnterior, mesSiguiente,
  diasSeleccionados, esOcupado, toggleDia, estaSeleccionado, fechasSeleccionadas
} = useCalendarioReservas()

// Abre el correo del usuario con la solicitud preparada (sin servicios externos)
const enviarSolicitud = () => {
  if (diasSeleccionados.value.length === 0) return
  const destinatario = "sio@icm.csic.es"
  const asunto = encodeURIComponent(t('pelagia.correo.asunto'))
  const cuerpo = encodeURIComponent(
    `${t('pelagia.correo.saludo')}\n\n` +
    `${t('pelagia.correo.intro')}\n` +
    `- ${fechasSeleccionadas.value.join('\n- ')}\n\n` +
    `${t('pelagia.correo.adjunto')}\n\n` +
    `${t('pelagia.correo.despedida')}`
  )
  window.location.href = `mailto:${destinatario}?subject=${asunto}&body=${cuerpo}`
}
</script>

<template>
  <div class="servicios-hub">
    <div class="fondo-servicios" :style="{ backgroundImage: `linear-gradient(rgba(1, 33, 105, 0.75), rgba(1, 33, 105, 0.9)), url(${fondoPelagia})` }"></div>

    <div class="contenido-hub">
      <h1 class="titulo-seccion">{{ $t('pelagia.titulo') }}</h1>
      <p class="subtitulo">{{ $t('pelagia.subtitulo') }}</p>

      <div class="grid-layout">
        
        <div class="seccion-bloque ficha-wiki">
          <h2 class="titulo-fija">{{ $t('pelagia.ficha') }}</h2>
          
          <div class="bloque-subcat">
            <h3 class="titulo-subcat">{{ $t('pelagia.descripcionTitulo') }}</h3>
            <p class="texto-descripcion">{{ $t('pelagia.descripcion') }}</p>
          </div>

          <div class="bloque-subcat">
            <h3 class="titulo-subcat">{{ $t('pelagia.especificaciones') }}</h3>
            <ul class="lista-wiki">
              <!-- Características básicas (eslora, manga, motorización, capacidad):
                   pendientes de los datos reales de la embarcación -->
              <li>
                <div class="item-header">
                  <span class="punto-azul">•</span>
                  <span class="enlace-wiki">{{ $t('pelagia.equipamiento') }}</span>
                </div>
                <div class="caja-gris-wiki">
                  <strong>- {{ $t('pelagia.navegacion') }}:</strong> {{ $t('pelagia.navegacionTexto') }}<br>
                  <strong>- {{ $t('pelagia.comunicacion') }}:</strong> {{ $t('pelagia.comunicacionTexto') }}<br>
                  <strong>- {{ $t('pelagia.maniobra') }}:</strong> {{ $t('pelagia.maniobraTexto') }}<br>
                  <strong>- {{ $t('pelagia.seguridad') }}:</strong> {{ $t('pelagia.seguridadTexto') }}
                </div>
              </li>
            </ul>
          </div>

          <div class="bloque-subcat">
            <h3 class="titulo-subcat">{{ $t('pelagia.normativaTitulo') }}</h3>
            <div class="caja-desc">
              <p>{{ $t('pelagia.normativa') }}</p>
            </div>
          </div>
        </div>

        <div class="seccion-bloque ficha-gestion">
          <div class="cabecera-estado">
            <h2 class="titulo-fija">{{ $t('pelagia.solicitud') }}</h2>
            <span class="badge-grande disponible">{{ $t('pelagia.operativa') }}</span>
          </div>
          
          <p style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">{{ $t('pelagia.paso1') }}</p>
          <div class="descarga-box-pequena">
          <a href="/Plan_Campana_Pelagia.docx" download="Plan_Campana_Pelagia.docx" class="link-dl-mini">
           ⬇ {{ $t('pelagia.descargar') }}
          </a>
          </div>

          <div class="calendario-mini">
            <h3 class="titulo-mini">{{ $t('pelagia.paso2') }}</h3>
            
            <div class="cabecera-mes">
              <button type="button" class="btn-mes" @click="mesAnterior" :class="{ 'oculto': !hayMesAnterior }" :aria-label="$t('pelagia.mesAnterior')">❮</button>
              <span class="mes-actual">{{ nombreMes }}</span>
              <button type="button" class="btn-mes" @click="mesSiguiente" :class="{ 'oculto': !hayMesSiguiente }" :aria-label="$t('pelagia.mesSiguiente')">❯</button>
            </div>

            <div class="grid-dias">
              <div 
                v-for="dia in diasMesVisible" 
                :key="dia" 
                @click="toggleDia(dia)" 
                :class="['dia', { 
                  ocupado: esOcupado(dia), 
                  seleccionado: estaSeleccionado(dia), 
                  disponible: !esOcupado(dia) 
                }]"
              >
                {{ dia }}
              </div>
            </div>
            <p class="leyenda">{{ $t('pelagia.leyenda') }}</p>
          </div>

          <div class="formulario-reserva">
            <h3 class="titulo-mini" style="margin-top: 20px;">{{ $t('pelagia.paso3') }}</h3>
            <p style="font-size: 0.85rem; color: #666; margin: 0 0 10px;">
              {{ $t('pelagia.explicacion') }}
              <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a>.
              <strong>{{ $t('pelagia.adjunta') }}</strong> {{ $t('pelagia.explicacionFin') }}
            </p>

            <button 
              type="button"
              @click="enviarSolicitud"
              :class="['btn-submit', { 'btn-desactivado': diasSeleccionados.length === 0 }]"
              :disabled="diasSeleccionados.length === 0"
              :title="diasSeleccionados.length === 0 ? $t('pelagia.seleccionaDia') : ''"
            >
              📧 {{ $t('pelagia.preparar') }}
            </button>
            <p v-if="diasSeleccionados.length === 0" class="aviso-dias">{{ $t('pelagia.avisoDias') }}</p>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.servicios-hub { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }

.fondo-servicios { 
  position: absolute; top: 0; left: 0; width: 100%; height: 550px; 
  /* La imagen se gestiona dinámicamente en el template */
  background-size: cover; background-position: center; z-index: 0; 
}

.contenido-hub { position: relative; z-index: 10; padding-top: 120px; max-width: 1300px; margin: 0 auto; padding-left: 20px; padding-right: 20px; }

.titulo-seccion { color: white; font-size: 2.2rem; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; margin-bottom: 15px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 35px; max-width: 800px; }

.grid-layout { display: grid; grid-template-columns: 1.8fr 1.3fr; gap: 30px; }
.seccion-bloque { background: white; border-radius: 12px; padding: 35px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); min-height: auto; }
.titulo-fija { color: #012169; margin-top: 0; font-size: 1.6rem; margin-bottom: 25px; border-bottom: 2px solid #eee; padding-bottom: 10px; }

/* ZONA IZQUIERDA */
.bloque-subcat { margin-bottom: 30px; }
.titulo-subcat { font-size: 1.2rem; color: #0056b3; margin-bottom: 15px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
.texto-descripcion { color: #444; line-height: 1.6; font-size: 1rem; text-align: justify; }

.lista-wiki { list-style: none; padding-left: 0; margin: 0; }
.item-header { margin-bottom: 8px; font-size: 1.05rem; }
.punto-azul { color: #0056b3; margin-right: 8px; font-size: 1.2rem; line-height: 0; }
.enlace-wiki { color: #0056b3; font-weight: bold; }

.caja-gris-wiki { background-color: #f1f3f4; border-radius: 6px; padding: 15px 20px; margin-left: 15px; margin-bottom: 20px; font-family: 'Consolas', monospace; font-size: 0.9rem; color: #202124; line-height: 1.8; }
.caja-desc { background: #f8f9fa; padding: 15px; border-left: 4px solid #8cc63f; border-radius: 0 8px 8px 0; margin-bottom: 15px;}
.caja-desc p { margin: 0; color: #444; line-height: 1.6; font-size: 0.95rem; text-align: justify;}

/* PANEL DERECHO (GESTIÓN) */
.cabecera-estado { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px;}
.cabecera-estado .titulo-fija { border-bottom: none; margin-bottom: 0; padding-bottom: 0; font-size: 1.4rem;}

.badge-grande { padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; }
.badge-grande.disponible { background: #e6f4ea; color: #1e7e34; }
.badge-grande.ocupado { background: #fff4e5; color: #b45d00; }

.descarga-box-pequena { background: #eef5fa; padding: 10px 15px; border: 1px dashed #0086c0; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; font-size: 0.85rem; }
.link-dl-mini { color: #0086c0; font-weight: bold; text-decoration: none; font-size: 0.8rem; background: white; padding: 4px 8px; border-radius: 4px; border: 1px solid #0086c0;}

/* CALENDARIO INTERACTIVO PELAGIA */
.calendario-mini { margin-bottom: 20px; }
.titulo-mini { font-size: 1.1rem; color: #012169; margin-bottom: 10px; font-weight: bold; }

.cabecera-mes { display: flex; justify-content: space-between; align-items: center; background-color: #012169; color: white; padding: 10px 15px; border-radius: 6px 6px 0 0; margin-bottom: 5px; }
.mes-actual { font-weight: bold; font-size: 1rem; }
.btn-mes { background: transparent; border: none; color: white; font-size: 1.1rem; cursor: pointer; transition: transform 0.2s; }
.btn-mes:hover { transform: scale(1.2); }
.oculto { visibility: hidden; }

.grid-dias { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; }
.dia { padding: 8px; text-align: center; font-size: 0.85rem; border-radius: 4px; font-weight: bold; transition: 0.2s; user-select: none; }
.dia.disponible { background: #f0f0f0; color: #666; cursor: pointer; border: 1px solid transparent;}
.dia.disponible:hover { border-color: #8cc63f; }
.dia.ocupado { background: #0086c0; color: white; cursor: not-allowed; opacity: 0.6; }
.dia.seleccionado { background: #8cc63f; color: #012169; border: 1px solid #012169; transform: scale(1.05); }
.leyenda { font-size: 0.75rem; color: #999; margin-top: 10px; text-align: center; }

/* FORMULARIO */
.formulario-reserva { background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; margin-top: 15px; }
.form-grupo { margin-bottom: 15px; }
.form-grupo label { display: block; font-size: 0.9rem; color: #333; margin-bottom: 5px; font-weight: bold; }
.input-form { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.95rem; box-sizing: border-box; }

.btn-submit { width: 100%; background-color: #012169; color: white; border: none; padding: 15px; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 10px; }
.btn-submit:hover:not(.btn-desactivado) { background-color: #0056b3; transform: translateY(-2px); }
.btn-desactivado { background-color: #ccc; cursor: not-allowed; }
.aviso-dias { font-size: 0.75rem; color: #d32f2f; text-align: center; margin-top: 8px; font-weight: bold;}

@media (max-width: 992px) { .grid-layout { grid-template-columns: 1fr; } }
</style>