<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import fondoInstrumentacion from '../assets/instrumentacion.jpg'

const { t } = useI18n()

// Icono de cada tipo de instrumento (los textos están en fondeos.instrumentos)
const iconosInstrumentos = ['🌊', '🌡️', '🧂', '🔵', '📊', '🟢', '🌿', '🧪', '🌀', '🪣']

// Solicitud: abre el correo del usuario con los datos preparados
const solicitud = ref({ proyecto: '', inicio: '', retirada: '', descripcion: '' })

const enviarSolicitud = () => {
  const { proyecto, inicio, retirada, descripcion } = solicitud.value
  const asunto = encodeURIComponent(t('fondeos.correo.asunto', { proyecto }))
  const cuerpo = encodeURIComponent(
    `${t('fondeos.correo.saludo')}\n\n` +
    `${t('fondeos.correo.intro')}\n\n` +
    `${t('fondeos.correo.proyecto')}: ${proyecto}\n` +
    `${t('fondeos.correo.inicio')}: ${inicio}\n` +
    `${t('fondeos.correo.retirada')}: ${retirada}\n\n` +
    `${descripcion}\n\n` +
    `${t('fondeos.correo.despedida')}`
  )
  window.location.href = `mailto:sio@icm.csic.es?subject=${asunto}&body=${cuerpo}`
}
</script>

<template>
  <div class="fondeos-page">
    <div class="fondo-fondeos" :style="{ backgroundImage: backgroundStyle }"></div>
    
    <div class="contenedor-ancho contenido-fondeos">
      <h1 class="titulo-seccion">{{ $t('fondeos.titulo') }}</h1>
      <p class="subtitulo">{{ $t('fondeos.subtitulo') }}</p>

      <div class="tarjeta-contenido">
        
        <!-- 🌟 PRESENTACIÓN DEL SERVICIO (NUEVO) -->
        <div class="intro-servicio">
          <p class="texto-destacado">{{ $t('fondeos.intro') }}</p>
          <p class="nota-usuario"><em>{{ $t('fondeos.nota') }}</em></p>
        </div>

        <!-- ⚙️ FASES DEL SERVICIO -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">{{ $t('fondeos.fasesTitulo') }}</h3>
          <div class="grid-fases">
            <div v-for="(fase, i) in $tm('fondeos.fases')" :key="i" class="fase-card">
              <span class="fase-num">{{ String(i + 1).padStart(2, '0') }}</span>
              <h4>{{ $rt(fase.titulo) }}</h4>
              <p>{{ $rt(fase.texto) }}</p>
            </div>
          </div>
        </div>

        <!-- 📊 TIPOS DE INSTRUMENTACIÓN INTEGRABLE -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">{{ $t('fondeos.instrumentosTitulo') }}</h3>
          <p class="texto-explicativo">{{ $t('fondeos.instrumentosTexto') }}</p>
          <div class="grid-instrumentos">
            <div v-for="(inst, i) in $tm('fondeos.instrumentos')" :key="i" class="inst-item">
              <span aria-hidden="true">{{ iconosInstrumentos[i] }}</span> {{ $rt(inst.nombre) }} <span class="inst-desc">{{ $rt(inst.texto) }}</span>
            </div>
          </div>
        </div>

        <!-- 📝 FORMULARIO DE SOLICITUD -->
        <div class="seccion-bloque">
          <h3 class="subtitulo-bloque">{{ $t('fondeos.solicitarTitulo') }}</h3>
          <form class="formulario-fondeo" @submit.prevent="enviarSolicitud">
            <div class="grupo-input">
              <label for="fnd-proyecto" class="solo-lectores">{{ $t('fondeos.proyecto') }}</label>
              <input type="text" id="fnd-proyecto" v-model="solicitud.proyecto" :placeholder="$t('fondeos.proyecto')" required>
            </div>
            <div class="fila-fechas">
              <div class="input-fecha-box">
                <label for="fnd-inicio">{{ $t('fondeos.inicio') }}:</label>
                <input type="date" id="fnd-inicio" v-model="solicitud.inicio" required>
              </div>
              <div class="input-fecha-box">
                <label for="fnd-retirada">{{ $t('fondeos.retirada') }}:</label>
                <input type="date" id="fnd-retirada" v-model="solicitud.retirada" required>
              </div>
            </div>
            <div class="grupo-input">
              <label for="fnd-descripcion" class="solo-lectores">{{ $t('fondeos.descripcion') }}</label>
              <textarea id="fnd-descripcion" v-model="solicitud.descripcion" rows="4" :placeholder="$t('fondeos.descripcionPh')" required></textarea>
            </div>
            <p class="aviso-correo">{{ $t('fondeos.avisoCorreo') }} <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a>.</p>
            <button type="submit" class="btn-solicitar">{{ $t('fondeos.enviar') }}</button>
          </form>
        </div>

        <!-- ⚓ ESTADO ACTUAL DE FONDEOS -->
        <div class="seccion-bloque" style="margin-top: 40px;">
          <h3 class="subtitulo-bloque">{{ $t('fondeos.estadoTitulo') }}</h3>
          <div class="estados-container">
            <div class="estado-grupo">
              <span class="punto-verde"></span> <strong>{{ $t('fondeos.activos') }}</strong>
              <div class="item-estado">
                <strong>FND-001</strong> - Cañón de Blanes <br><small>{{ $t('fondeos.ip') }}: Ivan Masmitja</small>
              </div>
            </div>
            <div class="estado-grupo">
              <span class="punto-gris"></span> <strong>{{ $t('fondeos.retirados') }}</strong>
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
.aviso-correo { font-size: 0.85rem; color: #666; margin: 0 0 12px; }
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