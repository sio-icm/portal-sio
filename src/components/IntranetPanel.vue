<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { traducirError, traducirValor } from '../i18n'
import { QuillEditor } from '@vueup/vue-quill'
import 'quill/dist/quill.snow.css' // estils de Quill 2 (els de vue-quill són de Quill 1 i no pinten bé llistes ni codi)
import PaginasDocs from './PaginasDocs.vue'
import Compras from './Compras.vue'
import ActasReunion from './ActasReunion.vue'
import GestionEquipo from './GestionEquipo.vue'
import DiarioActividad from './DiarioActividad.vue'
import InformeSemestral from './InformeSemestral.vue'
import GestionUsuarios from './GestionUsuarios.vue'
import MiCuenta from './MiCuenta.vue'
import CalendariEquip from './CalendariEquip.vue'

const router = useRouter()
const { t } = useI18n()
const apiBase = '/api'
const apiUrl = `${apiBase}/instrumentos`
const apiUrlProyectos = `${apiBase}/proyectos`

const estaLogueado = ref(false)
// Quién ha iniciado sesión: { nombre, usuario_id, es_admin } (lo da el backend)
const sesion = ref({ nombre: '', usuario_id: null, es_admin: false })

// La sessió viu en una cookie del backend (mateix domini, el navegador l'envia sola)
const peticionApi = async (url, opciones = {}) => {
  const respuesta = await fetch(url, opciones)
  if (respuesta.status === 401 && estaLogueado.value) {
    estaLogueado.value = false
    alert(t('intranet.panel.sesionCaducada'))
  }
  return respuesta
}
const seccionActiva = ref('calendari') // 'calendari' (en entrar), 'diario', 'informe', 'cuenta', 'usuarios', 'equipo', 'documentacion', 'compras', 'proyectos', 'instrumentos', 'instrumentacion' (formulari), 'proyecto' (formulari)

// Las secciones nuevas avisan si la sesión ha caducado
const sesionCaducada = () => {
  if (!estaLogueado.value) return
  estaLogueado.value = false
  alert(t('intranet.panel.sesionCaducada'))
}
const usuario = ref('')
const password = ref('')
const recordarSesion = ref(false)

// LLISTES DE DADES
const instrumentos = ref([])
const proyectos = ref([])

// VARIABLES PER A L'EDICIÓ
const editandoId = ref(null)
const editandoProyectoId = ref(null)

const nuevoEquipo = ref({
  nombre: '', marca: '', numero_serie: '', categoria: '', subcategoria: '', ultima_calibracion: '', descripcion: '', parametros_tecnicos: ''
})

const nuevoProyecto = ref({
  titulo: '', categoria: '', estado: '', descripcion_corta: '', descripcion_ampliada: '', investigador_principal: '', pit: '', imagen: '',
  descripcion_corta_es: '', descripcion_ampliada_es: '', descripcion_corta_en: '', descripcion_ampliada_en: '', nextcloud: ''
})
// Idioma de les descripcions que s'està editant: 'ca' (text principal), 'es' o 'en'
const idiomaTexto = ref('ca')
const IDIOMAS_TEXTO = ['ca', 'es', 'en']
const sufijoTexto = computed(() => idiomaTexto.value === 'ca' ? '' : '_' + idiomaTexto.value)
// Fotos de la web que es poden triar com a portada d'un projecte (també s'hi pot escriure una altra ruta o una adreça https)
const FOTOS_WEB = ['/fondeo.webp', '/instrumentacion.webp', '/marmarejada.webp', '/niskin.webp', '/oficinatecnica.webp',
  '/pecesaguasalada.webp', '/peces.webp', '/pelagia.webp', '/reflexesmar.webp', '/rov.webp', '/salinometro.jpg', '/tortuga.webp',
  '/fotos/noticias/sacoso-portada.webp', '/fotos/noticias/sacoso-hesperides.webp', '/fotos/noticias/sacoso-fondejos.webp',
  '/fotos/noticias/somorrostro-boia.webp', '/fotos/noticias/somorrostro-portada.webp', '/fotos/noticias/donana-portada.webp',
  '/fotos/noticias/fnob-portada.webp']

// CONFIGURACIÓ DE LA BARRA D'EINES (Amb icona d'Imatge 🖼️)
const opcionsEditor = [
  [{ 'header': [1, 2, 3, false] }],
  ['bold', 'italic', 'underline'],
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  ['link', 'image'], 
  ['clean']
]


// ==============================
// CÀRREGUES INICIALS
// ==============================
const cargarInstrumentos = async () => {
  try {
    const respuesta = await peticionApi(apiUrl)
    instrumentos.value = await respuesta.json()
  } catch (error) { console.error("Error carregant instruments:", error) }
}

const cargarProyectos = async () => {
  try {
    const respuesta = await peticionApi(apiUrlProyectos)
    proyectos.value = await respuesta.json()
  } catch (error) { console.error("Error carregant projectes:", error) }
}

