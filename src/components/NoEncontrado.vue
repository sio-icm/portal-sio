<template>
  <div class="pagina-no-encontrada">
    <div class="contenedor-ancho">
      <h1 class="titulo-seccion">{{ $t('noEncontrado.titulo') }}</h1>
      <p>{{ $t('noEncontrado.texto') }}</p>
      <RouterLink to="/" class="btn-inicio">{{ $t('noEncontrado.volver') }}</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.pagina-no-encontrada { padding: 80px 0; min-height: 50vh; background: #fdfdfd; }
.pagina-no-encontrada p { font-size: 16px; color: #444; margin-bottom: 30px; }
.btn-inicio { display: inline-block; background: var(--icm-blue); color: white; padding: 12px 24px; border-radius: 4px; text-decoration: none; font-weight: bold; }
.btn-inicio:hover { background: var(--icm-navy); }
</style>
