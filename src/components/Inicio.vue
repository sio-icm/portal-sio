<script setup>
import CarruselComponente from './CarruselComponente.vue'
import QuienesSomos from './QuienesSomos.vue'
</script>

<template>
  <div class="inicio-container">
    <h1 class="solo-lectores">{{ $t('inicio.titulo') }}</h1>
    <CarruselComponente />
    <QuienesSomos />
  </div>
</template>

<style scoped>
/* Ocupa l'espai que queda fins al peu (vegeu .main-inicio a App.vue) */
.inicio-container { flex: 1 0 auto; display: flex; flex-direction: column; }
</style>
