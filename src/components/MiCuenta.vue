<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'

// Cada usuario cambia aquí su propia contraseña. El administrador definido en
// el servidor (backend.env) no tiene usuario en la base de datos: la suya se
// cambia en el servidor (ver README).
const props = defineProps({
  sesion: { type: Object, required: true },
  // true = primer acceso: hay que cambiar la contraseña antes de usar la intranet
  obligatorio: { type: Boolean, default: false }
})
const emit = defineEmits(['sesion-caducada', 'cambiada'])
const { t } = useI18n()

const actual = ref('')
const nueva = ref('')
const repetida = ref('')
const mensaje = ref('')
const error = ref('')

// Correu per a «He oblidat la contrasenya»
const email = ref('')
const mensajeEmail = ref('')
const errorEmail = ref('')
onMounted(async () => {
  if (props.obligatorio || props.sesion.usuario_id === null) return
  const r = await peticionIntranet('/api/mi-cuenta', {}, () => emit('sesion-caducada'))
  if (r.ok) email.value = (await r.json()).email || ''
})
const guardarEmail = async () => {
  mensajeEmail.value = ''
  errorEmail.value = ''
  const r = await peticionIntranet('/api/mi-cuenta', {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: email.value })
  }, () => emit('sesion-caducada'))
  const d = await r.json().catch(() => ({}))
  if (r.ok) { email.value = d.email || ''; mensajeEmail.value = email.value ? t('intranet.cuenta.correoGuardado') : t('intranet.cuenta.correoBorrado') }
  else errorEmail.value = traducirError(d.error) || t('intranet.cuenta.correoNoGuardado')
}

const cambiar = async () => {
  mensaje.value = ''
  error.value = ''
  if (nueva.value !== repetida.value) {
    error.value = t('intranet.cuenta.noCoinciden')
    return
  }
  const r = await peticionIntranet('/api/mi-contrasena', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ actual: actual.value, nueva: nueva.value })
  }, () => emit('sesion-caducada'))
  if (r.ok) {
    mensaje.value = t('intranet.cuenta.cambiada')
    actual.value = nueva.value = repetida.value = ''
    emit('cambiada')
  } else {
    const d = await r.json().catch(() => ({}))
    error.value = traducirError(d.error) || t('intranet.panel.noCambiada')
  }
}
</script>

<template>
  <div class="panel-cuenta">
    <template v-if="props.obligatorio">
      <h2>{{ $t('intranet.cuenta.cambiaTitulo') }}</h2>
      <p class="aviso-obligatorio">{{ $t('intranet.cuenta.obligatorio', { nombre: props.sesion.nombre }) }}</p>
    </template>
    <h2 v-else>{{ $t('intranet.cuenta.titulo') }}</h2>
    <p v-if="!props.obligatorio" class="nombre">{{ props.sesion.nombre }} <span v-if="props.sesion.es_admin" class="etiqueta">{{ $t('intranet.cuenta.administrador') }}</span></p>

    <p v-if="props.sesion.usuario_id === null" class="ayuda">
      {{ $t('intranet.cuenta.adminServidor') }}
    </p>

    <form v-else class="formulario" @submit.prevent="cambiar">
      <h3 v-if="!props.obligatorio">{{ $t('intranet.cuenta.cambiarTitulo') }}</h3>
      <label>{{ $t(props.obligatorio ? 'intranet.cuenta.inicial' : 'intranet.cuenta.actual') }} <input type="password" v-model="actual" autocomplete="current-password" required></label>
      <label>{{ $t('intranet.cuenta.nueva') }} <input type="password" v-model="nueva" minlength="8" autocomplete="new-password" required></label>
      <label>{{ $t('intranet.cuenta.repite') }} <input type="password" v-model="repetida" minlength="8" autocomplete="new-password" required></label>
      <button type="submit" class="btn-principal">{{ $t('intranet.cuenta.cambiar') }}</button>
      <p v-if="mensaje" class="ok">{{ mensaje }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>

    <form v-if="!props.obligatorio && props.sesion.usuario_id !== null" class="formulario" @submit.prevent="guardarEmail">
      <h3>{{ $t('intranet.cuenta.correoTitulo') }}</h3>
      <p class="ayuda">{{ $t('intranet.cuenta.correoAyuda') }}</p>
      <label>{{ $t('intranet.cuenta.correo') }} <input type="email" v-model="email" autocomplete="email" :placeholder="$t('intranet.cuenta.correoPh')"></label>
      <button type="submit" class="btn-principal">{{ $t('intranet.cuenta.guardarCorreo') }}</button>
      <p v-if="mensajeEmail" class="ok">{{ mensajeEmail }}</p>
      <p v-if="errorEmail" class="error">{{ errorEmail }}</p>
    </form>
  </div>
</template>

<style scoped>
.panel-cuenta { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #0086c0; max-width: 520px; }
h2 { margin: 0; color: #012169; }
.nombre { font-weight: bold; color: #333; }
.etiqueta { background: #012169; color: white; border-radius: 10px; padding: 2px 8px; font-size: 0.75rem; margin-left: 6px; }
.ayuda { color: #666; font-size: 0.9rem; }
.aviso-obligatorio { color: #444; font-size: 0.95rem; line-height: 1.5; }
.formulario { display: flex; flex-direction: column; gap: 10px; }
.formulario h3 { margin: 10px 0 0; color: #012169; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; font-weight: bold; color: #444; }
input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font: inherit; font-weight: normal; }
.btn-principal { align-self: flex-start; background: #012169; color: white; border: none; padding: 9px 18px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.ok { color: #198754; font-weight: bold; }
.error { color: #b02a37; font-weight: bold; }
</style>
