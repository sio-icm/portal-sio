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
