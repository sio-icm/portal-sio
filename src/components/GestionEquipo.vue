<script setup>
import { ref } from 'vue'

// --- DATOS DEL EQUIPO REALES EXTRAÍDOS DEL PANTALLAZO ---
const equip = ref([
  { 
    id: 1, 
    nom: 'Raül Bardají', 
    carrec: 'Responsable Técnico del SIO', 
    email: 'rbardaji@icm.csic.es', // Puedes actualizar el email real luego
    bio: 'Coordinación general de infraestructuras, gestión de campañas oceanográficas y dirección del soporte tecnológico en el ICM-CSIC.', 
    foto: '/perfil-default.jpg' 
  },
  { 
    id: 2, 
    nom: 'Raül Ferrando', 
    carrec: 'Personal Técnico de Investigación (PIT)', 
    email: 'rferrando@icm.csic.es', 
    bio: 'Diseño industrial, desarrollo de sistemas embebidos, prototipado rápido (Mecanizado/Impresión 3D) y mantenimiento de la flota autónoma.', 
    foto: '/perfil-default.jpg' 
  },
  { 
    id: 3, 
    nom: 'Nina Hoareau', 
    carrec: 'Especialista en Instrumentación', 
    email: 'nhoareau@icm.csic.es', 
    bio: 'Calibración de sensores oceanográficos, análisis físico-químico de muestras de agua (Salinidad) y asistencia técnica en campañas.', 
    foto: '/perfil-default.jpg' 
  },
  { 
    id: 4, 
    nom: 'Bryan Nicolás', 
    carrec: 'Técnico en Electrónica y Sistemas', 
    email: 'bnicolas@icm.csic.es', 
    bio: 'Mantenimiento preventivo y correctivo de sistemas de telemetría, comunicaciones submarinas y electrónica analógica/digital.', 
    foto: '/perfil-default.jpg' 
  },
  { 
    id: 5, 
    nom: 'Kintxo Salvador', 
    carrec: 'Técnico de Soporte', 
    email: 'ksalvador@icm.csic.es', 
    bio: 'Escribe aquí la descripción de las tareas, especialidades y soporte que ofrece Kintxo dentro del Servicio de Ingeniería.', 
    foto: '/perfil-default.jpg' 
  },
  { 
    id: 6, 
    nom: 'Maribel Lloret', 
    carrec: 'Técnica de Soporte', 
    email: 'mlloret@icm.csic.es', 
    bio: 'Escribe aquí la descripción de las tareas, especialidades y soporte que ofrece Maribel dentro del Servicio de Ingeniería.', 
    foto: '/perfil-default.jpg' 
  }
])

// --- LÓGICA DE GESTIÓN ---
const mostrarFormulari = ref(false)
const modeEdicio = ref(false)

const membreActual = ref({
  id: null,
  nom: '',
  carrec: '',
  email: '',
  bio: '',
  foto: '/perfil-default.jpg'
})

const nouMembre = () => {
  membreActual.value = { id: null, nom: '', carrec: '', email: '', bio: '', foto: '/perfil-default.jpg' }
  modeEdicio.value = false
  mostrarFormulari.value = true
}

const editarMembre = (membre) => {
  membreActual.value = { ...membre }
  modeEdicio.value = true
  mostrarFormulari.value = true
}

const guardarMembre = () => {
  if (modeEdicio.value) {
    const index = equip.value.findIndex(m => m.id === membreActual.value.id)
    if (index !== -1) equip.value[index] = { ...membreActual.value }
  } else {
    membreActual.value.id = Date.now()
    equip.value.push({ ...membreActual.value })
  }
  mostrarFormulari.value = false
}

const eliminarMembre = (id) => {
  if (confirm("¿Seguro que quieres eliminar a este integrante del equipo?")) {
    equip.value = equip.value.filter(m => m.id !== id)
  }
}
</script>

