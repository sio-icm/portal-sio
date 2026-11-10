<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'

// Usuarios personales de la intranet (solo administradores). Cada persona del
// equipo tiene el suyo, para saber quién escribe cada nota del diario.
const emit = defineEmits(['sesion-caducada'])
const { t } = useI18n()
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })

const usuarios = ref([])
const error = ref('')
const mensaje = ref('')
const nuevo = ref({ usuario: '', nombre: '', email: '', password: '', es_admin: false })

const cargar = async () => {
  const r = await api('/api/usuarios')
  if (r.ok) usuarios.value = await r.json()
  else error.value = t('intranet.usuarios.errorCarga')
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
  error.value = traducirError(d.error) || t('intranet.comun.errorDesconocido')
  return false
}

const crear = async () => {
  const r = await api('/api/usuarios', json('POST', nuevo.value))
  if (await avisar(r, t('intranet.usuarios.creado', { usuario: nuevo.value.usuario }))) {
    nuevo.value = { usuario: '', nombre: '', email: '', password: '', es_admin: false }
  }
}

const cambiar = async (u, cambios, textoOk) => avisar(await api(`/api/usuarios/${u.id}`, json('PUT', cambios)), textoOk)

// Edición en la propia fila (usuario y nombre)
const editando = ref(null) // { id, usuario, nombre, email }
const empezarEdicion = (u) => { editando.value = { id: u.id, usuario: u.usuario, nombre: u.nombre, email: u.email || '' } }
const guardarEdicion = async () => {
  const { id, usuario, nombre, email } = editando.value
  if (await cambiar({ id }, { usuario, nombre, email }, t('intranet.usuarios.actualizado', { usuario }))) editando.value = null
}

const borrar = async (u) => {
  if (!confirm(t('intranet.usuarios.confirmarBorrar', { usuario: u.usuario, nombre: u.nombre }))) return
  await avisar(await api(`/api/usuarios/${u.id}`, { method: 'DELETE' }), t('intranet.usuarios.borrado', { usuario: u.usuario }))
}

const nuevaContrasena = async (u) => {
  const p = prompt(t('intranet.usuarios.pedirContrasena', { nombre: u.nombre }))
  if (p) await cambiar(u, { password: p }, t('intranet.usuarios.contrasenaCambiada', { nombre: u.nombre }))
}
</script>

