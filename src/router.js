import { createRouter, createWebHistory } from 'vue-router'
import i18n from './i18n'
import Inicio from './components/Inicio.vue'

// Cada sección tiene su propia dirección. Los enlaces usan el nombre de la
// ruta: <RouterLink :to="{ name: 'pelagia' }">
// titulo: clave del texto en src/i18n para el título de la pestaña.
// cabeceraSolida: la cabecera no va encima de una imagen de fondo.
const routes = [
  { path: '/', name: 'inicio', component: Inicio, meta: { titulo: '' } },
  { path: '/servicios', name: 'servicios', component: () => import('./components/Servicios.vue'), meta: { titulo: 'rutas.servicios' } },
  { path: '/servicios/instrumentacion', name: 'instrumentacion', component: () => import('./components/Instrumentacion.vue'), meta: { titulo: 'rutas.instrumentacion' } },
  { path: '/servicios/pelagia', name: 'pelagia', component: () => import('./components/Pelagia.vue'), meta: { titulo: 'rutas.pelagia' } },
  { path: '/servicios/tanques', name: 'tanques', component: () => import('./components/TanquesPruebas.vue'), meta: { titulo: 'rutas.tanques' } },
  { path: '/servicios/salinidad', name: 'salinidad', component: () => import('./components/AnalisisSalinidad.vue'), meta: { titulo: 'rutas.salinidad' } },
  { path: '/servicios/fondeos', name: 'fondeos', component: () => import('./components/Fondeos.vue'), meta: { titulo: 'rutas.fondeos' } },
  { path: '/servicios/prototipado', name: 'prototipado', component: () => import('./components/Prototipado.vue'), meta: { titulo: 'rutas.prototipado' } },
  { path: '/proyectos', name: 'proyectos', component: () => import('./components/Proyectos.vue'), meta: { titulo: 'rutas.proyectos' } },
  { path: '/idi', name: 'idi', component: () => import('./components/DesarrolloIdi.vue'), meta: { titulo: 'rutas.idi' } },
  { path: '/bluelab', name: 'bluelab', component: () => import('./components/BlueLab.vue'), meta: { titulo: 'rutas.bluelab' } },
  { path: '/equipo', name: 'equipo', component: () => import('./components/EquipoSio.vue'), meta: { titulo: 'rutas.equipo' } },
  { path: '/noticias', name: 'noticias', component: () => import('./components/NoticiasSio.vue'), meta: { titulo: 'rutas.noticias' } },
  { path: '/memoria', name: 'memoria', component: () => import('./components/MemoriaAnual.vue'), meta: { titulo: 'rutas.memoria' } },
  { path: '/contacto', name: 'contacto', component: () => import('./components/Contacto.vue'), meta: { titulo: 'rutas.contacto', cabeceraSolida: true } },
  { path: '/intranet', name: 'intranet', component: () => import('./components/IntranetPanel.vue'), meta: { titulo: 'rutas.intranet', sinCabecera: true } },
  { path: '/:ruta(.*)*', name: 'no-encontrado', component: () => import('./components/NoEncontrado.vue'), meta: { titulo: 'rutas.noEncontrado', cabeceraSolida: true } }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, posicionGuardada) {
    return posicionGuardada || { top: 0 }
  }
})

// También se llama al cambiar de idioma (App.vue)
export const actualizarTitulo = (ruta) => {
  const { t } = i18n.global
  const nombreWeb = t('comun.nombreServicio')
  document.title = ruta.meta.titulo ? `${t(ruta.meta.titulo)} | ${nombreWeb}` : nombreWeb
}

router.afterEach(actualizarTitulo)

export default router