<template>
  <div class="panel-admin">
    <div class="cabecera-panel">
      <div>
        <h2>👥 Gestión del Equipo SIO</h2>
        <p class="subtitulo-panel">Añade, edita o elimina los perfiles del personal del servicio.</p>
      </div>
      <button @click="nouMembre" class="btn-accio">+ Añadir Integrante</button>
    </div>

    <div v-if="mostrarFormulari" class="caja-formulari">
      <h3>{{ modeEdicio ? '✏️ Editar Integrante' : '➕ Nuevo Integrante' }}</h3>
      <form @submit.prevent="guardarMembre" class="grid-form">
        
        <div class="campo-doble">
          <div class="campo">
            <label>Nombre y Apellidos:</label>
            <input v-model="membreActual.nom" required placeholder="Ej: Dra. Cristina Romera Castillo">
          </div>
          <div class="campo">
            <label>Cargo / Rol:</label>
            <input v-model="membreActual.carrec" required placeholder="Ej: Personal de Investigación Técnica (PIT)">
          </div>
        </div>

        <div class="campo-doble">
          <div class="campo">
            <label>Correo Electrónico (ICM):</label>
            <input v-model="membreActual.email" type="email" required placeholder="usuario@icm.csic.es">
          </div>
          <div class="campo">
            <label>Nombre de la foto (Ruta):</label>
            <input v-model="membreActual.foto" placeholder="Ej: /fotos/cristina.jpg">
          </div>
        </div>

        <div class="campo">
          <label>Biografía Corta / Responsabilidades:</label>
          <textarea v-model="membreActual.bio" rows="4" required placeholder="Explica brevemente las tareas, especialidades y formación..."></textarea>
        </div>

        <div class="accions-form">
          <button type="submit" class="btn-guardar">💾 Guardar Perfil</button>
          <button type="button" @click="mostrarFormulari = false" class="btn-cancelar">❌ Cancelar</button>
        </div>
      </form>
    </div>

    <div class="grid-equip">
      <div v-for="membre in equip" :key="membre.id" class="targeta-membre">
        <div class="info-membre">
          <h4>{{ membre.nom }}</h4>
          <span class="badge-carrec">{{ membre.carrec }}</span>
          <p class="email-membre">✉️ {{ membre.email }}</p>
          <p class="bio-membre">{{ membre.bio }}</p>
        </div>
        <div class="accions-membre">
          <button @click="editarMembre(membre)" class="btn-editar">✏️ Editar</button>
          <button @click="eliminarMembre(membre.id)" class="btn-eliminar">🗑️</button>
        </div>
      </div>
      
      <div v-if="equip.length === 0" class="mensaje-vacio">
        No hay ningún integrante configurado todavía. Haz clic en "+ Añadir Integrante" para empezar.
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ESTILOS */
.panel-admin { background: #ffffff; border-radius: 10px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-top: 20px; border-top: 4px solid #17a2b8; }
.cabecera-panel { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 2px solid #eee; padding-bottom: 20px; }
.cabecera-panel h2 { color: #012169; margin: 0 0 5px 0; font-size: 1.6rem; }
.subtitulo-panel { color: #666; margin: 0; font-size: 0.95rem; }
.btn-accio { background: #17a2b8; color: white; padding: 10px 20px; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; transition: background 0.2s; }
.btn-accio:hover { background: #117a8b; }

.caja-formulari { background: #f8fcfd; border: 1px solid #bce0fd; padding: 25px; border-radius: 8px; margin-bottom: 30px; }
.caja-formulari h3 { margin-top: 0; color: #0086c0; border-bottom: 1px dashed #ccc; padding-bottom: 10px; }
.grid-form { display: flex; flex-direction: column; gap: 15px; }
.campo-doble { display: flex; gap: 20px; }
.campo { display: flex; flex-direction: column; flex: 1; gap: 5px; }
.campo label { font-size: 0.85rem; font-weight: bold; color: #444; }
.campo input, .campo textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; }
.accions-form { display: flex; gap: 10px; margin-top: 10px; }
.btn-guardar { background: #012169; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-cancelar { background: #eee; color: #555; padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }

.grid-equip { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.targeta-membre { background: white; border: 1px solid #eee; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s; }
.targeta-membre:hover { border-color: #bce0fd; transform: translateY(-2px); }
.info-membre h4 { margin: 0 0 5px 0; color: #012169; font-size: 1.2rem; }
.badge-carrec { display: inline-block; background: #e8f4fd; color: #0086c0; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; margin-bottom: 10px; }
.email-membre { margin: 0 0 10px 0; font-size: 0.9rem; color: #666; }
.bio-membre { font-size: 0.9rem; color: #555; line-height: 1.4; margin-bottom: 15px; flex-grow: 1; }
.accions-membre { display: flex; gap: 10px; border-top: 1px solid #eee; padding-top: 15px; margin-top: auto; }
.btn-editar { flex: 1; background: #f4f7f9; border: 1px solid #ccc; padding: 8px; border-radius: 4px; cursor: pointer; font-weight: bold; color: #012169; }
.btn-editar:hover { background: #e0e6ed; }
.btn-eliminar { background: #ffeeee; border: 1px solid #ffcccc; color: red; padding: 8px 12px; border-radius: 4px; cursor: pointer; }
.btn-eliminar:hover { background: #ffcccc; }

.mensaje-vacio { grid-column: 1 / -1; text-align: center; padding: 40px; color: #777; font-style: italic; background: #f9f9f9; border-radius: 8px; border: 1px dashed #ccc; }
</style>