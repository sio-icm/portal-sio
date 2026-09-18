<script setup>
import { ref, onMounted } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import GestionTickets from './GestionTickets.vue'
import GestionAlbaranes from './GestionAlbaranes.vue'
import BibliotecaDocs from './BibliotecaDocs.vue'
import GestionEquipo from './GestionEquipo.vue'

const apiUrl = 'http://localhost:5000/api/instrumentos'
const apiUrlProyectos = 'http://localhost:5000/api/proyectos'

const estaLogueado = ref(false)
const seccionActiva = ref('dashboard') // 'dashboard', 'instrumentacion', 'proyecto', 'tickets'
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
    const respuesta = await fetch(apiUrl)
    instrumentos.value = await respuesta.json()
  } catch (error) { console.error("Error carregant instruments:", error) }
}

const cargarProyectos = async () => {
  try {
    const respuesta = await fetch(apiUrlProyectos)
    proyectos.value = await respuesta.json()
  } catch (error) { console.error("Error carregant projectes:", error) }
}

onMounted(() => {
  if (sessionStorage.getItem('sio_auth') === 'true' || localStorage.getItem('sio_auth') === 'true') {
    estaLogueado.value = true
    cargarInstrumentos()
    cargarProyectos()
  }
})

// ==============================
// AUTENTICACIÓ
// ==============================
const iniciarSesion = () => {
  if (usuario.value === 'sio' && password.value === 'admin') {
    if (recordarSesion.value) {
      localStorage.setItem('sio_auth', 'true')
    } else {
      sessionStorage.setItem('sio_auth', 'true')
    }
    estaLogueado.value = true
    cargarInstrumentos()
    cargarProyectos()
  } else {
    alert("Usuari o contrasenya incorrectes")
  }
}

const cerrarSesion = () => {
  sessionStorage.removeItem('sio_auth')
  localStorage.removeItem('sio_auth')
  estaLogueado.value = false
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
    const respuesta = await fetch(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(nuevoEquipo.value)
    })
    if (respuesta.ok) {
      alert(editandoId.value ? "✅ Instrument actualitzat!" : "✅ Equip registrat!")
      volverDashboard()
      cargarInstrumentos()
    }
  } catch (error) { console.error(error) }
}

const eliminarInstrumento = async (id) => {
  if (!confirm("Segur que vols esborrar aquest instrument?")) return
  try {
    const respuesta = await fetch(`${apiUrl}/${id}`, { method: 'DELETE' })
    if (respuesta.ok) {
      alert("🗑️ Instrument eliminat")
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
    const res = await fetch(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datosAEnviar)
    });
    if (res.ok) {
      alert("✅ Projecte desat correctament!");
      volverDashboard();
      cargarProyectos();
    } else {
      const data = await res.json();
      alert("Error al guardar: " + JSON.stringify(data));
    }
  } catch (e) {
    console.error("Error catastrofic al guardar:", e);
  }
}

const eliminarProyecto = async (id) => {
  if (!confirm("Segur que vols esborrar aquest projecte/campanya?")) return
  try {
    const respuesta = await fetch(`${apiUrlProyectos}/${id}`, { method: 'DELETE' })
    if (respuesta.ok) {
      alert("🗑️ Projecte eliminat")
      cargarProyectos()
    }
  } catch (error) { console.error(error) }
}
</script>

<template>
  <div class="intranet-wrapper">

    <div v-if="!estaLogueado" class="login-overlay">
      <div class="login-box">
        <h2>Accés SIO</h2>
        <form @submit.prevent="iniciarSesion">
          <input v-model="usuario" placeholder="Usuari" required>
          <input type="password" v-model="password" placeholder="Contrasenya" required>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px; font-size: 0.9rem; color: #555;">
            <input type="checkbox" v-model="recordarSesion" id="recordar" style="width: auto; margin: 0;">
            <label for="recordar" style="cursor: pointer;">Recordar sessió</label>
          </div>
          <button type="submit">ENTRAR</button>
        </form>
      </div>
    </div>

    <div v-else class="dashboard-grid">

      <aside class="sidebar">
        <h3 class="sidebar-title">Panel SIO</h3>