// ==============================
// HE OBLIDAT LA CONTRASENYA
// ==============================
// L'enllaç del correu porta ?restablir=... : en aquest cas es mostra el formulari de contrasenya nova
const tokenRestablir = ref(new URLSearchParams(window.location.search).get('restablir'))
const mensajeLogin = ref('')
const olvido = ref({ dato: '', enviando: false, enviado: '', error: '' })
const pedirEnlace = async () => {
  olvido.value = { ...olvido.value, enviando: true, enviado: '', error: '' }
  try {
    const r = await fetch(`${apiBase}/recuperar`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ usuario: olvido.value.dato })
    })
    if (r.ok) olvido.value.enviado = t('intranet.panel.enlaceEnviado')
    else olvido.value.error = traducirError((await r.json().catch(() => ({}))).error) || t('intranet.panel.noEnviado')
  } catch {
    olvido.value.error = t('intranet.panel.sinConexion')
  } finally {
    olvido.value.enviando = false
  }
}
const restablir = ref({ nueva: '', repetida: '', error: '', guardando: false })
const guardarRestablir = async () => {
  const f = restablir.value
  f.error = ''
  if (f.nueva !== f.repetida) { f.error = t('intranet.panel.noCoinciden'); return }
  f.guardando = true
  try {
    const r = await fetch(`${apiBase}/restablir`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token: tokenRestablir.value, nueva: f.nueva })
    })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) { f.error = traducirError(d.error) || t('intranet.panel.noCambiada'); return }
    salirDeRestablir()
    usuario.value = d.usuario || ''
    mensajeLogin.value = t('intranet.panel.cambiadaEntra')
  } catch {
    f.error = t('intranet.panel.sinConexion')
  } finally {
    f.guardando = false
  }
}
const salirDeRestablir = () => {
  tokenRestablir.value = null
  restablir.value = { nueva: '', repetida: '', error: '', guardando: false }
  window.history.replaceState({}, '', window.location.pathname) // treu el testimoni de la barra d'adreces
}

onMounted(async () => {
  // Neteja de l'antic login fals, que guardava 'sio_auth' al navegador
  sessionStorage.removeItem('sio_auth')
  localStorage.removeItem('sio_auth')
  try {
    const respuesta = await peticionApi(`${apiBase}/sesion`)
    const datos = await respuesta.json()
    if (datos.autenticado) {
      sesion.value = datos
      estaLogueado.value = true
      cargarInstrumentos()
      cargarProyectos()
      aplicarEnlace()
    }
  } catch (error) { console.error("Error comprovant la sessió:", error) }
})

