<template>
  <div class="pagina-no-encontrada">
    <div class="contenedor-ancho">
      <h1 class="titulo-seccion">Página no encontrada</h1>
      <p>La dirección que buscas no existe o ha cambiado.</p>
      <RouterLink to="/" class="btn-inicio">Volver al inicio</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.pagina-no-encontrada { padding: 80px 0; min-height: 50vh; background: #fdfdfd; }
.pagina-no-encontrada p { font-size: 16px; color: #444; margin-bottom: 30px; }
.btn-inicio { display: inline-block; background: var(--icm-blue); color: white; padding: 12px 24px; border-radius: 4px; text-decoration: none; font-weight: bold; }
.btn-inicio:hover { background: var(--icm-navy); }
</style>
