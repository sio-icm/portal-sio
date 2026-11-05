<script setup>
// Aviso tras enviar una solicitud: confirmación o error con el correo del SIO como alternativa
defineProps({
  estado: { type: String, default: '' },
  error: { type: String, default: '' },
  oscuro: { type: Boolean, default: false }
})
</script>

<template>
  <p v-if="estado === 'enviado'" :class="['estado-solicitud', 'ok', { oscuro }]" role="status">
    ✓ {{ $t('solicitud.enviado') }}
  </p>
  <p v-else-if="estado === 'error'" :class="['estado-solicitud', 'error', { oscuro }]" role="alert">
    {{ error }}. {{ $t('solicitud.alternativa') }} <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a>.
  </p>
</template>

<style scoped>
.estado-solicitud { margin: 12px 0 0; padding: 10px 12px; border-radius: 4px; font-size: 0.9rem; text-align: left; }
.ok { background: #eaf6dc; color: #2e5b0a; border: 1px solid #8cc63f; }
.error { background: #fdecec; color: #8a1c1c; border: 1px solid #e3a1a1; }
.error a { color: inherit; font-weight: bold; }
</style>