// ==============================
// AUTENTICACIÓ
// ==============================
const iniciarSesion = async () => {
  try {
    const respuesta = await peticionApi(`${apiBase}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usuario: usuario.value, password: password.value, recordar: recordarSesion.value })
    })
    password.value = ''
    if (respuesta.ok) {
      sesion.value = await respuesta.json()
      seccionActiva.value = 'calendari'
      estaLogueado.value = true
      cargarInstrumentos()
      cargarProyectos()
      aplicarEnlace()
    } else if (respuesta.status === 401) {
      alert(t('intranet.panel.loginIncorrecto'))
    } else if (respuesta.status === 429) {
      alert(t('intranet.panel.demasiadosIntentos'))
    } else {
      alert(t('intranet.panel.loginError'))
    }
  } catch (error) {
    console.error("Error iniciant sessió:", error)
    alert(t('intranet.panel.sinConexion'))
  }
}

const cerrarSesion = async () => {
  try { await peticionApi(`${apiBase}/logout`, { method: 'POST' }) } catch (error) { console.error(error) }
  estaLogueado.value = false
  router.push('/') // en sortir, a la pàgina principal de la web
}

// ---------- MENÚ ----------
// Opcions agrupades per seccions. Al mòbil el menú es plega en un botó «☰» que diu on ets.
const menuAbierto = ref(false)
const gruposMenu = computed(() => [
  { titulo: 'intranet.panel.menu.grupoEquipo', items: [
    { id: 'calendari', texto: 'intranet.panel.menu.calendario' },
    { id: 'diario', texto: 'intranet.panel.menu.diario' },
    { id: 'actas', texto: 'intranet.panel.menu.actas' },
    { id: 'informe', texto: 'intranet.panel.menu.informe' },
    { id: 'equipo', texto: 'intranet.panel.menu.equipo' }
  ] },
  { titulo: 'intranet.panel.menu.grupoRecursos', items: [
    { id: 'proyectos', texto: 'intranet.panel.menu.proyectos' },
    { id: 'instrumentos', texto: 'intranet.panel.menu.instrumentos' },
    { id: 'documentacion', texto: 'intranet.panel.menu.documentacion' },
    { id: 'compras', texto: 'intranet.panel.menu.compras' }
  ] },
  { titulo: 'intranet.panel.menu.grupoCuenta', items: [
    { id: 'cuenta', texto: 'intranet.panel.menu.cuenta' },
    ...(sesion.value?.es_admin ? [{ id: 'usuarios', texto: 'intranet.panel.menu.usuarios' }] : [])
  ] }
])
// Els formularis d'alta compten com la seva llista (per marcar el menú)
const SECCION_DEL_MENU = { proyecto: 'proyectos', instrumentacion: 'instrumentos' }
const seccionMenu = computed(() => SECCION_DEL_MENU[seccionActiva.value] || seccionActiva.value)
const opcionActual = computed(() => gruposMenu.value.flatMap(g => g.items).find(i => i.id === seccionMenu.value))
// En tornar a prémer «Documentació» es torna a l'inici de la documentació
const docsKey = ref(0)
// Enllaços de la cerca: obrir directament una pàgina, una carpeta, una acta o una secció
const destinoInicial = ref({})
const aplicarEnlace = () => {
  const q = new URLSearchParams(window.location.search)
  if (q.get('doc') || q.get('carpeta')) {
    destinoInicial.value = { doc: Number(q.get('doc')) || null, carpeta: q.get('carpeta') || null }
    docsKey.value++
    seccionActiva.value = 'documentacion'
  } else if (q.get('acta')) {
    destinoInicial.value = { acta: Number(q.get('acta')) || null }
    seccionActiva.value = 'actas'
  } else if (['diario', 'calendari', 'compras', 'informe'].includes(q.get('seccion'))) {
    seccionActiva.value = q.get('seccion')
  } else return
  window.history.replaceState({}, '', window.location.pathname)
}
const irA = (id) => {
  if (id === 'documentacion') docsKey.value++
  if (id === 'proyectos' || id === 'instrumentos') volverDashboard(id)
  else seccionActiva.value = id
  menuAbierto.value = false
}

const volverDashboard = (destino = 'calendari') => {
  editandoId.value = null
  editandoProyectoId.value = null
  nuevoEquipo.value = { nombre: '', marca: '', numero_serie: '', categoria: '', subcategoria: '', ultima_calibracion: '', descripcion: '', parametros_tecnicos: '' }
  nuevoProyecto.value = { titulo: '', categoria: '', estado: '', descripcion_corta: '', descripcion_ampliada: '', investigador_principal: '', pit: '', imagen: '',
  descripcion_corta_es: '', descripcion_ampliada_es: '', descripcion_corta_en: '', descripcion_ampliada_en: '', nextcloud: '' }
  seccionActiva.value = typeof destino === 'string' ? destino : 'calendari'
}

// ==============================
// GESTIÓ D'INSTRUMENTS
// ==============================
const cargarParaEditar = (inst) => {
  editandoId.value = inst.id
  nuevoEquipo.value = {
    nombre: inst.nombre, marca: inst.marca || '', numero_serie: inst.numero_serie || '',
    categoria: inst.categoria || '', subcategoria: inst.subcategoria || '', ultima_calibracion: inst.ultima_calibracion || '',
    descripcion: inst.descripcion || '', parametros_tecnicos: inst.parametros_tecnicos || ''
  }
  seccionActiva.value = 'instrumentacion'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const guardarInstrumento = async () => {  
  try {
    const metodo = editandoId.value ? 'PUT' : 'POST'
    const url = editandoId.value ? `${apiUrl}/${editandoId.value}` : apiUrl
    const respuesta = await peticionApi(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(nuevoEquipo.value)
    })
    if (respuesta.ok) {
      alert(editandoId.value ? t('intranet.panel.instrumentoActualizado') : t('intranet.panel.instrumentoRegistrado'))
      volverDashboard('instrumentos')
      cargarInstrumentos()
    }
  } catch (error) { console.error(error) }
}

const eliminarInstrumento = async (id) => {
  if (!confirm(t('intranet.panel.confirmarBorrarInstrumento'))) return
  try {
    const respuesta = await peticionApi(`${apiUrl}/${id}`, { method: 'DELETE' })
    if (respuesta.ok) {
      alert(t('intranet.panel.instrumentoBorrado'))
      cargarInstrumentos()
    }
  } catch (error) { console.error(error) }
}

// ==============================
// GESTIÓ DE PROJECTES
// ==============================
const cargarParaEditarProyecto = (proj) => {
  editandoProyectoId.value = proj.id;
  nuevoProyecto.value = {
    titulo: proj.titulo,
    categoria: proj.categoria || '',
    estado: proj.estado || '',
    descripcion_corta: proj.descripcion_corta || '',
    descripcion_ampliada: proj.descripcion_ampliada || '',
    investigador_principal: proj.investigador_principal || '',
    pit: proj.pit || '',
    imagen: proj.imagen || '',
    descripcion_corta_es: proj.descripcion_corta_es || '',
    descripcion_ampliada_es: proj.descripcion_ampliada_es || '',
    descripcion_corta_en: proj.descripcion_corta_en || '',
    descripcion_ampliada_en: proj.descripcion_ampliada_en || '',
    nextcloud: proj.nextcloud || ''
  };
  idiomaTexto.value = 'ca';
  seccionActiva.value = 'proyecto';
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const guardarProyecto = async () => {
  const url = editandoProyectoId.value ? `${apiUrlProyectos}/${editandoProyectoId.value}` : apiUrlProyectos;
  const metodo = editandoProyectoId.value ? 'PUT' : 'POST';
  const datosAEnviar = {
    titulo: nuevoProyecto.value.titulo,
    categoria: nuevoProyecto.value.categoria,
    estado: nuevoProyecto.value.estado,
    descripcion_corta: nuevoProyecto.value.descripcion_corta,
    descripcion_ampliada: nuevoProyecto.value.descripcion_ampliada,
    investigador_principal: nuevoProyecto.value.investigador_principal,
    pit: nuevoProyecto.value.pit,
    imagen: nuevoProyecto.value.imagen,
    descripcion_corta_es: nuevoProyecto.value.descripcion_corta_es,
    descripcion_ampliada_es: nuevoProyecto.value.descripcion_ampliada_es,
    descripcion_corta_en: nuevoProyecto.value.descripcion_corta_en,
    descripcion_ampliada_en: nuevoProyecto.value.descripcion_ampliada_en,
    nextcloud: nuevoProyecto.value.nextcloud
  };
  try {
    const res = await peticionApi(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datosAEnviar)
    });
    if (res.ok) {
      alert(t('intranet.panel.proyectoGuardado'));
      volverDashboard('proyectos');
      cargarProyectos();
    } else {
      const data = await res.json();
      alert(t('intranet.panel.errorGuardar') + (traducirError(data.error) || JSON.stringify(data)));
    }
  } catch (e) {
    console.error("Error catastrofic al guardar:", e);
  }
}

const eliminarProyecto = async (id) => {
  if (!confirm(t('intranet.panel.confirmarBorrarProyecto'))) return
  try {
    const respuesta = await peticionApi(`${apiUrlProyectos}/${id}`, { method: 'DELETE' })
    if (respuesta.ok) {
      alert(t('intranet.panel.proyectoBorrado'))
      cargarProyectos()
    }
  } catch (error) { console.error(error) }
}
</script>

<template>
  <div class="intranet-wrapper">

    <div v-if="!estaLogueado" class="login-overlay">
      <div class="login-box">
        <!-- Enllaç del correu «He oblidat la contrasenya» -->
        <template v-if="tokenRestablir">
          <h2>{{ $t('intranet.panel.nuevaContrasena') }}</h2>
          <form @submit.prevent="guardarRestablir">
            <input type="password" v-model="restablir.nueva" :placeholder="$t('intranet.panel.nuevaMin')" minlength="8" autocomplete="new-password" required>
            <input type="password" v-model="restablir.repetida" :placeholder="$t('intranet.panel.repitela')" minlength="8" autocomplete="new-password" required>
            <p v-if="restablir.error" class="login-error">{{ restablir.error }}</p>
            <button type="submit" :disabled="restablir.guardando">{{ $t('intranet.panel.guardarMayus') }}</button>
          </form>
          <p class="olvido"><a href="#" @click.prevent="salirDeRestablir">{{ $t('intranet.panel.volverAcceso') }}</a></p>
        </template>
        <template v-else>
        <h2>{{ $t('intranet.panel.accesoTitulo') }}</h2>
        <p v-if="mensajeLogin" class="login-ok">{{ mensajeLogin }}</p>
        <form @submit.prevent="iniciarSesion">
          <input v-model="usuario" :placeholder="$t('intranet.panel.usuario')" autocomplete="username" required>
          <input type="password" v-model="password" :placeholder="$t('intranet.panel.contrasena')" autocomplete="current-password" required>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px; font-size: 0.9rem; color: #555;">
            <input type="checkbox" v-model="recordarSesion" id="recordar" style="width: auto; margin: 0;">
            <label for="recordar" style="cursor: pointer;">{{ $t('intranet.panel.recordar') }}</label>
          </div>
          <button type="submit">{{ $t('intranet.panel.entrar') }}</button>
        </form>
        <details class="olvido">
          <summary>{{ $t('intranet.panel.olvidoTitulo') }}</summary>
          <p>{{ $t('intranet.panel.olvidoTexto') }}</p>
          <form @submit.prevent="pedirEnlace">
            <input v-model="olvido.dato" :placeholder="$t('intranet.panel.usuarioOCorreo')" autocomplete="username" required>
            <button type="submit" class="btn-olvido" :disabled="olvido.enviando">{{ $t('intranet.panel.enviarEnlace') }}</button>
          </form>
          <p v-if="olvido.enviado" class="login-ok">{{ olvido.enviado }}</p>
          <p v-if="olvido.error" class="login-error">{{ olvido.error }}</p>
          <p class="nota-olvido">{{ $t('intranet.panel.olvidoNota') }}</p>
        </details>
        </template>
      </div>
    </div>

    <!-- Primer acceso (o contraseña puesta por un administrador): hay que cambiarla antes de seguir -->
    <div v-else-if="sesion.debe_cambiar" class="cambio-obligatorio">
      <MiCuenta :sesion="sesion" obligatorio @cambiada="sesion.debe_cambiar = false" @sesion-caducada="sesionCaducada" />
      <button @click="cerrarSesion" class="btn-salir-cambio">{{ $t('intranet.panel.cerrarSesion') }}</button>
    </div>

    <div v-else class="dashboard-grid">

      <aside class="sidebar" :class="{ abierto: menuAbierto }">
        <div class="sidebar-cabecera">
          <div class="sidebar-quien">
            <h3 class="sidebar-title">{{ $t('intranet.panel.menu.titulo') }}</h3>
            <p class="sidebar-usuario">👤 {{ sesion.nombre }}</p>
          </div>
          <!-- Només al mòbil: plega i desplega el menú -->
          <button type="button" class="btn-menu-movil" :aria-expanded="menuAbierto" aria-controls="menu-intranet" @click="menuAbierto = !menuAbierto">
            <span class="btn-menu-icono" aria-hidden="true">{{ menuAbierto ? '✕' : '☰' }}</span>
            <span class="btn-menu-texto">{{ opcionActual ? $t(opcionActual.texto) : $t('intranet.panel.menu.titulo') }}</span>
          </button>
        </div>
        <nav id="menu-intranet" class="sidebar-nav" :aria-label="$t('intranet.panel.menu.titulo')">
          <div v-for="g in gruposMenu" :key="g.titulo" class="grupo-menu">
            <p class="grupo-titulo">{{ $t(g.titulo) }}</p>
            <a v-for="item in g.items" :key="item.id" href="#" :class="{ active: seccionMenu === item.id }"
              :aria-current="seccionMenu === item.id ? 'page' : null" @click.prevent="irA(item.id)">{{ $t(item.texto) }}</a>
          </div>
        </nav>
        <div class="sidebar-pie">
          <!-- Sense prevent: sí que ha d'obrir la web pública en una pestanya nova -->
          <a href="/" target="_blank" class="btn-web">{{ $t('intranet.panel.menu.webPublica') }}</a>
          <button @click="cerrarSesion" class="btn-logout">{{ $t('intranet.panel.cerrarSesion') }}</button>
        </div>
      </aside>

      <main class="main-content">
        

        <CalendariEquip v-if="seccionActiva === 'calendari'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <DiarioActividad v-else-if="seccionActiva === 'diario'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <InformeSemestral v-else-if="seccionActiva === 'informe'" @sesion-caducada="sesionCaducada" />
        <MiCuenta v-else-if="seccionActiva === 'cuenta'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <GestionUsuarios v-else-if="seccionActiva === 'usuarios' && sesion.es_admin" @sesion-caducada="sesionCaducada" />
        <!-- Documentació: tot són pàgines (amb els fitxers adjunts) -->
        <PaginasDocs v-else-if="seccionActiva === 'documentacion'" :key="docsKey" :inicial="destinoInicial" @sesion-caducada="sesionCaducada" />
        <Compras v-else-if="seccionActiva === 'compras'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <ActasReunion v-else-if="seccionActiva === 'actas'" :sesion="sesion" :acta-inicial="destinoInicial.acta || null" @sesion-caducada="sesionCaducada" />
        <GestionEquipo v-else-if="seccionActiva === 'equipo'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <div v-else-if="seccionActiva === 'instrumentacion'" class="admin-panel">
          <button type="button" class="btn-tornar" @click="volverDashboard('instrumentos')">← {{ $t('intranet.panel.volverInstrumentos') }}</button>
          <h2>{{ $t(editandoId ? 'intranet.panel.editarInstrumento' : 'intranet.panel.registrarInstrumento') }}</h2>
          <form @submit.prevent="guardarInstrumento" class="grid-form">
            <div style="grid-column: span 2; display: flex; gap: 10px; margin-bottom: 5px;">
              <div style="flex: 1;">
                <label style="font-size: 0.85rem; font-weight: bold; color: #555;">{{ $t('intranet.panel.nombreEquipo') }}</label>
                <input v-model="nuevoEquipo.nombre" placeholder="Ex: CTD-48M" required style="width: 100%; box-sizing: border-box;">
              </div>
              <div style="flex: 1;">
                <label style="font-size: 0.85rem; font-weight: bold; color: #555;">{{ $t('intranet.panel.marca') }}</label>
                <input v-model="nuevoEquipo.marca" placeholder="Ex: Sea-Bird" style="width: 100%; box-sizing: border-box;">
              </div>
              <div style="flex: 1; background-color: #fff3cd; padding: 5px 10px; border-radius: 4px; border: 1px dashed #ffeeba;">
                <label style="color: #856404; font-size: 0.85rem; font-weight: bold;">{{ $t('intranet.panel.numeroSerie') }}</label>
                <input v-model="nuevoEquipo.numero_serie" placeholder="Ex: SN-180" style="background: white; width: 100%; box-sizing: border-box;" />
              </div>
            </div>

            <div style="grid-column: span 2; display: flex; gap: 10px; margin-bottom: 10px;">
              <select v-model="nuevoEquipo.categoria" required style="flex: 1;">
                <option value="" disabled selected>{{ $t('intranet.panel.categoria') }}</option>
                <option v-for="v in ['Física', 'Química', 'Biologia', 'Geologia']" :key="v" :value="v">{{ traducirValor(v) }}</option>
              </select>
              <select v-model="nuevoEquipo.subcategoria" required style="flex: 1;">
                <option value="" disabled selected>{{ $t('intranet.panel.subcategoria') }}</option>
                <option v-for="v in ['General', 'Sondes', 'Mostreig', 'Sistemes Estacionaris']" :key="v" :value="v">{{ traducirValor(v) }}</option>
              </select>
              <input v-model="nuevoEquipo.ultima_calibracion" type="date" required style="flex: 1;">
            </div>

            <div style="grid-column: span 2; margin-top: 10px;">
              <label style="font-weight: bold; color: #333;">{{ $t('intranet.panel.descripcionTecnica') }}</label>
              <div style="background: white; border-radius: 4px; border: 1px solid #ddd;">
                <QuillEditor theme="snow" v-model:content="nuevoEquipo.descripcion" contentType="html" :toolbar="opcionsEditor" />
              </div>
            </div>

            <div style="grid-column: span 2; margin-top: 10px; margin-bottom: 20px;">
              <label style="font-weight: bold; color: #333;">{{ $t('intranet.panel.parametros') }}</label>
              <div style="background: white; border-radius: 4px; border: 1px solid #ddd;">
                <QuillEditor theme="snow" v-model:content="nuevoEquipo.parametros_tecnicos" contentType="html" :toolbar="opcionsEditor" />
              </div>
            </div>

            <div style="grid-column: span 2; display: flex; gap: 10px;">
              <button type="submit" style="flex: 1; padding: 12px; font-weight: bold; background: #012169; color: white; border: none; border-radius: 4px; cursor: pointer;">
                {{ $t(editandoId ? 'intranet.panel.guardarCambios' : 'intranet.panel.registrarCatalogo') }}
              </button>
              <button v-if="editandoId" type="button" @click="volverDashboard('instrumentos')" style="flex: 0.3; background: #ccc; color: #333; font-weight: bold; padding: 12px; border: none; border-radius: 4px; cursor: pointer;">
                {{ $t('intranet.panel.cancelarX') }}
              </button>
            </div>
          </form>
        </div>

        <div v-else-if="seccionActiva === 'proyecto'" class="admin-panel">
          <button type="button" class="btn-tornar" @click="volverDashboard('proyectos')">← {{ $t('intranet.panel.volverProyectos') }}</button>
          <h2>{{ $t(editandoProyectoId ? 'intranet.panel.editarProyecto' : 'intranet.panel.registrarProyecto') }}</h2>
          <form @submit.prevent="guardarProyecto" class="grid-form">
            <label>{{ $t('intranet.panel.titulo') }}</label>
            <input v-model="nuevoProyecto.titulo" :placeholder="$t('intranet.panel.tituloPh')" required>
            <div style="display: flex; gap: 20px; margin-bottom: 15px;">
              <div style="flex: 1;">
                <label>{{ $t('intranet.panel.categoriaDos') }}</label>
                <select v-model="nuevoProyecto.categoria" required style="width: 100%;">
                  <option v-for="v in ['Infraestructura', 'Campanya', 'I+D+I', 'Divulgació científica', 'Plan Nacional', 'Contrato', 'Otro']" :key="v" :value="v">{{ traducirValor(v) }}</option>
                </select>
              </div>
              <div style="flex: 1;">
                <label>{{ $t('intranet.panel.estado') }}</label>
                <select v-model="nuevoProyecto.estado" required style="width: 100%;">
                  <option v-for="v in ['Sol·licitat', 'Aprovat', 'En Curs', 'Finalitzat']" :key="v" :value="v">{{ traducirValor(v) }}</option>
                </select>
              </div>
            </div>

            <div class="campo-form">
              <label>{{ $t('intranet.panel.ip') }}</label>
              <input type="text" v-model="nuevoProyecto.investigador_principal" placeholder="Ex: Maria Garcia, Joan Puig" class="input-texto">
            </div>

            <div class="campo-form">
              <label>{{ $t('intranet.panel.pit') }}</label>
              <input type="text" v-model="nuevoProyecto.pit" placeholder="Ex: Raül Ferrando" class="input-texto">
            </div>

            <div class="campo-form">
              <label>{{ $t('intranet.panel.nextcloud') }}</label>
              <input type="url" v-model="nuevoProyecto.nextcloud" pattern="https://.*" :placeholder="$t('intranet.panel.nextcloudPh')" class="input-texto">
              <small class="ayuda-campo">{{ $t('intranet.panel.nextcloudAyuda') }}</small>
            </div>

            <div class="campo-form">
              <label>{{ $t('intranet.panel.imagenProyecto') }}</label>
              <div class="campo-imagen">
                <input type="text" v-model="nuevoProyecto.imagen" list="fotos-web" :placeholder="$t('intranet.panel.imagenProyectoPh')" class="input-texto">
                <img v-if="nuevoProyecto.imagen" :src="nuevoProyecto.imagen" alt="" class="vista-imagen">
              </div>
              <datalist id="fotos-web"><option v-for="f in FOTOS_WEB" :key="f" :value="f"></option></datalist>
            </div>

            <!-- Descripcions en tres idiomes: el català és el principal -->
            <div class="pestanas-idioma" role="group" :aria-label="$t('intranet.panel.idiomaTextos')">
              <button v-for="l in IDIOMAS_TEXTO" :key="l" type="button" :class="{ activa: idiomaTexto === l }" :aria-pressed="idiomaTexto === l" @click="idiomaTexto = l">
                {{ l.toUpperCase() }}<span v-if="l !== 'ca' && !(nuevoProyecto['descripcion_corta_' + l] || '').trim()" class="falta" :title="$t('intranet.panel.sinTraducir')">·</span>
              </button>
              <span class="nota-idioma">{{ $t('intranet.panel.notaIdiomas') }}</span>
            </div>
            <div style="margin-bottom: 15px;">
              <label>{{ $t('intranet.panel.descCorta') }}</label>
              <textarea v-model="nuevoProyecto['descripcion_corta' + sufijoTexto]" rows="2" maxlength="300" :placeholder="$t('intranet.panel.descCortaPh')" style="width: 100%; resize: none; border: 1px solid #ccc; border-radius: 4px; padding: 8px; font-family: inherit;"></textarea>
            </div>

            <div style="margin-bottom: 15px;">
              <label>{{ $t('intranet.panel.descAmpliada') }}</label>
              <div style="background: white; border: 1px solid #ddd;">
                <QuillEditor :key="idiomaTexto" theme="snow" v-model:content="nuevoProyecto['descripcion_ampliada' + sufijoTexto]" contentType="html" :toolbar="opcionsEditor" />
              </div>
            </div>

            <button type="submit" class="btn-submit-main" style="margin-top: 10px; padding: 15px; cursor: pointer;">
              {{ $t(editandoProyectoId ? 'intranet.panel.guardarCambios' : 'intranet.panel.registrarProyectoBtn') }}
            </button>
          </form>
        </div>

        <!-- Projectes i campanyes -->
        <div v-else-if="seccionActiva === 'proyectos'" class="panel-lista">
          <div class="panel-lista-cabecera">
            <h2>{{ $t('intranet.panel.proyectos', { n: proyectos.length }) }}</h2>
            <button type="button" @click="seccionActiva = 'proyecto'" class="btn-nou">{{ $t('intranet.panel.nuevoProyecto') }}</button>
          </div>
          <div class="tabla-scroll">
            <table class="tabla-instrumentos">
              <tr v-for="proj in proyectos" :key="proj.id">
                <td>
                  <strong style="color: #0086c0; font-size: 1.1rem;">{{ proj.titulo }}</strong> <br>
                  <small style="color: #666;">{{ traducirValor(proj.categoria) }} | IP: {{ proj.investigador_principal || $t('intranet.panel.sinAsignar') }}</small>
                </td>
                <td><span class="badge-estado">{{ traducirValor(proj.estado) }}</span></td>
                <td class="acciones-fila">
                  <a v-if="proj.nextcloud" :href="proj.nextcloud" target="_blank" rel="noopener noreferrer" class="btn-saco" :title="$t('intranet.panel.abrirNextcloud')">📂 SACO</a>
                  <button @click="cargarParaEditarProyecto(proj)" class="btn-edit">{{ $t('intranet.comun.editar') }}</button>
                  <button @click="eliminarProyecto(proj.id)" class="btn-delete">{{ $t('intranet.comun.borrar') }}</button>
                </td>
              </tr>
            </table>
          </div>
        </div>

        <!-- Inventari d'instruments -->
        <div v-else-if="seccionActiva === 'instrumentos'" class="panel-lista">
          <div class="panel-lista-cabecera">
            <h2>{{ $t('intranet.panel.instrumentos', { n: instrumentos.length }) }}</h2>
            <button type="button" @click="seccionActiva = 'instrumentacion'" class="btn-nou">{{ $t('intranet.panel.nuevoInstrumento') }}</button>
          </div>
          <div class="tabla-scroll">
            <table class="tabla-instrumentos">
              <tr v-for="inst in instrumentos" :key="inst.id">
                <td>
                  <strong>{{ inst.nombre }}</strong> <br>
                  <small>{{ inst.marca }}</small>
                  <span v-if="inst.numero_serie" style="color: #d32f2f; font-size: 0.85em; margin-left: 10px; background: #ffebee; padding: 2px 6px; border-radius: 4px;">
                    🔒 SN: {{ inst.numero_serie }}
                  </span>
                </td>
                <td class="acciones-fila">
                  <button @click="cargarParaEditar(inst)" class="btn-edit">{{ $t('intranet.comun.editar') }}</button>
                  <button @click="eliminarInstrumento(inst.id)" class="btn-delete">{{ $t('intranet.comun.borrar') }}</button>
                </td>
              </tr>
            </table>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* ALÇADA MINIMA EDITOR */
:deep(.ql-editor) {
  min-height: 150px;
}

.tabla-instrumentos { width: 100%; border-collapse: collapse; background: white; }
.tabla-instrumentos td { padding: 15px; border-bottom: 1px solid #eee; vertical-align: middle; }
.btn-delete { background: #d9534f; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; }
.btn-edit { background: #0086c0; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; }

.intranet-wrapper { min-height: 100vh; }
.login-overlay { position: fixed; inset: 0; background: #012169; display: flex; align-items: center; justify-content: center; z-index: 100; }
.login-box { background: white; padding: 40px; border-radius: 8px; width: 300px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2); }
.login-box input { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.olvido { margin-top: 15px; font-size: 0.85rem; color: #444; }
.olvido summary { cursor: pointer; color: #0086c0; text-align: center; }
.olvido p { margin: 8px 0; line-height: 1.4; }
.olvido a { color: #0086c0; }
.login-box .btn-olvido { background: white; border: 1px solid #0086c0; color: #0086c0; }
.nota-olvido { color: #666; font-size: 0.8rem; }
.login-ok { color: #198754; font-weight: bold; font-size: 0.85rem; }
.login-error { color: #b02a37; font-weight: bold; font-size: 0.85rem; margin: -5px 0 10px; }
.login-box button { width: 100%; padding: 10px; background: #8cc63f; color: #012169; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; }

.dashboard-grid { display: flex; min-height: 100vh; }
.sidebar { width: 260px; flex-shrink: 0; background: #012169; color: white; padding: 22px 16px; display: flex; flex-direction: column; }
.sidebar-title { margin: 0 0 4px; padding: 0 8px; font-size: 1.15rem; }
.sidebar-usuario { color: #8cc63f; font-size: 0.85rem; margin: 0 0 6px; padding: 0 8px; }
.btn-menu-movil { display: none; }
.grupo-titulo { margin: 16px 0 4px; padding: 0 10px; font-size: 0.7rem; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; color: #8fa3c8; }
.sidebar-nav a { display: block; color: #d6deeb; padding: 8px 10px; margin-bottom: 2px; text-decoration: none; border-radius: 6px; border-left: 3px solid transparent;
  font-size: 0.92rem; line-height: 1.3; transition: background 0.15s, color 0.15s; }
.sidebar-nav a:hover { background: rgba(255, 255, 255, 0.08); color: white; }
.sidebar-nav a.active { color: white; font-weight: bold; border-left-color: #8cc63f; background: rgba(140, 198, 63, 0.16); }
.sidebar-nav a:focus-visible, .btn-menu-movil:focus-visible { outline: 2px solid #8cc63f; outline-offset: 2px; }
.sidebar-pie { display: flex; flex-direction: column; gap: 8px; margin-top: 22px; }
.btn-web { display: block; background: #8cc63f; color: #012169 !important; font-weight: bold; border-radius: 6px; padding: 9px 10px; text-align: center; text-decoration: none; font-size: 0.9rem; }
.btn-web:hover { background: #a5d65f; }
.btn-logout { background: none; border: 1px solid rgba(255, 255, 255, 0.6); color: white; padding: 8px 10px; cursor: pointer; border-radius: 6px; font: inherit; font-size: 0.9rem; }
.btn-logout:hover { background: rgba(255, 255, 255, 0.1); }

.main-content { flex-grow: 1; min-width: 0; padding: 40px; background: #f4f7f9; }
.grid-form { display: grid; gap: 10px; max-width: 800px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); }
.grid-form input, .grid-form select { padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
.badge-estado { background-color: #e1eef5; color: #0086c0; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: bold; }

.acordeon-dash { background: white; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05); overflow: hidden; }
.acordeon-dash-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background-color: #ffffff; border-bottom: 1px solid #eee; cursor: pointer; }
.pestanas-idioma { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: 4px 0 10px; }
.pestanas-idioma button { padding: 6px 14px; border: 1px solid #ccd5df; background: white; border-radius: 16px; font-weight: bold; cursor: pointer; color: #012169; }
.pestanas-idioma button.activa { background: #012169; color: white; border-color: #012169; }
.pestanas-idioma .falta { color: #d9661a; font-size: 1.4rem; line-height: 0; margin-left: 2px; }
.nota-idioma { font-size: 0.8rem; color: #666; }
.campo-imagen { display: flex; gap: 10px; align-items: center; }
.campo-imagen .input-texto { flex: 1; }
.vista-imagen { width: 96px; height: 60px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd; }
.pestanas-docs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: -4px; }
.pestanas-docs button { padding: 9px 18px; border: 1px solid #ccd5df; border-bottom: none; background: #e9eef3; color: #012169; border-radius: 8px 8px 0 0; font: inherit; font-weight: bold; cursor: pointer; }
.pestanas-docs button.activa { background: white; border-color: #17a2b8; box-shadow: 0 -2px 0 #17a2b8 inset; }
.panel-lista { background: white; border-radius: 10px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #012169; }
.panel-lista-cabecera { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.panel-lista-cabecera h2 { margin: 0; color: #012169; font-size: 1.4rem; }
.tabla-scroll { overflow-x: auto; }
.acciones-fila { text-align: right; white-space: nowrap; }
.acciones-fila .btn-edit { margin-right: 5px; }
.btn-saco { display: inline-block; margin-right: 5px; padding: 8px 12px; border-radius: 4px; background: #e8f1fb; color: #0b5cad; font-weight: bold; text-decoration: none; border: 1px solid #c4dbf2; }
.btn-saco:hover { background: #d6e8fa; }
.ayuda-campo { color: #777; font-size: 0.8rem; }
.btn-tornar { background: none; border: none; color: #0086c0; font: inherit; font-weight: bold; cursor: pointer; padding: 0; margin-bottom: 10px; }
.btn-nou { background: #8cc63f; color: #012169; border: none; padding: 6px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }

/* Móvil: el menú pasa arriba y el contenido ocupa todo el ancho */
@media (max-width: 768px) {
  .dashboard-grid { flex-direction: column; min-height: 0; }
  /* Una sola barra: qui ets + botó «☰ secció actual»; en obrir-lo, graella de 2 columnes */
  .sidebar { width: auto; padding: 10px 12px; }
  .sidebar-cabecera { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
  .sidebar-quien { min-width: 0; }
  .sidebar-title { font-size: 1rem; padding: 0; }
  .sidebar-usuario { margin: 0; padding: 0; font-size: 0.78rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .btn-menu-movil { display: flex; align-items: center; gap: 8px; min-width: 0; max-width: 62%; padding: 8px 12px; border-radius: 6px;
    background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.35); color: white; font: inherit; font-size: 0.85rem; font-weight: bold; cursor: pointer; }
  .btn-menu-icono { font-size: 1.05rem; line-height: 1; }
  .btn-menu-texto { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .sidebar-nav, .sidebar-pie { display: none; }
  .sidebar.abierto .sidebar-nav { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 10px; }
  .grupo-menu { display: contents; }
  .grupo-titulo { grid-column: 1 / -1; margin: 6px 0 0; padding: 0 2px; }
  .sidebar-nav a { margin: 0; padding: 9px 10px; font-size: 0.84rem; background: rgba(255, 255, 255, 0.07); border-left: none; }
  .sidebar-nav a.active { background: rgba(140, 198, 63, 0.25); box-shadow: inset 0 -2px 0 #8cc63f; }
  .sidebar.abierto .sidebar-pie { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 12px; }
  .btn-web, .btn-logout { padding: 8px; font-size: 0.84rem; }
  .main-content { padding: 14px 10px; min-width: 0; }
}
.cambio-obligatorio { min-height: 70vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px; padding: 40px 15px; background: #f4f7f9; }
.btn-salir-cambio { background: none; border: none; color: #012169; text-decoration: underline; cursor: pointer; }
</style>