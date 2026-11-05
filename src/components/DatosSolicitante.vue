<script setup>
// Campos comunes de las solicitudes de servicios: nombre, correo y campo trampa.
// Se usa con useSolicitud(): <DatosSolicitante v-model:nombre="nombre" v-model:email="email" v-model:web="web" />
defineProps({ oscuro: { type: Boolean, default: false } })
const nombre = defineModel('nombre', { type: String, default: '' })
const email = defineModel('email', { type: String, default: '' })
const web = defineModel('web', { type: String, default: '' })

const id = `sol-${Math.random().toString(36).slice(2, 8)}`
</script>

<template>
  <div :class="['datos-solicitante', { oscuro }]">
    <div class="campo">
      <label :for="`${id}-nombre`">{{ $t('solicitud.nombre') }}</label>
      <input type="text" :id="`${id}-nombre`" v-model="nombre" :placeholder="$t('solicitud.nombrePh')"
             maxlength="200" autocomplete="name" required>
    </div>
    <div class="campo">
      <label :for="`${id}-email`">{{ $t('solicitud.email') }}</label>
      <input type="email" :id="`${id}-email`" v-model="email" :placeholder="$t('solicitud.emailPh')"
             maxlength="254" autocomplete="email" required>
    </div>
    <!-- Campo trampa para bots: oculto a las personas -->
    <div class="campo-trampa" aria-hidden="true">
      <label :for="`${id}-web`">{{ $t('contacto.trampa') }}</label>
      <input type="text" :id="`${id}-web`" v-model="web" tabindex="-1" autocomplete="off">
    </div>
  </div>
</template>

<style scoped>
.datos-solicitante { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; text-align: left; }
.campo { display: flex; flex-direction: column; gap: 5px; }
.campo label { font-size: 0.9rem; font-weight: bold; color: #003366; }
.campo input {
  width: 100%; padding: 10px; border: 1px solid #ccd6e0; border-radius: 4px;
  box-sizing: border-box; font-size: 0.95rem; font-family: inherit; background: white;
}
.campo input:focus { outline: none; border-color: #003366; }
.oscuro .campo label { color: white; }
.oscuro .campo input { border: none; background-color: rgba(255, 255, 255, 0.9); }
.campo-trampa { position: absolute; left: -10000px; width: 1px; height: 1px; overflow: hidden; }
@media (max-width: 600px) { .datos-solicitante { grid-template-columns: 1fr; } }
</style>
