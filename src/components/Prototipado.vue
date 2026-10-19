<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
const fondoInstrumentacion = '/instrumentacion.webp'

const { t } = useI18n()

// Solicitud: abre el correo del usuario con los datos preparados
const solicitud = ref({ proyecto: '', pieza: '', requisitos: '' })

const enviarSolicitud = () => {
  const { proyecto, pieza, requisitos } = solicitud.value
  const asunto = encodeURIComponent(t('prototipado.correo.asunto', { pieza }))
  const cuerpo = encodeURIComponent(
    `${t('prototipado.correo.saludo')}\n\n` +
    `${t('prototipado.correo.intro')}\n\n` +
    `${t('prototipado.correo.proyecto')}: ${proyecto}\n` +
    `${t('prototipado.correo.pieza')}: ${pieza}\n\n` +
    `${requisitos}\n\n` +
    `${t('prototipado.correo.despedida')}`
  )
  window.location.href = `mailto:sio@icm.csic.es?subject=${asunto}&body=${cuerpo}`
}
</script>

<template>
  <div class="prototipado-page">
    <div class="fondo-prototipado" :style="{ backgroundImage: backgroundStyle }"></div>
    
    <div class="contenedor-ancho contenido-prototipado">
      <h1 class="titulo-seccion">{{ $t('prototipado.titulo') }}</h1>
      <p class="subtitulo">{{ $t('prototipado.subtitulo') }}</p>

      <div class="tarjeta-contenido">
        
        <!-- 🌟 PRESENTACIÓN DEL SERVICIO -->
        <div class="intro-servicio">
          <p class="texto-destacado">{{ $t('prototipado.intro') }}</p>
        </div>

        <!-- ⚙️ TECNOLOGÍAS Y CAPACIDADES -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">{{ $t('prototipado.capacidadesTitulo') }}</h3>
          <div class="grid-fases">
            <div v-for="(capacidad, i) in $tm('prototipado.capacidades')" :key="i" class="fase-card">
              <span class="fase-num">{{ String(i + 1).padStart(2, '0') }}</span>
              <h4>{{ $rt(capacidad.titulo) }}</h4>
              <p>{{ $rt(capacidad.texto) }}</p>
            </div>
          </div>
        </div>

        <!-- 📝 FORMULARIO DE SOLICITUD -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">{{ $t('prototipado.solicitarTitulo') }}</h3>
          <form class="formulario-prototipado" @submit.prevent="enviarSolicitud">
            <div class="grupo-input">
              <label for="pro-proyecto" class="solo-lectores">{{ $t('prototipado.proyecto') }}</label>
              <input type="text" id="pro-proyecto" v-model="solicitud.proyecto" :placeholder="$t('prototipado.proyecto')" required>
            </div>
            <div class="grupo-input">
              <label for="pro-pieza" class="solo-lectores">{{ $t('prototipado.pieza') }}</label>
              <input type="text" id="pro-pieza" v-model="solicitud.pieza" :placeholder="$t('prototipado.piezaPh')" required>
            </div>
            <div class="grupo-input">
              <label for="pro-requisitos" class="solo-lectores">{{ $t('prototipado.requisitos') }}</label>
              <textarea id="pro-requisitos" v-model="solicitud.requisitos" rows="4" :placeholder="$t('prototipado.requisitosPh')" required></textarea>
            </div>
            <p class="aviso-correo">{{ $t('prototipado.avisoCorreo') }} <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a>.</p>
            <button type="submit" class="btn-solicitar">{{ $t('prototipado.enviar') }}</button>
          </form>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.aviso-correo { font-size: 0.85rem; color: #666; margin: 0 0 12px; }
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