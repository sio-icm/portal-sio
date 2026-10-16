<script setup>
import { ref } from 'vue'
// Importamos tu imagen de fondo
import fondoPelagia from '../assets/Pelagia.jpg'

// --- LÓGICA DEL CALENDARIO (6 MESES VISTA) ---
const meses = [
  'Mayo 2026', 'Junio 2026', 'Julio 2026', 'Agosto 2026',
  'Septiembre 2026', 'Octubre 2026', 'Noviembre 2026'
]

const mesActualIndex = ref(0)

const mesAnterior = () => { if (mesActualIndex.value > 0) mesActualIndex.value-- }
const mesSiguiente = () => { if (mesActualIndex.value < meses.length - 1) mesActualIndex.value++ }

const diasSeleccionados = ref([])

// Simulador de días ocupados (distribuidos por meses)
const esOcupado = (dia, mesIndex) => {
  if (mesIndex === 0 && [12, 13, 14].includes(dia)) return true // Mayo
  if (mesIndex === 1 && [2, 5, 14, 15, 22].includes(dia)) return true // Junio
  if (mesIndex === 2 && [10, 11, 12, 28, 29].includes(dia)) return true // Julio
  if (mesIndex === 3 && [1, 2, 3, 20, 21].includes(dia)) return true // Agosto
  if (mesIndex === 4 && [15, 16, 17].includes(dia)) return true // Septiembre
  return false
}

// Seleccionar un día, guardando también el mes para el correo
const toggleDia = (dia) => {
  if (esOcupado(dia, mesActualIndex.value)) return

  const fechaStr = `${dia} de ${meses[mesActualIndex.value]}`
  const index = diasSeleccionados.value.indexOf(fechaStr)

  if (index === -1) {
    diasSeleccionados.value.push(fechaStr) 
  } else {
    diasSeleccionados.value.splice(index, 1) 
  }
}

// Comprueba si un día de este mes está en la lista de seleccionados
const estaSeleccionado = (dia) => {
  const fechaStr = `${dia} de ${meses[mesActualIndex.value]}`
  return diasSeleccionados.value.includes(fechaStr)
}

// Abre el correo del usuario con la solicitud preparada (sin servicios externos)
const enviarSolicitud = () => {
  if (diasSeleccionados.value.length === 0) return
  const destinatario = "sio@icm.csic.es"
  const asunto = encodeURIComponent("Solicitud de salida: Embarcación Pelagia")
  const cuerpo = encodeURIComponent(
    `Hola equipo del SIO,\n\n` +
    `Me gustaría solicitar la embarcación Pelagia para estos días:\n` +
    `- ${diasSeleccionados.value.join('\n- ')}\n\n` +
    `Adjunto el Plan de Campaña firmado.\n\n` +
    `Quedo a la espera de vuestra confirmación.\n\nUn saludo.`
  )
  window.location.href = `mailto:${destinatario}?subject=${asunto}&body=${cuerpo}`
}
</script>

