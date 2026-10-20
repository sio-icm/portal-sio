<script setup>
import { ref } from 'vue'
import { peticionIntranet } from '../utils/diario'

// Cada usuario cambia aquí su propia contraseña. El administrador definido en
// el servidor (backend.env) no tiene usuario en la base de datos: la suya se
// cambia en el servidor (ver README).
const props = defineProps({ sesion: { type: Object, required: true } })
const emit = defineEmits(['sesion-caducada'])

const actual = ref('')
const nueva = ref('')
const repetida = ref('')
const mensaje = ref('')
const error = ref('')

const cambiar = async () => {
  mensaje.value = ''
  error.value = ''
  if (nueva.value !== repetida.value) {
    error.value = 'Les dues contrasenyes noves no coincideixen.'
    return
  }
  const r = await peticionIntranet('/api/mi-contrasena', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ actual: actual.value, nueva: nueva.value })
  }, () => emit('sesion-caducada'))
  if (r.ok) {
    mensaje.value = 'Contrasenya canviada.'
    actual.value = nueva.value = repetida.value = ''
  } else {
    const d = await r.json().catch(() => ({}))
    error.value = d.error || "No s'ha pogut canviar la contrasenya."
  }
}
</script>

<template>
  <div class="panel-cuenta">
    <h2>👤 El meu compte</h2>
    <p class="nombre">{{ props.sesion.nombre }} <span v-if="props.sesion.es_admin" class="etiqueta">Administrador</span></p>

    <p v-if="props.sesion.usuario_id === null" class="ayuda">
      Has entrat amb l'usuari administrador del servidor. La seva contrasenya es canvia al servidor (vegeu el README).
      Per escriure al diari amb el teu nom, crea't un usuari personal a «Usuaris».
    </p>

    <form v-else class="formulario" @submit.prevent="cambiar">
      <h3>Canviar la contrasenya</h3>
      <label>Contrasenya actual <input type="password" v-model="actual" autocomplete="current-password" required></label>
      <label>Contrasenya nova (mínim 8 caràcters) <input type="password" v-model="nueva" minlength="8" autocomplete="new-password" required></label>
      <label>Repeteix la nova <input type="password" v-model="repetida" minlength="8" autocomplete="new-password" required></label>
      <button type="submit" class="btn-principal">Canviar</button>
      <p v-if="mensaje" class="ok">{{ mensaje }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<style scoped>
.panel-cuenta { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #0086c0; max-width: 520px; }
h2 { margin: 0; color: #012169; }
.nombre { font-weight: bold; color: #333; }
.etiqueta { background: #012169; color: white; border-radius: 10px; padding: 2px 8px; font-size: 0.75rem; margin-left: 6px; }
.ayuda { color: #666; font-size: 0.9rem; }
.formulario { display: flex; flex-direction: column; gap: 10px; }
.formulario h3 { margin: 10px 0 0; color: #012169; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; font-weight: bold; color: #444; }
input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font: inherit; font-weight: normal; }
.btn-principal { align-self: flex-start; background: #012169; color: white; border: none; padding: 9px 18px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.ok { color: #198754; font-weight: bold; }
.error { color: #b02a37; font-weight: bold; }
</style>
