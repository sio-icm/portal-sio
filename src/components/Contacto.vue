<script setup>
import { ref } from 'vue'

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
    const datos = await respuesta.json().catch(() => ({}))
    errorContacto.value = datos.error || 'No se ha podido enviar la consulta'
  } catch (error) {
    console.error('Error enviando la consulta:', error)
    errorContacto.value = 'No se ha podido conectar con el servidor'
  }
  estadoContacto.value = 'error'
}
</script>

<template>
  <div class="pagina-contacto">
    <div class="contenedor-ancho">
      <h1 class="titulo-seccion">CONTACTO Y UBICACIÓN</h1>
      
      <div class="contacto-unacolumna">
        <div class="tarjeta-dato datos-unificados">
          <h3>Información del SIO</h3>
          <p><strong>Dirección:</strong> Passeig Marítim de la Barceloneta, 37-49, 08003 Barcelona</p>
          <p><strong>Teléfono:</strong> +34 93 230 95 00</p>
          <p><strong>Email:</strong> <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a></p>
        </div>

        <div class="mapa-container">
          <iframe 
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
          <h3>Envíanos tu consulta</h3>
          <form @submit.prevent="enviarContacto">
            <div class="grupo-input">
              <label for="nombre">Nombre</label>
              <input type="text" id="nombre" name="nombre" v-model="contacto.nombre" placeholder="Tu nombre" maxlength="200" required>
            </div>
            <div class="grupo-input">
              <label for="email">Email</label>
              <input type="email" id="email" name="email" v-model="contacto.email" placeholder="tu@email.com" maxlength="254" required>
            </div>
            <div class="grupo-input">
              <label for="mensaje">Mensaje</label>
              <textarea id="mensaje" name="mensaje" v-model="contacto.mensaje" rows="6" placeholder="¿En qué podemos ayudarte?" maxlength="5000" required></textarea>
            </div>
            <!-- Campo trampa para bots: oculto a las personas -->
            <div class="campo-trampa" aria-hidden="true">
              <label for="web">No rellenar</label>
              <input type="text" id="web" name="web" v-model="contacto.web" tabindex="-1" autocomplete="off">
            </div>
            <p class="aviso-privacidad">
              Los datos de este formulario se usan solo para responder a tu consulta y no se ceden a terceros.
              Responsable: Institut de Ciències del Mar (ICM-CSIC).
            </p>
            <button type="submit" class="btn-enviar" :disabled="estadoContacto === 'enviando'">
              {{ estadoContacto === 'enviando' ? 'ENVIANDO…' : 'ENVIAR CONSULTA' }}
            </button>
            <p v-if="estadoContacto === 'enviado'" class="estado-contacto ok" role="status">
              Consulta enviada. Te responderemos lo antes posible.
            </p>
            <p v-else-if="estadoContacto === 'error'" class="estado-contacto error" role="alert">
              {{ errorContacto }}. Puedes escribirnos directamente a <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a>.
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
