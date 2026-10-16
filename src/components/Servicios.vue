<script setup>
// Textos de cada tarjeta: servicios.<clave> en src/i18n
const tarjetas = [
  { clave: 'pelagia', punto: 'punto-azul' },
  { clave: 'instrumentacion', punto: 'punto-verde' },
  { clave: 'tanques', punto: 'punto-azul' },
  { clave: 'salinidad', punto: 'punto-verde' },
  { clave: 'fondeos', punto: 'punto-azul' },
  { clave: 'prototipado', punto: 'punto-verde' }
]
</script>

<template>
  <div class="servicios-hub">
    <div class="fondo-servicios"></div>
    <div class="contenedor-ancho contenido-hub">
      <h1 class="titulo-seccion">{{ $t('servicios.titulo') }}</h1>
      <p class="subtitulo">{{ $t('servicios.subtitulo') }}</p>

      <div class="grid-servicios">
        <RouterLink v-for="tarjeta in tarjetas" :key="tarjeta.clave" :to="{ name: tarjeta.clave }" class="seccion-bloque">
          <div class="cabecera-bloque">
            <h2 class="titulo-fija">{{ $t(`servicios.${tarjeta.clave}.titulo`) }}</h2>
            <p>{{ $t(`servicios.${tarjeta.clave}.texto`) }}</p>
          </div>
          <div class="lista-items">
            <div v-for="(item, i) in $tm(`servicios.${tarjeta.clave}.items`)" :key="i" class="item-servicio">
              <span :class="tarjeta.punto" aria-hidden="true">●</span><div>{{ $rt(item) }}</div>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.servicios-hub { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-servicios { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-image: linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('/instrumentacion.jpg'); background-size: cover; background-position: center; z-index: 0; }
.contenido-hub { position: relative; z-index: 10; padding-top: 120px; }
.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 40px; max-width: 800px; }

/* CUADRICULA 2x2 */
.grid-servicios { display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; }

.seccion-bloque { background: white; border-radius: 12px; padding: 35px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); display: flex; flex-direction: column; cursor: pointer; transition: transform 0.3s; }
.seccion-bloque:hover { transform: translateY(-5px); }
a.seccion-bloque { color: inherit; text-decoration: none; }
.seccion-bloque:focus-visible { outline: 3px solid #0086c0; outline-offset: 4px; }
.titulo-fija { color: #012169; margin-top: 0; font-size: 1.6rem; margin-bottom: 10px; }
.cabecera-bloque p { color: #666; font-size: 0.95rem; line-height: 1.3; margin-bottom: 15px; }
.lista-items { margin-top: 15px; display: flex; flex-direction: column; gap: 8px; }
.item-servicio { display: flex; gap: 10px; font-size: 0.9rem; color: #333; }
.punto-azul { color: #007bff; }
.punto-verde { color: #28a745; }

@media (max-width: 900px) { .grid-servicios { grid-template-columns: 1fr; } }
</style>