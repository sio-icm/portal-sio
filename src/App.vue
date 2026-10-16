<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import logoSio from './assets/sioblanco2baix.png'
import logoCsic from './assets/csic.png'
import logoIcm from './assets/icm.png'
import logoSevero from './assets/severo.png'

const route = useRoute()
const idiomaActual = ref('es') // Controla qué botón de idioma está activo

const mostrarCabecera = computed(() => !route.meta.sinCabecera)
const cabeceraSolida = computed(() => Boolean(route.meta.cabeceraSolida))

// --- FUNCIÓN PARA CAMBIAR DE IDIOMA CON GOOGLE ---
const cambiarIdioma = (lang) => {
  idiomaActual.value = lang
  
  if (lang === 'es') {
    location.reload(); // Vuelve al original recargando limpio
    return;
  }

  const selectField = document.querySelector('.goog-te-combo');
  if (selectField) {
    selectField.value = lang;
    selectField.dispatchEvent(new Event('change'));
  } else {
    // Si Google tarda un poco en inyectar el elemento, reintentamos a los 800ms
    setTimeout(() => {
      const retryField = document.querySelector('.goog-te-combo');
      if (retryField) {
        retryField.value = lang;
        retryField.dispatchEvent(new Event('change'));
      }
    }, 800);
  }
}
</script>

<template>
  <div class="icm-layout">
    
    <div class="top-bar">
      <div class="contenedor-ancho top-bar-inner">
        <div class="spacer"></div>
        <div class="top-nav-group">
          <RouterLink :to="{ name: 'contacto' }" class="top-item border-left underline-item">CONTACTO</RouterLink>
          <RouterLink :to="{ name: 'intranet' }" class="top-item border-left underline-item">INTRANET</RouterLink>
          
          <div class="top-item border-left idiomas-container">
            <span class="lang-link" :class="{ active: idiomaActual === 'ca' }" @click="cambiarIdioma('ca')">CAT</span> | 
            <span class="lang-link" :class="{ active: idiomaActual === 'es' }" @click="cambiarIdioma('es')">ES</span> | 
            <span class="lang-link" :class="{ active: idiomaActual === 'en' }" @click="cambiarIdioma('en')">EN</span>
          </div>

          <div class="top-item border-left search-block">
            <span class="search-label">BUSCAR</span>
            <svg class="lupa-svg" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
          </div>
        </div>
      </div>
    </div>
    
    <header v-if="mostrarCabecera" class="main-header header-transparente" :class="{ 'header-solido-contacto': cabeceraSolida }">
      <div class="contenedor-ancho header-inner">
        
        <div class="header-left">
          <RouterLink to="/" aria-label="Inicio">
            <img :src="logoSio" alt="SIO" class="logo-principal">
          </RouterLink>
          
          <div class="divider"></div>
          
          <div class="logos-grupo">
            <a href="https://www.icm.csic.es" target="_blank" rel="noopener noreferrer">
              <img :src="logoIcm" alt="ICM" class="logo-pequeno">
            </a>
            
            <a href="https://www.aei.gob.es/ayudas-concedidas/centros-unidades-excelencia" target="_blank" rel="noopener noreferrer">
              <img :src="logoSevero" alt="Severo Ochoa" class="logo-pequeno">
            </a>
            
            <a href="https://www.csic.es" target="_blank" rel="noopener noreferrer">
              <img :src="logoCsic" alt="CSIC" class="logo-pequeno filter-white">
            </a>
          </div>
        </div>

        <nav class="nav-menu">
          <RouterLink :to="{ name: 'inicio' }" class="nav-item">EL SIO</RouterLink>
          <RouterLink :to="{ name: 'servicios' }" class="nav-item">SERVICIOS</RouterLink>
          <RouterLink :to="{ name: 'proyectos' }" class="nav-item">PROYECTOS</RouterLink>
          <RouterLink :to="{ name: 'idi' }" class="nav-item">I+D+I</RouterLink>
        </nav>
        
      </div>
    </header>

    <main class="main-content">
      <RouterView />
    </main>

    <footer class="footer-icm">
      <div class="contenedor-ancho">
        <p>© 2026 Servicio de Ingeniería Oceanográfica - CSIC</p>
      </div>
    </footer>
    
  </div> 