<nav class="sidebar-nav">
          <a href="#" @click.prevent="volverDashboard" :class="{ active: seccionActiva === 'dashboard' }">📊 Visió General</a>
          <a href="#" @click.prevent="seccionActiva = 'equipo'" :class="{ active: seccionActiva === 'equipo' }">👥 Gestión del Equipo</a>
          <a href="#" @click.prevent="seccionActiva = 'tickets'" :class="{ active: seccionActiva === 'tickets' }">🎫 Gestió de Tickets</a>
          <a href="#" @click.prevent="seccionActiva = 'albaranes'" :class="{ active: seccionActiva === 'albaranes' }">📦 Gestió d'Albarans</a>
          <a href="#" @click.prevent="seccionActiva = 'documentacion'" :class="{ active: seccionActiva === 'documentacion' }">📚 Documentació i Manuals</a>
          <a href="#" @click.prevent="seccionActiva = 'instrumentacion'" :class="{ active: seccionActiva === 'instrumentacion' }">
            {{ editandoId ? '✏️ Editant Instrument' : '🛠️ Alta Instrument' }}
          </a>
          <a href="#" @click.prevent="seccionActiva = 'proyecto'" :class="{ active: seccionActiva === 'proyecto' }">
            {{ editandoProyectoId ? '✏️ Editant Projecte' : '🚀 Alta Projecte' }}
          </a>
          <!-- Este lo dejamos sin prevent porque SÍ queremos que abra una pestaña nueva hacia la web pública -->
          <a href="/" target="_blank" class="btn-web">🌐 Veure Web Pública</a>
        </nav>
        <button @click="cerrarSesion" class="btn-logout">Tancar Sessió</button>
      </aside>

      <main class="main-content">
        

        <div v-if="seccionActiva === 'tickets'">
          <GestionTickets />
        </div>

        <div v-else-if="seccionActiva === 'albaranes'">
          <GestionAlbaranes />
        </div>
        <div v-else-if="seccionActiva === 'documentacion'">
        <BibliotecaDocs />
        </div>
        <div v-else-if="seccionActiva === 'equipo'">
        <GestionEquipo />
        </div>
        <div v-else-if="seccionActiva === 'instrumentacion'" class="admin-panel">
          <h2>{{ editandoId ? '✏️ Editar Instrument' : '➕ Registrar Nou Instrument' }}</h2>
          <form @submit.prevent="guardarInstrumento" class="grid-form">
            <div style="grid-column: span 2; display: flex; gap: 10px; margin-bottom: 5px;">
              <div style="flex: 1;">
                <label style="font-size: 0.85rem; font-weight: bold; color: #555;">Nom de l'equip:</label>
                <input v-model="nuevoEquipo.nombre" placeholder="Ex: CTD-48M" required style="width: 100%; box-sizing: border-box;">
              </div>
              <div style="flex: 1;">
                <label style="font-size: 0.85rem; font-weight: bold; color: #555;">Marca / Fabricant:</label>
                <input v-model="nuevoEquipo.marca" placeholder="Ex: Sea-Bird" style="width: 100%; box-sizing: border-box;">
              </div>
              <div style="flex: 1; background-color: #fff3cd; padding: 5px 10px; border-radius: 4px; border: 1px dashed #ffeeba;">
                <label style="color: #856404; font-size: 0.85rem; font-weight: bold;">🔒 Número de Sèrie:</label>
                <input v-model="nuevoEquipo.numero_serie" placeholder="Ex: SN-180" style="background: white; width: 100%; box-sizing: border-box;" />
              </div>
            </div>

            <div style="grid-column: span 2; display: flex; gap: 10px; margin-bottom: 10px;">
              <select v-model="nuevoEquipo.categoria" required style="flex: 1;">
                <option value="" disabled selected>Categoria</option>
                <option value="Física">Física</option>
                <option value="Química">Química</option>
                <option value="Biologia">Biologia</option>
                <option value="Geologia">Geologia</option>
              </select>
              <select v-model="nuevoEquipo.subcategoria" required style="flex: 1;">
                <option value="" disabled selected>Subcategoria</option>
                <option value="General">General</option>
                <option value="Sondes">Sondes</option>
                <option value="Mostreig">Mostreig</option>
                <option value="Sistemes Estacionaris">Sistemes Estacionaris</option>
              </select>
              <input v-model="nuevoEquipo.ultima_calibracion" type="date" required style="flex: 1;">
            </div>

            <div style="grid-column: span 2; margin-top: 10px;">
              <label style="font-weight: bold; color: #333;">Descripció tècnica:</label>
              <div style="background: white; border-radius: 4px; border: 1px solid #ddd;">
                <QuillEditor theme="snow" v-model:content="nuevoEquipo.descripcion" contentType="html" :toolbar="opcionsEditor" />
              </div>
            </div>

            <div style="grid-column: span 2; margin-top: 10px; margin-bottom: 20px;">
              <label style="font-weight: bold; color: #333;">Paràmetres / Manuals:</label>
              <div style="background: white; border-radius: 4px; border: 1px solid #ddd;">
                <QuillEditor theme="snow" v-model:content="nuevoEquipo.parametros_tecnicos" contentType="html" :toolbar="opcionsEditor" />
              </div>
            </div>

            <div style="grid-column: span 2; display: flex; gap: 10px;">
              <button type="submit" style="flex: 1; padding: 12px; font-weight: bold; background: #012169; color: white; border: none; border-radius: 4px; cursor: pointer;">
                {{ editandoId ? '💾 Desar Canvis' : '➕ Registrar al Catàleg' }}
              </button>
              <button v-if="editandoId" type="button" @click="volverDashboard" style="flex: 0.3; background: #ccc; color: #333; font-weight: bold; padding: 12px; border: none; border-radius: 4px; cursor: pointer;">
                ❌ Cancel·lar
              </button>
            </div>
          </form>
        </div>

        <div v-else-if="seccionActiva === 'proyecto'" class="admin-panel">
          <h2>{{ editandoProyectoId ? '✏️ Editar Projecte' : '🚀 Registrar Nou Projecte' }}</h2>
          <form @submit.prevent="guardarProyecto" class="grid-form">
            <label>Títol:</label>
            <input v-model="nuevoProyecto.titulo" placeholder="Títol del projecte" required>
            <div style="display: flex; gap: 20px; margin-bottom: 15px;">
              <div style="flex: 1;">
                <label>Categoria:</label>
                <select v-model="nuevoProyecto.categoria" required style="width: 100%;">
                  <option value="Infraestructura">Infraestructura</option>
                  <option value="Campanya">Campanya</option>
                  <option value="I+D+I">I+D+I</option>
                  <option value="Divulgació científica">Divulgació científica</option>
                  <option value="Plan Nacional">Plan Nacional</option>
                  <option value="Contrato">Contrato</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>
              <div style="flex: 1;">
                <label>Estat:</label>
                <select v-model="nuevoProyecto.estado" required style="width: 100%;">
                  <option value="Sol·licitat">Sol·licitat</option>
                  <option value="Aprovat">Aprovat</option>
                  <option value="En Curs">En Curs</option>
                  <option value="Finalitzat">Finalitzat</option>
                </select>
              </div>
            </div>

            <div class="campo-form">
              <label>IP (Investigador Principal):</label>
              <input type="text" v-model="nuevoProyecto.investigador_principal" placeholder="Ex: Maria Garcia, Joan Puig" class="input-texto">
            </div>

            <div class="campo-form">
              <label>PIT (Personal Tècnic SIO):</label>
              <input type="text" v-model="nuevoProyecto.pit" placeholder="Ex: Raül Ferrando" class="input-texto">
            </div>

            <div style="margin-bottom: 15px;">
              <label>Descripció curta (Resum màx. 2 línies):</label>
              <textarea v-model="nuevoProyecto.descripcion_corta" rows="2" maxlength="150" placeholder="Escriu un breu resum aquí..." style="width: 100%; resize: none; border: 1px solid #ccc; border-radius: 4px; padding: 8px; font-family: inherit;"></textarea>
            </div>

            <div style="margin-bottom: 15px;">
              <label>Descripció ampliada (Amb imatges):</label>
              <div style="background: white; border: 1px solid #ddd;">
                <QuillEditor theme="snow" v-model:content="nuevoProyecto.descripcion_ampliada" contentType="html" :toolbar="opcionsEditor" />
              </div>
            </div>

            <button type="submit" class="btn-submit-main" style="margin-top: 10px; padding: 15px; cursor: pointer;">
              {{ editandoProyectoId ? '💾 Desar Canvis' : '🚀 Registrar Projecte' }}
            </button>
          </form>
        </div>

        <div v-else class="dashboard-view">
          
          <div class="acordeon-dash">
            <div class="acordeon-dash-header" @click="toggleDashboard('proyectos')">
              <div style="display: flex; align-items: center; gap: 15px;">
                <h3 style="margin: 0; color: #012169;">Campanyes i Projectes ({{ proyectos.length }})</h3>
              </div>
              <div style="display: flex; align-items: center; gap: 20px;">
                <button @click.stop="seccionActiva = 'proyecto'" class="btn-nou">+ Nou Projecte</button>
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
                    <small style="color: #666;">{{ proj.categoria }} | IP: {{ proj.investigador_principal || 'No assignat' }}</small>
                  </td>
                  <td><span class="badge-estado">{{ proj.estado }}</span></td>
                  <td style="text-align: right; width: 220px;">
                    <button @click="cargarParaEditarProyecto(proj)" class="btn-edit" style="margin-right: 5px;">✏️ Editar</button>
                    <button @click="eliminarProyecto(proj.id)" class="btn-delete">🗑️ Esborrar</button>
                  </td>
                </tr>
              </table>
            </div>
          </div>

          <div class="acordeon-dash">
            <div class="acordeon-dash-header" @click="toggleDashboard('instrumentos')">
              <div style="display: flex; align-items: center; gap: 15px;">
                <h3 style="margin: 0; color: #012169;">Inventari d'Instruments ({{ instrumentos.length }})</h3>
              </div>
              <div style="display: flex; align-items: center; gap: 20px;">
                <button @click.stop="seccionActiva = 'instrumentacion'" class="btn-nou">+ Nou Instrument</button>
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
                    <button @click="cargarParaEditar(inst)" class="btn-edit" style="margin-right: 5px;">✏️ Editar</button>
                    <button @click="eliminarInstrumento(inst.id)" class="btn-delete">🗑️ Esborrar</button>
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
.login-box button { width: 100%; padding: 10px; background: #8cc63f; color: #012169; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; }

.dashboard-grid { display: flex; min-height: 100vh; }
.sidebar { width: 250px; background: #012169; color: white; padding: 20px; display: flex; flex-direction: column; }
.sidebar-nav a { display: block; color: #ccc; padding: 10px; text-decoration: none; border-radius: 4px; margin-bottom: 5px; }
.sidebar-nav a.active { color: white; font-weight: bold; border-left: 3px solid #8cc63f; background: rgba(255, 255, 255, 0.05); }
.btn-logout { margin-top: auto; background: none; border: 1px solid white; color: white; padding: 10px; cursor: pointer; border-radius: 4px; }

.main-content { flex-grow: 1; padding: 40px; background: #f4f7f9; }
.grid-form { display: grid; gap: 10px; max-width: 800px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); }
.grid-form input, .grid-form select { padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
.badge-estado { background-color: #e1eef5; color: #0086c0; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: bold; }

.acordeon-dash { background: white; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05); overflow: hidden; }
.acordeon-dash-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background-color: #ffffff; border-bottom: 1px solid #eee; cursor: pointer; }
.btn-nou { background: #8cc63f; color: #012169; border: none; padding: 6px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
</style>