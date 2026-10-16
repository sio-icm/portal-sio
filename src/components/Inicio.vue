<script setup>
import CarruselComponente from './CarruselComponente.vue'
import QuienesSomos from './QuienesSomos.vue'

defineEmits(['cambiar-pagina'])
</script>

<template>
  <div class="inicio-container">
    <CarruselComponente />
    <QuienesSomos @cambiar-pagina="(pagina) => $emit('cambiar-pagina', pagina)" />
  </div>
</template>
