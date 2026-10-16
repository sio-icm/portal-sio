<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// --- FORMULARIO DE CONTACTO (se envía al backend del SIO) ---
const contacto = ref({ nombre: '', email: '', mensaje: '', web: '' })
const estadoContacto = ref('') // '', 'enviando', 'enviado', 'error'
const errorContacto = ref('')

const enviarContacto = async () => {
  estadoContacto.value = 'enviando'
  errorContacto.value = ''
  try {
    const respuesta = await fetch('/api/contacto', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(contacto.value)
    })
    if (respuesta.ok) {
      estadoContacto.value = 'enviado'
      contacto.value = { nombre: '', email: '', mensaje: '', web: '' }
      return
    }
    if (respuesta.status === 400) errorContacto.value = t('contacto.errorDatos')
    else if (respuesta.status === 429) errorContacto.value = t('contacto.errorLimite')
    else errorContacto.value = t('contacto.errorEnvio')
  } catch (error) {
    console.error('Error enviando la consulta:', error)
    errorContacto.value = t('contacto.errorConexion')
  }
  estadoContacto.value = 'error'
}
</script>

<template>
  <div class="pagina-contacto">
    <div class="contenedor-ancho">
      <h1 class="titulo-seccion">{{ $t('contacto.titulo') }}</h1>
      
      <div class="contacto-unacolumna">
        <div class="tarjeta-dato datos-unificados">
          <h3>{{ $t('contacto.info') }}</h3>
          <p><strong>{{ $t('contacto.direccion') }}:</strong> Passeig Marítim de la Barceloneta, 37-49, 08003 Barcelona</p>
          <p><strong>{{ $t('contacto.telefono') }}:</strong> +34 93 230 95 00</p>
          <p><strong>{{ $t('contacto.email') }}:</strong> <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a></p>
        </div>

        <div class="mapa-container">
          <iframe 
            :title="$t('contacto.mapa')"
            src="https://maps.google.com/maps?q=Passeig%20Mar%C3%ADtim%20de%20la%20Barceloneta,%2037-49,%2008003%20Barcelona&t=&z=15&ie=UTF8&iwloc=&output=embed" 
            width="100%" 
            height="400" 
            style="border:0;" 
            allowfullscreen="" 
            loading="lazy" 
            referrerpolicy="no-referrer-when-downgrade">
          </iframe>
        </div>
        
        <div class="tarjeta-dato formulario-amplio">
          <h3>{{ $t('contacto.formTitulo') }}</h3>
          <form @submit.prevent="enviarContacto">
            <div class="grupo-input">
              <label for="nombre">{{ $t('contacto.nombre') }}</label>
              <input type="text" id="nombre" name="nombre" v-model="contacto.nombre" :placeholder="$t('contacto.nombrePh')" maxlength="200" required>
            </div>
            <div class="grupo-input">
              <label for="email">{{ $t('contacto.email') }}</label>
              <input type="email" id="email" name="email" v-model="contacto.email" :placeholder="$t('contacto.emailPh')" maxlength="254" required>
            </div>
            <div class="grupo-input">
              <label for="mensaje">{{ $t('contacto.mensaje') }}</label>
              <textarea id="mensaje" name="mensaje" v-model="contacto.mensaje" rows="6" :placeholder="$t('contacto.mensajePh')" maxlength="5000" required></textarea>
            </div>
            <!-- Campo trampa para bots: oculto a las personas -->
            <div class="campo-trampa" aria-hidden="true">
              <label for="web">{{ $t('contacto.trampa') }}</label>
              <input type="text" id="web" name="web" v-model="contacto.web" tabindex="-1" autocomplete="off">
            </div>
            <p class="aviso-privacidad">{{ $t('contacto.privacidad') }}</p>
            <button type="submit" class="btn-enviar" :disabled="estadoContacto === 'enviando'">
              {{ estadoContacto === 'enviando' ? $t('contacto.enviando') : $t('contacto.enviar') }}
            </button>
            <p v-if="estadoContacto === 'enviado'" class="estado-contacto ok" role="status">
              {{ $t('contacto.enviado') }}
            </p>
            <p v-else-if="estadoContacto === 'error'" class="estado-contacto error" role="alert">
              {{ errorContacto }}. {{ $t('contacto.alternativa') }} <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a>.
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