</template>
  
<style>
/* 🌐 ESTILOS PARA EL TRADUCTOR DE GOOGLE */
.goog-te-banner-frame.skiptranslate { display: none !important; }
body { top: 0px !important; }
.goog-tooltip { display: none !important; }
.goog-text-highlight { background-color: transparent !important; box-shadow: none !important; }
#google_translate_element { position: absolute; left: -9999px; opacity: 0; pointer-events: none; }

:root { 
  --icm-navy: #012169ff;   
  --icm-blue: #0086c0;
  --icm-gris-claro: #a8bacc; 
}

body { margin: 0; font-family: 'Helvetica Neue', Arial, sans-serif; -webkit-font-smoothing: antialiased; }
.contenedor-ancho { max-width: 1200px; margin: 0 auto; padding: 0 15px; }
.btn-reset { background: none; border: none; color: inherit; font: inherit; cursor: pointer; padding: 0; }

.top-bar { 
  background: var(--icm-navy); 
  height: 40px; 
  position: relative; 
  z-index: 9999; 
}
.top-bar-inner { display: flex; justify-content: space-between; align-items: center; height: 100%; }
.top-nav-group { display: flex; height: 100%; align-items: center; border-right: 1px solid rgba(255,255,255,0.2); }
.top-item { display: flex; align-items: center; height: 100%; padding: 0 15px; font-size: 11px; font-weight: bold; color: white; text-decoration: none; position: relative; }
.border-left { border-left: 1px solid rgba(255,255,255,0.2); }
.underline-item::after { content: ''; position: absolute; width: 0; height: 2px; bottom: 12px; left: 15px; background-color: white; transition: width 0.3s ease; }
.underline-item:hover::after { width: calc(100% - 30px); }
.idiomas-container { display: flex; gap: 8px; align-items: center; }
.lang-separator { color: var(--icm-gris-claro); font-weight: normal; font-size: 10px; }
.lang-link { color: var(--icm-gris-claro); position: relative; cursor: pointer; padding-bottom: 2px; transition: color 0.3s; }
.lang-link::after { content: ''; position: absolute; width: 0; height: 2px; bottom: -4px; left: 0; background-color: var(--icm-gris-claro); transition: width 0.3s ease; }
.lang-link:hover::after { width: 100%; }
.lang-link.active { color: white; }
.lang-link.active::after { width: 100%; background-color: white; }
.search-block { background: var(--icm-blue); padding: 0 15px; cursor: pointer; transition: background 0.3s; gap: 8px; }
.search-block:hover { background: #00a4eb; }
.lupa-svg { height: 16px; width: 16px; fill: white; }

.header-transparente { 
  position: absolute; 
  top: 40px; 
  left: 0; 
  right: 0; 
  background: transparent !important; 
  padding: 25px 0; 
  z-index: 900; 
  border-bottom: 1px solid rgba(255,255,255,0.2); 
}
.header-inner { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }

.logo-principal { height: 60px; cursor: pointer; transition: transform 0.3s; }
.logo-principal:hover { transform: scale(1.05); } 

.divider { width: 1px; height: 45px; background: rgba(255,255,255,0.4); margin: 0 25px; }
.logos-grupo { display: flex; align-items: center; gap: 15px; }
.logo-pequeno { height: 35px; opacity: 0.9; transition: transform 0.3s; }
.logo-pequeno:hover { transform: scale(1.05); opacity: 1; }
.filter-white { filter: brightness(0) invert(1); }

.nav-menu { display: flex; align-items: center; gap: 25px; }
.nav-item { 
  color: white !important; 
  text-decoration: none; 
  font-weight: bold; 
  font-size: 14px; 
  text-shadow: 1px 1px 3px rgba(0,0,0,0.9); 
  position: relative; 
  padding-bottom: 5px; 
  transition: color 0.3s ease; 
}
.nav-item:hover { color: var(--icm-blue) !important; }
.nav-item::after { content: ''; position: absolute; width: 0; height: 3px; bottom: -2px; left: 0; background-color: var(--icm-blue); transition: width 0.3s ease; }
.nav-item:hover::after { width: 100%; }

.main-content { margin-top: 0; }
.titulo-seccion { color: var(--icm-navy); font-size: 28px; border-bottom: 2px solid var(--icm-blue); padding-bottom: 10px; margin-bottom: 30px; }
.contacto-unacolumna { display: flex; flex-direction: column; gap: 30px; max-width: 900px; margin: 0 auto; }
.pagina-contacto { padding: 80px 0; background: #fdfdfd; animation: fadeIn 0.5s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.tarjeta-dato { background: white; padding: 20px; border-left: 4px solid var(--icm-blue); margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.tarjeta-dato h3 { margin: 0 0 10px 0; font-size: 16px; color: var(--icm-navy); }
.grupo-input { display: flex; flex-direction: column; gap: 5px; margin-bottom: 15px; }
.grupo-input label { font-size: 13px; font-weight: bold; color: #555; }
.grupo-input input, .grupo-input select, .grupo-input textarea { padding: 12px; border: 1px solid #ddd; border-radius: 4px; }

.btn-enviar { width: 100%; letter-spacing: 1px; background: var(--icm-blue); color: white; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: background 0.3s; }
.btn-enviar:hover { background: var(--icm-navy); }
.btn-enviar:disabled { opacity: 0.6; cursor: wait; }
.campo-trampa { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
.aviso-privacidad { font-size: 12px; color: #666; line-height: 1.5; margin: 0 0 15px; }
.estado-contacto { margin: 15px 0 0; padding: 12px; border-radius: 4px; font-size: 14px; }
.estado-contacto.ok { background: #e6f4ea; color: #1e6b34; }
.estado-contacto.error { background: #fdecea; color: #a12622; }
.estado-contacto a { color: inherit; font-weight: bold; }

.datos-unificados p { font-size: 15px; color: #444; margin: 12px 0; line-height: 1.5; }
.datos-unificados a { color: var(--icm-blue); text-decoration: none; font-weight: bold; }
.datos-unificados a:hover { text-decoration: underline; }

.mapa-container { width: 100%; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.15); border: 1px solid #ddd; }
.formulario-amplio { border-top: 4px solid var(--icm-blue); border-left: none; padding: 30px; }

.header-solido-contacto { background: var(--icm-navy) !important; position: relative !important; top: 0 !important; border-bottom: none !important; }
.header-solido-contacto + .main-content .pagina-contacto { padding-top: 40px; }

@media (max-width: 768px) {
  .header-inner { flex-direction: column; gap: 15px; }
  .header-left { display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 12px; width: 100%; }
  .divider { display: none; }
  .logo-principal { height: 38px; flex-shrink: 0; }
  .logos-grupo { display: flex; flex-direction: row; align-items: center; gap: 6px; }
  .logo-pequeno { height: 18px; flex-shrink: 0; }
  .nav-menu { flex-wrap: wrap; justify-content: center; gap: 12px; }
  .nav-item { font-size: 12px; }
  .contacto-unacolumna { padding: 0 10px; }
  .top-item { padding: 0 8px; font-size: 10px; }
  .search-label { display: none; }
  .idiomas-container { gap: 4px; }
}

.carousel-dots { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; z-index: 10; }
.dot { width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; background: transparent; cursor: pointer; transition: all 0.3s ease; }
.dot.active { background: white; transform: scale(1.2); }
.dot:hover { background: rgba(255, 255, 255, 0.5); } 
</style>