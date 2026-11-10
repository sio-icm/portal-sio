<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { traducirError, traducirValor } from '../i18n'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import BibliotecaDocs from './BibliotecaDocs.vue'
import GestionEquipo from './GestionEquipo.vue'
import DiarioActividad from './DiarioActividad.vue'
import InformeSemestral from './InformeSemestral.vue'
import GestionUsuarios from './GestionUsuarios.vue'
import MiCuenta from './MiCuenta.vue'
import CalendariEquip from './CalendariEquip.vue'
import ResumenCalendario from './ResumenCalendario.vue'

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
const seccionActiva = ref('dashboard') // 'dashboard', 'calendari', 'diario', 'informe', 'cuenta', 'usuarios', 'equipo', 'documentacion', 'instrumentacion', 'proyecto'

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
  titulo: '', categoria: '', estado: '', descripcion_corta: '', descripcion_ampliada: '', investigador_principal: '', pit: ''
})

// CONFIGURACIÓ DE LA BARRA D'EINES (Amb icona d'Imatge 🖼️)
const opcionsEditor = [
  [{ 'header': [1, 2, 3, false] }],
  ['bold', 'italic', 'underline'],
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  ['link', 'image'], 
  ['clean']
]

// CONTROL DELS ACORDIONS DEL DASHBOARD
const acordeonesDash = ref({
  proyectos: true,
  instrumentos: true
})

const toggleDashboard = (seccion) => {
  acordeonesDash.value[seccion] = !acordeonesDash.value[seccion]
}

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
      seccionActiva.value = 'dashboard'
      estaLogueado.value = true
      cargarInstrumentos()
      cargarProyectos()
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

