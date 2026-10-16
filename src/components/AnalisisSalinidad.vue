<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Lógica del formulario
const proyecto = ref('')
const numeroBotellas = ref('')
const fechaRecogida = ref('')
const fechaEntrega = ref('')

// Abre el correo del usuario con la solicitud preparada
const enviarSolicitud = () => {
  if (!proyecto.value || !numeroBotellas.value || !fechaRecogida.value || !fechaEntrega.value) {
    alert(t('salinidad.faltanDatos'))
    return
  }
  const destinatario = "sio@icm.csic.es"
  const asunto = encodeURIComponent(t('salinidad.correo.asunto', { proyecto: proyecto.value }))
  const cuerpo = encodeURIComponent(
    `${t('salinidad.correo.saludo')}\n\n` +
    `${t('salinidad.correo.intro')}\n` +
    `${t('salinidad.correo.proyecto')}: ${proyecto.value}\n` +
    `${t('salinidad.correo.botellas')}: ${numeroBotellas.value}\n` +
    `${t('salinidad.correo.recogida')}: ${fechaRecogida.value}\n` +
    `${t('salinidad.correo.entrega')}: ${fechaEntrega.value}`
  )
  window.location.href = `mailto:${destinatario}?subject=${asunto}&body=${cuerpo}`
}
</script>

<template>
  <div class="pagina-detalle">
    
    <div class="hero-detalle hero-salinidad">
      <div class="contenedor-ancho contenido-hero">
        <h1 class="titulo-hero">{{ $t('salinidad.titulo') }}</h1>
        <p class="subtitulo-hero">{{ $t('salinidad.subtitulo') }}</p>
      </div>
    </div>

    <div class="contenedor-ancho seccion-principal">
      <div class="grid-dos-columnas">
        
        <div class="columna-ficha">
          <h2 class="titulo-seccion-pequeno">{{ $t('salinidad.ficha') }}</h2>
          
          <div class="bloque-info">
            <h3>{{ $t('salinidad.descripcionTitulo') }}</h3>
            <p>{{ $t('salinidad.descripcion') }}</p>
          </div>

          <div class="bloque-info">
            <h3>{{ $t('salinidad.especificaciones') }}</h3>
            <ul class="lista-especificaciones">
              <li><strong>{{ $t('salinidad.equipo') }}:</strong> {{ $t('salinidad.equipoTexto') }}</li>
              <li><strong>{{ $t('salinidad.precision') }}:</strong> {{ $t('salinidad.precisionTexto') }}</li>
              <li><strong>{{ $t('salinidad.calibracion') }}:</strong> {{ $t('salinidad.calibracionTexto') }}</li>
              <li><strong>{{ $t('salinidad.control') }}:</strong> {{ $t('salinidad.controlTexto') }}</li>
            </ul>
          </div>
        </div>

        <div class="columna-reserva">
          <div class="tarjeta-reserva">
            <div class="cabecera-reserva">
              <h2>{{ $t('salinidad.solicitud') }}</h2>
              <span class="badge-operativa">{{ $t('salinidad.operativa') }}</span>
            </div>
            
            <p class="texto-explicativo">{{ $t('salinidad.explicacion') }}</p>
            
            <form @submit.prevent="enviarSolicitud" class="formulario-salinidad">
              <div class="grupo-input">
                <label for="sal-proyecto">{{ $t('salinidad.proyecto') }}:</label>
                <input type="text" id="sal-proyecto" v-model="proyecto" required>
              </div>
              <div class="grupo-input mt-3">
                <label for="sal-botellas">{{ $t('salinidad.botellas') }}:</label>
                <input type="number" id="sal-botellas" min="1" v-model="numeroBotellas" required>
              </div>
              <div class="grid-fechas mt-3">
                <div class="grupo-input">
                  <label for="sal-recogida">{{ $t('salinidad.recogida') }}:</label>
                  <input type="date" id="sal-recogida" v-model="fechaRecogida" required>
                </div>
                <div class="grupo-input">
                  <label for="sal-entrega">{{ $t('salinidad.entrega') }}:</label>
                  <input type="date" id="sal-entrega" v-model="fechaEntrega" required>
                </div>
              </div>
              <button type="submit" class="btn-enviar mt-4">{{ $t('salinidad.enviar') }}</button>
            </form>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* ESTILOS EXACTOS DE LA CABECERA (HERO) DE PELAGIA */
.hero-salinidad { 
  background-image: linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.8)), url('/salinometro.jpg');
  background-size: cover; 
  background-position: center 30%; 
}

.hero-detalle { 
  padding: 120px 0 80px 0; 
  color: white; 
}

.contenido-hero { 
  display: flex; 
  flex-direction: column; 
  align-items: flex-start; 
}

.titulo-hero { 
  font-size: 3rem; 
  font-weight: bold; 
  margin: 0 0 15px 0; 
  position: relative; 
  display: inline-block; 
  padding-bottom: 10px; 
}

/* LA LÍNEA VERDE DEBAJO DEL TÍTULO */
.titulo-hero::after { 
  content: ''; 
  position: absolute; 
  bottom: 0; 
  left: 0; 
  width: 100%; 
  height: 5px; 
  background-color: #8cc63f; 
}

.subtitulo-hero { 
  font-size: 1.15rem; 
  color: #e0e6ed; 
  max-width: 800px; 
  margin: 0; 
}

/* RESTO DEL DISEÑO */
.pagina-detalle { background-color: #f4f7f9; min-height: 100vh; padding-bottom: 80px; }
.contenedor-ancho { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.seccion-principal { margin-top: -40px; position: relative; z-index: 5; }
.grid-dos-columnas { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }

.columna-ficha { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); height: fit-content; }
.columna-reserva { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); height: fit-content; }

.titulo-seccion-pequeno { color: #012169; font-size: 1.5rem; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }
.bloque-info { margin-bottom: 25px; }
.bloque-info h3 { color: #0086c0; margin-bottom: 10px; font-size: 1.15rem; }
.bloque-info p { color: #444; line-height: 1.6; margin: 0; }

.lista-especificaciones { list-style: none; padding: 0; margin: 10px 0 0 0; }
.lista-especificaciones li { margin-bottom: 8px; padding-left: 15px; position: relative; color: #444; line-height: 1.5; }
.lista-especificaciones li::before { content: '●'; color: #0086c0; position: absolute; left: 0; }

.cabecera-reserva { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }
.cabecera-reserva h2 { font-size: 1.3rem; color: #012169; margin: 0; }
.badge-operativa { background: #e6f4ea; color: #1e8e3e; padding: 4px 10px; border-radius: 15px; font-size: 0.75rem; font-weight: bold; border: 1px solid #1e8e3e; }
.texto-explicativo { color: #555; font-size: 0.95rem; margin-bottom: 20px; }

.grupo-input { display: flex; flex-direction: column; gap: 5px; }
.grupo-input label { font-weight: bold; font-size: 0.9rem; color: #012169; }
.grupo-input input { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; }
.grupo-input input:focus { outline: none; border-color: #0086c0; }

.grid-fechas { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.btn-enviar { background: #0086c0; color: white; border: none; padding: 12px; border-radius: 4px; font-weight: bold; cursor: pointer; width: 100%; transition: background 0.3s; }
.btn-enviar:hover { background: #012169; }

.mt-3 { margin-top: 15px; }
.mt-4 { margin-top: 20px; }

@media (max-width: 900px) { .grid-dos-columnas { grid-template-columns: 1fr; } }
</style>