<template>
  <div class="servicios-hub">
    <div class="fondo-servicios" :style="{ backgroundImage: `linear-gradient(rgba(1, 33, 105, 0.75), rgba(1, 33, 105, 0.9)), url(${fondoPelagia})` }"></div>

    <div class="contenido-hub">
      <h1 class="titulo-seccion">Plataforma Pelagia</h1>
      <p class="subtitulo">Información técnica, disponibilidad y gestión de reservas de la embarcación del SIO.</p>

      <div class="grid-layout">
        
        <div class="seccion-bloque ficha-wiki">
          <h2 class="titulo-fija">Ficha Técnica</h2>
          
          <div class="bloque-subcat">
            <h3 class="titulo-subcat">Descripción General</h3>
            <p class="texto-descripcion">
              La Pelagia es la embarcación de trabajo costero del Servicio de Ingeniería Oceanográfica (SIO). 
              Está diseñada y equipada para dar soporte a operaciones de buceo científico, despliegue y recuperación 
              de instrumentación oceanográfica, y muestreos costeros.
            </p>
          </div>

          <div class="bloque-subcat">
            <h3 class="titulo-subcat">Especificaciones Principales</h3>
            <ul class="lista-wiki">
              <li>
                <div class="item-header">
                  <span class="punto-azul">•</span>
                  <span class="enlace-wiki">Características Básicas</span>
                </div>
                <div class="caja-gris-wiki">
                  <strong>- Eslora:</strong> [Añadir metros] m<br>
                  <strong>- Manga:</strong> [Añadir metros] m<br>
                  <strong>- Motorización:</strong> [Añadir CV/Marca]<br>
                  <strong>- Capacidad máxima:</strong> [Añadir pax] personas (incluyendo patrón)
                </div>
              </li>
              <li>
                <div class="item-header">
                  <span class="punto-azul">•</span>
                  <span class="enlace-wiki">Equipamiento a bordo</span>
                </div>
                <div class="caja-gris-wiki">
                  <strong>- Navegación:</strong> GPS / Sonda plotter integrado.<br>
                  <strong>- Comunicación:</strong> Emisora VHF fija.<br>
                  <strong>- Maniobra:</strong> Pescante / Maquinilla para perfiladores ligeros (CTD, roseta pequeña).<br>
                  <strong>- Seguridad:</strong> Material de seguridad completo zona [X].
                </div>
              </li>
            </ul>
          </div>

          <div class="bloque-subcat">
            <h3 class="titulo-subcat">Normativa de Uso</h3>
            <div class="caja-desc">
              <p>
                Para el uso de la embarcación Pelagia es estrictamente obligatorio contar con la aprobación del SIO. 
                La plataforma Pelagia está capitaneada por Brian Nicolás, profesional con amplia experiencia demostrable 
                en navegación costera y soporte a operaciones oceanográficas. Su liderazgo a bordo garantiza la seguridad 
                de la tripulación y la correcta ejecución de los protocolos de trabajo marítimo. Su perfil resolutivo y 
                su actitud colaborativa facilitan enormemente la coordinación de las actividades científicas durante las campañas.  
              </p>
            </div>
          </div>
        </div>

        <div class="seccion-bloque ficha-gestion">
          <div class="cabecera-estado">
            <h2 class="titulo-fija">Solicitud de Uso</h2>
            <span class="badge-grande disponible">Operativa</span>
          </div>
          
          <p style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Paso 1: Descarga las normas y plan de campaña.</p>
          <div class="descarga-box-pequena">
          <a href="/Plan_Campana_Pelagia.docx" download="Plan_Campana_Pelagia.docx" class="link-dl-mini">
           ⬇ Descargar Plan de Campaña
          </a>
          </div>

          <div class="calendario-mini">
            <h3 class="titulo-mini">Paso 2: Selecciona los días de salida</h3>
            
            <div class="cabecera-mes">
              <button type="button" class="btn-mes" @click="mesAnterior" :class="{ 'oculto': mesActualIndex === 0 }">❮</button>
              <span class="mes-actual">{{ meses[mesActualIndex] }}</span>
              <button type="button" class="btn-mes" @click="mesSiguiente" :class="{ 'oculto': mesActualIndex === meses.length - 1 }">❯</button>
            </div>

            <div class="grid-dias">
              <div 
                v-for="dia in 31" 
                :key="dia" 
                @click="toggleDia(dia)" 
                :class="['dia', { 
                  ocupado: esOcupado(dia, mesActualIndex), 
                  seleccionado: estaSeleccionado(dia), 
                  disponible: !esOcupado(dia, mesActualIndex) 
                }]"
              >
                {{ dia }}
              </div>
            </div>
            <p class="leyenda">* Gris: Disponible | Azul: Ocupado/Mantenimiento | Verde: Tu selección</p>
          </div>

          <div class="formulario-reserva">
            <h3 class="titulo-mini" style="margin-top: 20px;">Paso 3: Envía tu Plan</h3>
            <p style="font-size: 0.85rem; color: #666; margin: 0 0 10px;">
              Al pulsar el botón se abrirá tu programa de correo con la solicitud preparada para enviar a
              <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a>.
              <strong>Adjunta el Plan de Campaña firmado</strong> antes de enviarlo.
            </p>

            <button 
              type="button"
              @click="enviarSolicitud"
              :class="['btn-submit', { 'btn-desactivado': diasSeleccionados.length === 0 }]"
              :disabled="diasSeleccionados.length === 0"
              :title="diasSeleccionados.length === 0 ? 'Selecciona al menos un día' : ''"
            >
              📧 Preparar correo de solicitud
            </button>
            <p v-if="diasSeleccionados.length === 0" class="aviso-dias">Selecciona al menos un día en el calendario superior para poder enviar.</p>
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