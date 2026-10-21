<script setup>
import { ref, onMounted } from 'vue'
import { peticionIntranet } from '../utils/diario'

// Usuarios personales de la intranet (solo administradores). Cada persona del
// equipo tiene el suyo, para saber quién escribe cada nota del diario.
const emit = defineEmits(['sesion-caducada'])
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })

const usuarios = ref([])
const error = ref('')
const mensaje = ref('')
const nuevo = ref({ usuario: '', nombre: '', password: '', es_admin: false })

const cargar = async () => {
  const r = await api('/api/usuarios')
  if (r.ok) usuarios.value = await r.json()
  else error.value = "No s'han pogut carregar els usuaris."
}
onMounted(cargar)

const avisar = async (respuesta, textoOk) => {
  if (respuesta.ok) {
    error.value = ''
    mensaje.value = textoOk
    await cargar()
    return true
  }
  const d = await respuesta.json().catch(() => ({}))
  mensaje.value = ''
  error.value = d.error || 'Error desconegut.'
  return false
}

const crear = async () => {
  const r = await api('/api/usuarios', json('POST', nuevo.value))
  if (await avisar(r, `Usuari «${nuevo.value.usuario}» creat. Passa-li la contrasenya inicial: la primera vegada que entri haurà de canviar-la.`)) {
    nuevo.value = { usuario: '', nombre: '', password: '', es_admin: false }
  }
}

const cambiar = async (u, cambios, textoOk) => avisar(await api(`/api/usuarios/${u.id}`, json('PUT', cambios)), textoOk)

// Edición en la propia fila (usuario y nombre)
const editando = ref(null) // { id, usuario, nombre }
const empezarEdicion = (u) => { editando.value = { id: u.id, usuario: u.usuario, nombre: u.nombre } }
const guardarEdicion = async () => {
  const { id, usuario, nombre } = editando.value
  if (await cambiar({ id }, { usuario, nombre }, `Usuari «${usuario}» actualitzat.`)) editando.value = null
}

const borrar = async (u) => {
  if (!confirm(`Segur que vols esborrar l'usuari «${u.usuario}» (${u.nombre})?`)) return
  await avisar(await api(`/api/usuarios/${u.id}`, { method: 'DELETE' }), `Usuari «${u.usuario}» esborrat.`)
}

const nuevaContrasena = async (u) => {
  const p = prompt(`Nova contrasenya per a ${u.nombre} (mínim 8 caràcters):`)
  if (p) await cambiar(u, { password: p }, `Contrasenya de ${u.nombre} canviada.`)
}
</script>

<template>
  <div class="panel-usuarios">
    <h2>👥 Usuaris de la intranet</h2>
    <p class="ayuda">Cada persona de l'equip té el seu usuari: així el diari sap qui escriu cada nota. Els administradors poden gestionar usuaris i editar qualsevol nota.
      Un usuari només es pot esborrar si no ha escrit cap nota; si en té, desactiva'l.</p>

    <form class="nuevo" @submit.prevent="crear">
      <h3>Nou usuari</h3>
      <div class="fila">
        <label>Usuari <input v-model="nuevo.usuario" placeholder="ex.: nhoareau" autocomplete="off" required></label>
        <label class="ancho">Nom complet <input v-model="nuevo.nombre" placeholder="ex.: Nina Hoareau" required></label>
        <label>Contrasenya inicial <input v-model="nuevo.password" type="text" minlength="8" autocomplete="new-password" required></label>
        <label class="check"><input type="checkbox" v-model="nuevo.es_admin"> Administrador</label>
        <button type="submit" class="btn-principal">Crear</button>
      </div>
    </form>

    <p v-if="mensaje" class="ok">{{ mensaje }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table class="tabla">
      <thead><tr><th>Usuari</th><th>Nom</th><th>Administrador</th><th>Estat</th><th></th></tr></thead>
      <tbody>
        <tr v-if="usuarios.length === 0"><td colspan="5" class="aviso">Encara no hi ha usuaris personals.</td></tr>
        <tr v-for="u in usuarios" :key="u.id" :class="{ inactivo: !u.activo }">
          <template v-if="editando && editando.id === u.id">
            <td><input v-model="editando.usuario" class="input-fila" aria-label="Usuari"></td>
            <td><input v-model="editando.nombre" class="input-fila" aria-label="Nom complet"></td>
          </template>
          <template v-else>
            <td>{{ u.usuario }}</td>
            <td>{{ u.nombre }}</td>
          </template>
          <td>
            <label class="check"><input type="checkbox" :checked="!!u.es_admin"
              @change="cambiar(u, { es_admin: $event.target.checked }, `Permisos de ${u.nombre} actualitzats.`)"></label>
          </td>
          <td>
            {{ u.activo ? 'Actiu' : 'Desactivat' }}
            <span v-if="u.activo && u.debe_cambiar" class="pendiente" title="Ha de canviar la contrasenya en entrar">· pendent de canviar la contrasenya</span>
          </td>
          <td v-if="editando && editando.id === u.id" class="acciones">
            <button class="btn-mini guardar" @click="guardarEdicion">💾 Desar</button>
            <button class="btn-mini" @click="editando = null">Cancel·lar</button>
          </td>
          <td v-else class="acciones">
            <button class="btn-mini" @click="empezarEdicion(u)">✏️ Editar</button>
            <button class="btn-mini" @click="nuevaContrasena(u)">🔑 Contrasenya</button>
            <button class="btn-mini" @click="cambiar(u, { activo: !u.activo }, u.activo ? `${u.nombre} desactivat.` : `${u.nombre} activat.`)">
              {{ u.activo ? '⛔ Desactivar' : '✅ Activar' }}
            </button>
            <button class="btn-mini peligro" @click="borrar(u)">🗑️ Esborrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.panel-usuarios { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #012169; }
h2 { margin: 0; color: #012169; }
.ayuda { color: #666; font-size: 0.9rem; margin: 8px 0 20px; }
.nuevo { background: #f4f7f9; border-radius: 8px; padding: 15px 20px; margin-bottom: 15px; }
.nuevo h3 { margin: 0 0 10px; color: #012169; }
.fila { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; font-weight: bold; color: #444; }
label.check { flex-direction: row; align-items: center; gap: 6px; }
.ancho { flex: 1; min-width: 200px; }
input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font: inherit; font-weight: normal; }
.btn-principal { background: #012169; color: white; border: none; padding: 9px 18px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.ok { color: #198754; font-weight: bold; }
.error { color: #b02a37; font-weight: bold; }
.aviso { color: #666; font-style: italic; text-align: center; }
.tabla { width: 100%; border-collapse: collapse; margin-top: 10px; }
@media (max-width: 768px) {
  .panel-usuarios { padding: 14px; }
  .tabla { display: block; overflow-x: auto; }
}
.tabla th, .tabla td { border-bottom: 1px solid #e3e8ee; padding: 8px; text-align: left; font-size: 0.9rem; }
.tabla th { color: #555; }
.inactivo td { color: #999; }
.pendiente { color: #c26a00; font-size: 0.8rem; }
.acciones { display: flex; gap: 6px; flex-wrap: wrap; }
.input-fila { width: 100%; box-sizing: border-box; padding: 5px 8px; }
.btn-mini.guardar { background: #e6f4ea; color: #1e6b34; border-color: #a8d5b5; }
.btn-mini.peligro { color: #b02a37; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.8rem; }
</style>
