<script setup>
import { computed, watch, ref, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { cambiarIdioma } from './i18n'
import { actualizarTitulo } from './router'
import logoSioCa from './assets/logos/logo-sio-blanco-ca.png'
import logoSioEs from './assets/logos/logo-sio-blanco-es.png'
import logoSioEn from './assets/logos/logo-sio-blanco-en.png'
import logoCsic from './assets/csic.png'
import logoIcm from './assets/icm.png'
import logoSevero from './assets/severo.png'

const route = useRoute()
const router = useRouter()
// Cerca de la barra de dalt (al mòbil, la lupa obre el quadre)
const textoCerca = ref('')
const cercaAbierta = ref(false)
const inputCerca = ref(null)
const obrirCerca = (e) => {
  if (!cercaAbierta.value && !textoCerca.value.trim() && window.matchMedia('(max-width: 768px)').matches) {
    e.preventDefault()
    cercaAbierta.value = true
    nextTick(() => inputCerca.value?.focus())
  }
}
const buscarWeb = () => {
  const q = textoCerca.value.trim()
  if (!q) { inputCerca.value?.focus(); return }
  router.push({ name: 'cerca', query: { q } })
  cercaAbierta.value = false
}
watch(() => route.query.q, (q) => { if (route.name === 'cerca') textoCerca.value = String(q || '') })
const { locale } = useI18n()

const idiomas = [
  { codigo: 'ca', etiqueta: 'CAT', nombre: 'Català' },
  { codigo: 'es', etiqueta: 'ES', nombre: 'Español' },
  { codigo: 'en', etiqueta: 'EN', nombre: 'English' }
]

// El logo lleva el nombre del servicio, así que cambia con el idioma
const logosSio = { ca: logoSioCa, es: logoSioEs, en: logoSioEn }
const logoSio = computed(() => logosSio[locale.value] || logoSioEs)

const mostrarCabecera = computed(() => !route.meta.sinCabecera)
const cabeceraSolida = computed(() => Boolean(route.meta.cabeceraSolida))

watch(locale, () => actualizarTitulo(route))
</script>

<template>
  <div class="icm-layout">
    
    <div class="top-bar">
      <div class="contenedor-ancho top-bar-inner">
        <div class="spacer"></div>
        <div class="top-nav-group">
          <RouterLink :to="{ name: 'contacto' }" class="top-item border-left underline-item">{{ $t('comun.contacto') }}</RouterLink>
          <RouterLink :to="{ name: 'intranet' }" class="top-item border-left underline-item">{{ $t('comun.intranet') }}</RouterLink>
          
          <div class="top-item border-left idiomas-container" role="group" :aria-label="$t('comun.idiomas')">
            <template v-for="(idioma, i) in idiomas" :key="idioma.codigo">
              <span v-if="i > 0" class="lang-separator" aria-hidden="true">|</span>
              <button
                type="button"
                class="lang-link btn-reset"
                :class="{ active: locale === idioma.codigo }"
                :lang="idioma.codigo"
                :aria-label="idioma.nombre"
                :aria-pressed="locale === idioma.codigo"
                @click="cambiarIdioma(idioma.codigo)"
              >{{ idioma.etiqueta }}</button>
            </template>
          </div>
          <form class="top-item border-left cerca-top" :class="{ abierta: cercaAbierta }" role="search" @submit.prevent="buscarWeb">
            <input ref="inputCerca" v-model="textoCerca" type="search" :placeholder="$t('cerca.placeholderCorto')" :aria-label="$t('cerca.titulo')"
              @keydown.esc="cercaAbierta = false">
            <!-- Només al mòbil: la lupa obre el quadre (a l'ordinador ja es llegeix «Cercar...») -->
            <button type="submit" class="btn-reset lupa" :aria-label="$t('cerca.buscar')" @click="obrirCerca">
              <svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                <circle cx="10.5" cy="10.5" r="6.5" /><line x1="15.5" y1="15.5" x2="21" y2="21" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
    
    <header v-if="mostrarCabecera" class="main-header header-transparente" :class="{ 'header-solido-contacto': cabeceraSolida }">
      <div class="contenedor-ancho header-inner">
        
        <div class="header-left">
          <RouterLink to="/" :aria-label="$t('comun.inicio')">
            <img :src="logoSio" :alt="$t('comun.nombreServicio')" class="logo-principal">
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
          <RouterLink :to="{ name: 'inicio' }" class="nav-item">{{ $t('comun.menu.sio') }}</RouterLink>
          <RouterLink :to="{ name: 'servicios' }" class="nav-item">{{ $t('comun.menu.servicios') }}</RouterLink>
          <RouterLink :to="{ name: 'proyectos' }" class="nav-item">{{ $t('comun.menu.proyectos') }}</RouterLink>
          <RouterLink :to="{ name: 'idi' }" class="nav-item">{{ $t('comun.menu.idi') }}</RouterLink>
        </nav>
        
      </div>
    </header>

    <main class="main-content" :class="{ 'main-inicio': route.name === 'inicio' }">
      <RouterView />
    </main>

    <footer class="footer-icm">
      <div class="contenedor-ancho">
        <p>{{ $t('comun.pie') }}</p>
      </div>
    </footer>
    
  </div> 
</template>
  
<style>
/* Figtree (SIL OFL, ver src/assets/fonts/OFL-Figtree.txt): la tipografía del logo
   de BLUE Lab, usada en las fichas de la portada. Incluida en la web, sin Google Fonts */
@font-face {
  font-family: 'Figtree';
  src: url('./assets/fonts/figtree-600.woff2') format('woff2');
  font-weight: 600;
  font-style: normal;
  font-display: swap;
}

:root { 
  --icm-navy: #012169ff;   
  --icm-blue: #0086c0;
  --icm-gris-claro: #a8bacc; 
}

body { margin: 0; font-family: 'Helvetica Neue', Arial, sans-serif; -webkit-font-smoothing: antialiased; }
.contenedor-ancho { max-width: 1200px; margin: 0 auto; padding: 0 15px; }
/* Visible solo para lectores de pantalla y buscadores */
.solo-lectores { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
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
/* Cerca */
.cerca-top { gap: 4px; padding: 0 10px; }
.cerca-top input { width: 150px; height: 26px; border: 1px solid rgba(255,255,255,0.35); border-radius: 13px; background: rgba(255,255,255,0.12); color: white; font: inherit; font-size: 12px; font-weight: normal; padding: 0 10px; outline: none; transition: width 0.25s, background 0.2s; }
.cerca-top input::placeholder { color: rgba(255,255,255,0.7); }
.cerca-top input:focus { width: 210px; background: white; color: #012169; }
.cerca-top .lupa { display: none; color: white; line-height: 0; padding: 4px; }
.cerca-top .lupa:hover { opacity: 0.8; }

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

.logo-principal { height: 51px; cursor: pointer; transition: transform 0.3s; }
.logo-principal:hover { transform: scale(1.05); } 

.divider { width: 1px; height: 36px; background: rgba(255,255,255,0.4); margin: 0 20px; }
.logos-grupo { display: flex; align-items: center; gap: 15px; }
.logo-pequeno { height: 34px; opacity: 0.9; transition: transform 0.3s; }
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
/* A la portada la pàgina ocupa com a mínim tota la pantalla: les fitxes creixen fins al peu
   (sense espai blanc a sota). La resta de pàgines no canvien. */
.icm-layout:has(.main-inicio) { min-height: 100vh; min-height: 100svh; display: flex; flex-direction: column; }
.main-inicio { flex: 1 0 auto; display: flex; flex-direction: column; }
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
  /* Capçalera més compacta però amb els logos més grans (s'ajusten a l'amplada: també caben en mòbils de 360 px) */
  .header-transparente { padding: 12px 0; }
  .header-inner { flex-direction: column; gap: 10px; }
  .header-left { display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 10px; width: 100%; }
  .divider { display: none; }
  .logo-principal { height: min(42px, 10.5vw); flex-shrink: 0; }
  .logos-grupo { display: flex; flex-direction: row; align-items: center; gap: 6px; }
  .logo-pequeno { height: min(22px, 5.6vw); flex-shrink: 0; }
  .nav-menu { flex-wrap: wrap; justify-content: center; gap: 12px; }
  .nav-item { font-size: 12px; }
  .contacto-unacolumna { padding: 0 10px; }
  .top-item { padding: 0 8px; font-size: 10px; }
  .idiomas-container { gap: 4px; }
  /* Al mòbil només es veu la lupa; en prémer-la, el quadre s'obre a sota de la barra */
  .cerca-top input { display: none; }
  .cerca-top .lupa { display: block; }
  .cerca-top.abierta input::placeholder { color: #8a94a6; }
  .cerca-top.abierta input { display: block; position: absolute; top: 40px; right: 0; width: min(320px, 92vw); height: 38px; border-radius: 0 0 0 8px; background: white; color: #012169; font-size: 15px; border: none; box-shadow: 0 6px 16px rgba(0,0,0,0.25); }
}

.carousel-dots { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; z-index: 10; }
.dot { width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; background: transparent; cursor: pointer; transition: all 0.3s ease; }
.dot.active { background: white; transform: scale(1.2); }
.dot:hover { background: rgba(255, 255, 255, 0.5); } 
</style>