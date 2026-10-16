import { createRouter, createWebHistory } from 'vue-router'
import Inicio from './components/Inicio.vue'

// Cada sección tiene su propia dirección. El nombre de la ruta es el que
// usan los componentes al emitir 'cambiar-pagina'.
// cabeceraSolida: la cabecera no va encima de una imagen de fondo.
const routes = [
  { path: '/', name: 'inicio', component: Inicio, meta: { titulo: '' } },
  { path: '/servicios', name: 'servicios', component: () => import('./components/Servicios.vue'), meta: { titulo: 'Servicios' } },
  { path: '/servicios/instrumentacion', name: 'instrumentacion', component: () => import('./components/Instrumentacion.vue'), meta: { titulo: 'Instrumentación' } },
  { path: '/servicios/pelagia', name: 'pelagia', component: () => import('./components/Pelagia.vue'), meta: { titulo: 'Embarcación Pelagia' } },
  { path: '/servicios/tanques', name: 'tanques', component: () => import('./components/TanquesPruebas.vue'), meta: { titulo: 'Tanques de pruebas' } },
  { path: '/servicios/salinidad', name: 'salinidad', component: () => import('./components/AnalisisSalinidad.vue'), meta: { titulo: 'Análisis de salinidad' } },
  { path: '/servicios/fondeos', name: 'fondeos', component: () => import('./components/Fondeos.vue'), meta: { titulo: 'Fondeos' } },
  { path: '/servicios/prototipado', name: 'prototipado', component: () => import('./components/Prototipado.vue'), meta: { titulo: 'Prototipado' } },
  { path: '/proyectos', name: 'proyectos', component: () => import('./components/Proyectos.vue'), meta: { titulo: 'Proyectos' } },
  { path: '/idi', name: 'idi', component: () => import('./components/DesarrolloIdi.vue'), meta: { titulo: 'I+D+I' } },
  { path: '/bluelab', name: 'bluelab', component: () => import('./components/BlueLab.vue'), meta: { titulo: 'BLUE Lab' } },
  { path: '/equipo', name: 'equipo', component: () => import('./components/EquipoSio.vue'), meta: { titulo: 'Equipo' } },
  { path: '/noticias', name: 'noticias', component: () => import('./components/NoticiasSio.vue'), meta: { titulo: 'Noticias' } },
  { path: '/memoria', name: 'memoria', component: () => import('./components/MemoriaAnual.vue'), meta: { titulo: 'Memoria anual' } },
  { path: '/contacto', name: 'contacto', component: () => import('./components/Contacto.vue'), meta: { titulo: 'Contacto', cabeceraSolida: true } },
  { path: '/intranet', name: 'intranet', component: () => import('./components/IntranetPanel.vue'), meta: { titulo: 'Intranet', sinCabecera: true } },
  { path: '/:ruta(.*)*', name: 'no-encontrado', component: () => import('./components/NoEncontrado.vue'), meta: { titulo: 'Página no encontrada', cabeceraSolida: true } }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, posicionGuardada) {
    return posicionGuardada || { top: 0 }
  }
})

const TITULO_WEB = 'Servicio de Ingeniería Oceanográfica'

router.afterEach((to) => {
  document.title = to.meta.titulo ? `${to.meta.titulo} | ${TITULO_WEB}` : TITULO_WEB
})

export default router
