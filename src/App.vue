<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import QuienesSomos from './components/QuienesSomos.vue'
import Proyectos from './components/Proyectos.vue'
import Servicios from './components/Servicios.vue'
import DesarrolloIdi from './components/DesarrolloIdi.vue'
import BlueLab from './components/BlueLab.vue'
import IntranetPanel from './components/IntranetPanel.vue'
import CarruselComponente from './components/CarruselComponente.vue'
import Instrumentacion from './components/Instrumentacion.vue'
import Pelagia from './components/Pelagia.vue'
import logoSio from './assets/sioblanco2baix.png'
import logoCsic from './assets/csic.png'
import logoIcm from './assets/icm.png'
import logoSevero from './assets/severo.png'
import TanquesPruebas from './components/TanquesPruebas.vue'
import AnalisisSalinidad from './components/AnalisisSalinidad.vue'
import EquipoSio from './components/EquipoSio.vue'
import Fondeos from './components/Fondeos.vue' 
import NoticiasSio from './components/NoticiasSio.vue'
import MemoriaAnual from './components/MemoriaAnual.vue'
import Prototipado from './components/Prototipado.vue'

const vistaActual = ref('inicio')
const usuarioLogueadoSio = ref(false)
const idiomaActual = ref('es') // Controla qué botón de idioma está activo

onMounted(() => {
  if (sessionStorage.getItem('sio_auth') === 'true') {
    usuarioLogueadoSio.value = true
  }
})

const cambiarVista = (nuevaVista) => { 
  vistaActual.value = nuevaVista
  window.history.pushState({ vista: nuevaVista }, '', `#${nuevaVista}`)
  window.scrollTo(0, 0)
}

const irAContacto = () => { cambiarVista('contacto') }
const volverAInicio = () => { cambiarVista('inicio') }

// --- MAGIA PARA LA FLECHA "ATRÁS" DEL NAVEGADOR ---
const manejarFlechaAtras = (evento) => {
  if (evento.state && evento.state.vista) {
    vistaActual.value = evento.state.vista
  } else {
    vistaActual.value = 'inicio'
  }
}

onMounted(() => {
  window.addEventListener('popstate', manejarFlechaAtras)
  window.history.replaceState({ vista: 'inicio' }, '', '')
  
  if (sessionStorage.getItem('sio_auth') === 'true') {
    usuarioLogueadoSio.value = true
  }
})

onUnmounted(() => {
  window.removeEventListener('popstate', manejarFlechaAtras)
})

const manejarClicIntranet = () => {
  cambiarVista('intranet') 
}

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
          <a href="#" class="top-item border-left underline-item" @click.prevent="irAContacto">CONTACTO</a>
          <button class="top-item border-left btn-reset underline-item" @click="manejarClicIntranet">INTRANET</button>
          
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
    
    <header v-if="vistaActual !== 'intranet'" class="main-header header-transparente" :class="{ 'header-solido-contacto': vistaActual === 'contacto' }">
      <div class="contenedor-ancho header-inner">
        
        <div class="header-left">
          <img :src="logoSio" alt="SIO" class="logo-principal" @click="volverAInicio">
          
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
          <a href="#" @click.prevent="cambiarVista('inicio')" class="nav-item">EL SIO</a>
          <a href="#" @click.prevent="cambiarVista('servicios')" class="nav-item">SERVICIOS</a>
          <a href="#" @click.prevent="cambiarVista('proyectos')" class="nav-item">PROYECTOS</a>
          <a href="#" @click.prevent="cambiarVista('idi')" class="nav-item">I+D+I</a>
        </nav>
        
      </div>
    </header>

    <main class="main-content">
      
      <div v-if="vistaActual === 'inicio'" class="inicio-container">
        <CarruselComponente />
        <QuienesSomos @cambiar-pagina="cambiarVista" />
      </div>
      
      <Servicios v-else-if="vistaActual === 'servicios'" @cambiar-pagina="cambiarVista" />
      <Instrumentacion v-else-if="vistaActual === 'instrumentacion'" @cambiar-pagina="cambiarVista" />
      <Pelagia v-else-if="vistaActual === 'pelagia'" @cambiar-pagina="cambiarVista" />
      <TanquesPruebas v-else-if="vistaActual === 'tanques'" @cambiar-pagina="cambiarVista" />
      <AnalisisSalinidad v-else-if="vistaActual === 'salinidad'" @cambiar-pagina="cambiarVista" />
      <Prototipado v-else-if="vistaActual === 'prototipado'" @cambiar-pagina="cambiarVista" />

      <div v-else-if="vistaActual === 'proyectos'"><Proyectos @volver="volverAInicio" /></div>
      <div v-else-if="vistaActual === 'idi'"><DesarrolloIdi @volver="volverAInicio" @cambiar-pagina="cambiarVista" /></div>
      <div v-else-if="vistaActual === 'bluelab'"><BlueLab @volver="vistaActual = 'idi'" /></div>
      <div v-else-if="vistaActual === 'intranet'"><IntranetPanel @volver="volverAInicio" /></div>

      <EquipoSio v-else-if="vistaActual === 'equipo'" @cambiar-pagina="cambiarVista" />
      <Fondeos v-else-if="vistaActual === 'fondeos'" @cambiar-pagina="cambiarVista" />
      <NoticiasSio v-else-if="vistaActual === 'noticias'" @cambiar-pagina="cambiarVista" />
      <MemoriaAnual v-else-if="vistaActual === 'memoria'" @cambiar-pagina="cambiarVista" /> 
      
      <div v-else-if="vistaActual === 'contacto'" class="pagina-contacto">
        <div class="contenedor-ancho">
          <h2 class="titulo-seccion">CONTACTO Y UBICACIÓN</h2>
          
          <div class="contacto-unacolumna">
            <div class="tarjeta-dato datos-unificados">
              <h3>Información del SIO</h3>
              <p><strong>Dirección:</strong> Passeig Marítim de la Barceloneta, 37-49, 08003 Barcelona</p>
              <p><strong>Teléfono:</strong> +34 93 230 95 00</p>
              <p><strong>Email:</strong> <a href="mailto:sio.icm@icm.csic.es">sio.icm@icm.csic.es</a></p>
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
              <form @submit.prevent>
                <div class="grupo-input">
                  <label for="nombre">Nombre</label>
                  <input type="text" id="nombre" placeholder="Tu nombre" required>
                </div>
                <div class="grupo-input">
                  <label for="email">Email</label>
                  <input type="email" id="email" placeholder="tu@email.com" required>
                </div>
                <div class="grupo-input">
                  <label for="mensaje">Mensaje</label>
                  <textarea id="mensaje" rows="6" placeholder="¿En qué podemos ayudarte?" required></textarea>
                </div>
                <button type="submit" class="btn-enviar">ENVIAR CONSULTA</button>
              </form>
            </div>
          </div>
        </div>
      </div>
      
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