<template>
  <div class="panel-usuarios">
    <h2>{{ $t('intranet.usuarios.titulo') }}</h2>
    <p class="ayuda">{{ $t('intranet.usuarios.ayuda') }}</p>

    <form class="nuevo" @submit.prevent="crear">
      <h3>{{ $t('intranet.usuarios.nuevo') }}</h3>
      <div class="fila">
        <label>{{ $t('intranet.usuarios.usuario') }} <input v-model="nuevo.usuario" :placeholder="$t('intranet.usuarios.ejUsuario')" autocomplete="off" required></label>
        <label class="ancho">{{ $t('intranet.usuarios.nombre') }} <input v-model="nuevo.nombre" :placeholder="$t('intranet.usuarios.ejNombre')" required></label>
        <label class="ancho">{{ $t('intranet.usuarios.correo') }} <input v-model="nuevo.email" type="email" :placeholder="$t('intranet.cuenta.correoPh')"></label>
        <label>{{ $t('intranet.usuarios.inicial') }} <input v-model="nuevo.password" type="text" minlength="8" autocomplete="new-password" required></label>
        <label class="check"><input type="checkbox" v-model="nuevo.es_admin"> {{ $t('intranet.usuarios.admin') }}</label>
        <button type="submit" class="btn-principal">{{ $t('intranet.usuarios.crear') }}</button>
      </div>
    </form>

    <p v-if="mensaje" class="ok">{{ mensaje }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div class="tabla-scroll">
    <table class="tabla">
      <thead><tr><th>{{ $t('intranet.usuarios.usuario') }}</th><th>{{ $t('intranet.usuarios.nombreCorto') }}</th><th>{{ $t('intranet.usuarios.correo') }}</th><th>{{ $t('intranet.usuarios.admin') }}</th><th>{{ $t('intranet.usuarios.plantilla') }}</th><th>{{ $t('intranet.usuarios.estado') }}</th><th></th></tr></thead>
      <tbody>
        <tr v-if="usuarios.length === 0"><td colspan="7" class="aviso">{{ $t('intranet.usuarios.ninguno') }}</td></tr>
        <tr v-for="u in usuarios" :key="u.id" :class="{ inactivo: !u.activo }">
          <template v-if="editando && editando.id === u.id">
            <td><input v-model="editando.usuario" class="input-fila" :aria-label="$t('intranet.usuarios.usuario')"></td>
            <td><input v-model="editando.nombre" class="input-fila" :aria-label="$t('intranet.usuarios.nombre')"></td>
            <td><input v-model="editando.email" type="email" class="input-fila" :aria-label="$t('intranet.usuarios.correo')" :placeholder="$t('intranet.comun.ninguno')"></td>
          </template>
          <template v-else>
            <td>{{ u.usuario }}</td>
            <td>{{ u.nombre }}</td>
            <td class="correo">{{ u.email || '—' }}</td>
          </template>
          <td>
            <label class="check"><input type="checkbox" :checked="!!u.es_admin"
              @change="cambiar(u, { es_admin: $event.target.checked }, $t('intranet.usuarios.permisos', { nombre: u.nombre }))"></label>
          </td>
          <td>
            <label class="check"><input type="checkbox" :checked="!!u.plantilla" :aria-label="$t('intranet.usuarios.plantillaAria', { nombre: u.nombre })"
              @change="cambiar(u, { plantilla: $event.target.checked }, $event.target.checked ? $t('intranet.usuarios.enPlantilla', { nombre: u.nombre }) : $t('intranet.usuarios.fueraPlantilla', { nombre: u.nombre }))"></label>
          </td>
          <td>
            {{ $t(u.activo ? 'intranet.usuarios.activo' : 'intranet.usuarios.desactivado') }}
            <span v-if="u.activo && u.debe_cambiar" class="pendiente" :title="$t('intranet.usuarios.pendienteTitulo')">{{ $t('intranet.usuarios.pendiente') }}</span>
          </td>
          <td v-if="editando && editando.id === u.id" class="acciones">
            <button class="btn-mini guardar" @click="guardarEdicion">{{ $t('intranet.comun.guardar') }}</button>
            <button class="btn-mini" @click="editando = null">{{ $t('intranet.comun.cancelar') }}</button>
          </td>
          <td v-else class="acciones">
            <button class="btn-mini" @click="empezarEdicion(u)">{{ $t('intranet.comun.editar') }}</button>
            <button class="btn-mini" @click="nuevaContrasena(u)">{{ $t('intranet.usuarios.contrasena') }}</button>
            <button class="btn-mini" @click="cambiar(u, { activo: !u.activo }, u.activo ? $t('intranet.usuarios.desactivadoMsg', { nombre: u.nombre }) : $t('intranet.usuarios.activadoMsg', { nombre: u.nombre }))">
              {{ $t(u.activo ? 'intranet.usuarios.desactivar' : 'intranet.usuarios.activar') }}
            </button>
            <button class="btn-mini peligro" @click="borrar(u)">{{ $t('intranet.comun.borrar') }}</button>
          </td>
        </tr>
      </tbody>
    </table>
    </div>
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
.tabla-scroll { overflow-x: auto; }  /* si la taula no hi cap, es desplaça dins la caixa (no aixafa el menú) */
.tabla { width: 100%; border-collapse: collapse; margin-top: 10px; }
@media (max-width: 768px) {
  .panel-usuarios { padding: 14px; }
}
.tabla th, .tabla td { border-bottom: 1px solid #e3e8ee; padding: 8px; text-align: left; font-size: 0.9rem; }
.tabla th { color: #555; }
.inactivo td { color: #999; }
.pendiente { color: #c26a00; font-size: 0.8rem; }
.correo { color: #555; font-size: 0.85rem; word-break: break-all; }
.acciones { display: flex; gap: 6px; flex-wrap: wrap; }
.input-fila { width: 100%; box-sizing: border-box; padding: 5px 8px; }
.btn-mini.guardar { background: #e6f4ea; color: #1e6b34; border-color: #a8d5b5; }
.btn-mini.peligro { color: #b02a37; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.8rem; }
</style>