const volverDashboard = () => {
  editandoId.value = null
  editandoProyectoId.value = null
  nuevoEquipo.value = { nombre: '', marca: '', numero_serie: '', categoria: '', subcategoria: '', ultima_calibracion: '', descripcion: '', parametros_tecnicos: '' }
  nuevoProyecto.value = { titulo: '', categoria: '', estado: '', descripcion_corta: '', descripcion_ampliada: '', investigador_principal: '', pit: '' }
  seccionActiva.value = 'dashboard'
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
      volverDashboard()
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
    pit: proj.pit || ''
  };
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
    pit: nuevoProyecto.value.pit 
  };
  try {
    const res = await peticionApi(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datosAEnviar)
    });
    if (res.ok) {
      alert(t('intranet.panel.proyectoGuardado'));
      volverDashboard();
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

      <aside class="sidebar">
        <h3 class="sidebar-title">{{ $t('intranet.panel.menu.titulo') }}</h3>
        <p class="sidebar-usuario">👤 {{ sesion.nombre }}</p>
<nav class="sidebar-nav">
          <a href="#" @click.prevent="volverDashboard" :class="{ active: seccionActiva === 'dashboard' }">{{ $t('intranet.panel.menu.general') }}</a>
          <a href="#" @click.prevent="seccionActiva = 'calendari'" :class="{ active: seccionActiva === 'calendari' }">{{ $t('intranet.panel.menu.calendario') }}</a>
          <a href="#" @click.prevent="seccionActiva = 'diario'" :class="{ active: seccionActiva === 'diario' }">{{ $t('intranet.panel.menu.diario') }}</a>
          <a href="#" @click.prevent="seccionActiva = 'informe'" :class="{ active: seccionActiva === 'informe' }">{{ $t('intranet.panel.menu.informe') }}</a>
          <a href="#" @click.prevent="seccionActiva = 'equipo'" :class="{ active: seccionActiva === 'equipo' }">{{ $t('intranet.panel.menu.equipo') }}</a>
          <a href="#" @click.prevent="seccionActiva = 'documentacion'" :class="{ active: seccionActiva === 'documentacion' }">{{ $t('intranet.panel.menu.documentacion') }}</a>
          <a href="#" @click.prevent="seccionActiva = 'instrumentacion'" :class="{ active: seccionActiva === 'instrumentacion' }">
            {{ $t(editandoId ? 'intranet.panel.menu.editandoInstrumento' : 'intranet.panel.menu.altaInstrumento') }}
          </a>
          <a href="#" @click.prevent="seccionActiva = 'proyecto'" :class="{ active: seccionActiva === 'proyecto' }">
            {{ $t(editandoProyectoId ? 'intranet.panel.menu.editandoProyecto' : 'intranet.panel.menu.altaProyecto') }}
          </a>
          <a href="#" @click.prevent="seccionActiva = 'cuenta'" :class="{ active: seccionActiva === 'cuenta' }">{{ $t('intranet.panel.menu.cuenta') }}</a>
          <a v-if="sesion.es_admin" href="#" @click.prevent="seccionActiva = 'usuarios'" :class="{ active: seccionActiva === 'usuarios' }">{{ $t('intranet.panel.menu.usuarios') }}</a>
          <!-- Este lo dejamos sin prevent porque SÍ queremos que abra una pestaña nueva hacia la web pública -->
          <a href="/" target="_blank" class="btn-web">{{ $t('intranet.panel.menu.webPublica') }}</a>
        </nav>
        <button @click="cerrarSesion" class="btn-logout">{{ $t('intranet.panel.cerrarSesion') }}</button>
      </aside>

      <main class="main-content">
        

        <CalendariEquip v-if="seccionActiva === 'calendari'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <DiarioActividad v-else-if="seccionActiva === 'diario'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <InformeSemestral v-else-if="seccionActiva === 'informe'" @sesion-caducada="sesionCaducada" />
        <MiCuenta v-else-if="seccionActiva === 'cuenta'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <GestionUsuarios v-else-if="seccionActiva === 'usuarios' && sesion.es_admin" @sesion-caducada="sesionCaducada" />
        <BibliotecaDocs v-else-if="seccionActiva === 'documentacion'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <GestionEquipo v-else-if="seccionActiva === 'equipo'" :sesion="sesion" @sesion-caducada="sesionCaducada" />
        <div v-else-if="seccionActiva === 'instrumentacion'" class="admin-panel">
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
              <button v-if="editandoId" type="button" @click="volverDashboard" style="flex: 0.3; background: #ccc; color: #333; font-weight: bold; padding: 12px; border: none; border-radius: 4px; cursor: pointer;">
                {{ $t('intranet.panel.cancelarX') }}
              </button>
            </div>
          </form>
        </div>

        <div v-else-if="seccionActiva === 'proyecto'" class="admin-panel">
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

            <div style="margin-bottom: 15px;">
              <label>{{ $t('intranet.panel.descCorta') }}</label>
              <textarea v-model="nuevoProyecto.descripcion_corta" rows="2" maxlength="150" :placeholder="$t('intranet.panel.descCortaPh')" style="width: 100%; resize: none; border: 1px solid #ccc; border-radius: 4px; padding: 8px; font-family: inherit;"></textarea>
            </div>

            <div style="margin-bottom: 15px;">
              <label>{{ $t('intranet.panel.descAmpliada') }}</label>
              <div style="background: white; border: 1px solid #ddd;">
                <QuillEditor theme="snow" v-model:content="nuevoProyecto.descripcion_ampliada" contentType="html" :toolbar="opcionsEditor" />
              </div>
            </div>

            <button type="submit" class="btn-submit-main" style="margin-top: 10px; padding: 15px; cursor: pointer;">
              {{ $t(editandoProyectoId ? 'intranet.panel.guardarCambios' : 'intranet.panel.registrarProyectoBtn') }}
            </button>
          </form>
        </div>

        <div v-else class="dashboard-view">
          <ResumenCalendario :sesion="sesion" @abrir="seccionActiva = 'calendari'" @sesion-caducada="sesionCaducada" />
          
          <div class="acordeon-dash">
            <div class="acordeon-dash-header" @click="toggleDashboard('proyectos')">
              <div style="display: flex; align-items: center; gap: 15px;">
                <h3 style="margin: 0; color: #012169;">{{ $t('intranet.panel.proyectos', { n: proyectos.length }) }}</h3>
              </div>
              <div style="display: flex; align-items: center; gap: 20px;">
                <button @click.stop="seccionActiva = 'proyecto'" class="btn-nou">{{ $t('intranet.panel.nuevoProyecto') }}</button>
                <span style="font-size: 1.5rem; color: #0086c0; font-weight: bold; width: 20px; text-align: center;">
                  {{ acordeonesDash.proyectos ? '−' : '+' }}
                </span>
              </div>
            </div>
            <div class="acordeon-dash-body" v-show="acordeonesDash.proyectos">
              <table class="tabla-instrumentos">
                <tr v-for="proj in proyectos" :key="proj.id">
                  <td>
                    <strong style="color: #0086c0; font-size: 1.1rem;">{{ proj.titulo }}</strong> <br>
                    <small style="color: #666;">{{ traducirValor(proj.categoria) }} | IP: {{ proj.investigador_principal || $t('intranet.panel.sinAsignar') }}</small>
                  </td>
                  <td><span class="badge-estado">{{ traducirValor(proj.estado) }}</span></td>
                  <td style="text-align: right; width: 220px;">
                    <button @click="cargarParaEditarProyecto(proj)" class="btn-edit" style="margin-right: 5px;">{{ $t('intranet.comun.editar') }}</button>
                    <button @click="eliminarProyecto(proj.id)" class="btn-delete">{{ $t('intranet.comun.borrar') }}</button>
                  </td>
                </tr>
              </table>
            </div>
          </div>

          <div class="acordeon-dash">
            <div class="acordeon-dash-header" @click="toggleDashboard('instrumentos')">
              <div style="display: flex; align-items: center; gap: 15px;">
                <h3 style="margin: 0; color: #012169;">{{ $t('intranet.panel.instrumentos', { n: instrumentos.length }) }}</h3>
              </div>
              <div style="display: flex; align-items: center; gap: 20px;">
                <button @click.stop="seccionActiva = 'instrumentacion'" class="btn-nou">{{ $t('intranet.panel.nuevoInstrumento') }}</button>
                <span style="font-size: 1.5rem; color: #0086c0; font-weight: bold; width: 20px; text-align: center;">
                  {{ acordeonesDash.instrumentos ? '−' : '+' }}
                </span>
              </div>
            </div>
            <div class="acordeon-dash-body" v-show="acordeonesDash.instrumentos">
              <table class="tabla-instrumentos">
                <tr v-for="inst in instrumentos" :key="inst.id">
                  <td>
                    <strong>{{ inst.nombre }}</strong> <br>
                    <small>{{ inst.marca }}</small>
                    <span v-if="inst.numero_serie" style="color: #d32f2f; font-size: 0.85em; margin-left: 10px; background: #ffebee; padding: 2px 6px; border-radius: 4px;">
                      🔒 SN: {{ inst.numero_serie }}
                    </span>
                  </td>
                  <td style="text-align: right; width: 220px;">
                    <button @click="cargarParaEditar(inst)" class="btn-edit" style="margin-right: 5px;">{{ $t('intranet.comun.editar') }}</button>
                    <button @click="eliminarInstrumento(inst.id)" class="btn-delete">{{ $t('intranet.comun.borrar') }}</button>
                  </td>
                </tr>
              </table>
            </div>
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

.btn-web { background: #8cc63f; color: white !important; margin-top: 15px; border-radius: 4px; padding: 10px; text-align: center; }
.btn-web:hover { background: #7ab335; }
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
.sidebar { width: 250px; flex-shrink: 0; background: #012169; color: white; padding: 20px; display: flex; flex-direction: column; }
.sidebar-usuario { color: #8cc63f; font-size: 0.85rem; margin: -5px 0 15px; }
.sidebar-nav a { display: block; color: #ccc; padding: 10px; text-decoration: none; border-radius: 4px; margin-bottom: 5px; }
.sidebar-nav a.active { color: white; font-weight: bold; border-left: 3px solid #8cc63f; background: rgba(255, 255, 255, 0.05); }
.btn-logout { margin-top: 12px; background: none; border: 1px solid white; color: white; padding: 10px; cursor: pointer; border-radius: 4px; }

.main-content { flex-grow: 1; min-width: 0; padding: 40px; background: #f4f7f9; }
.grid-form { display: grid; gap: 10px; max-width: 800px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); }
.grid-form input, .grid-form select { padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
.badge-estado { background-color: #e1eef5; color: #0086c0; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: bold; }

.acordeon-dash { background: white; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05); overflow: hidden; }
.acordeon-dash-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background-color: #ffffff; border-bottom: 1px solid #eee; cursor: pointer; }
.btn-nou { background: #8cc63f; color: #012169; border: none; padding: 6px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }

/* Móvil: el menú pasa arriba y el contenido ocupa todo el ancho */
@media (max-width: 768px) {
  .dashboard-grid { flex-direction: column; min-height: 0; }
  .sidebar { width: auto; padding: 12px 14px; }
  .sidebar-title { margin: 0 0 4px; }
  .sidebar-nav { display: flex; flex-wrap: wrap; gap: 4px; }
  .sidebar-nav a { margin: 0; padding: 6px 9px; font-size: 0.85rem; background: rgba(255, 255, 255, 0.06); }
  .sidebar-nav a.active { border-left: none; box-shadow: inset 0 -2px 0 #8cc63f; }
  .btn-logout { margin-top: 10px; padding: 6px; }
  .main-content { padding: 14px 10px; min-width: 0; }
}
.cambio-obligatorio { min-height: 70vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px; padding: 40px 15px; background: #f4f7f9; }
.btn-salir-cambio { background: none; border: none; color: #012169; text-decoration: underline; cursor: pointer; }
</style>