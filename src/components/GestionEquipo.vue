<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'

// Fichas de la página pública «Equipo SIO» (se guardan en el servidor: /api/equipo).
// Cualquiera del equipo puede añadir y editar; solo un administrador puede eliminar.
const props = defineProps({ sesion: { type: Object, required: true } })
const emit = defineEmits(['sesion-caducada'])
const { t, locale } = useI18n()
const caducada = () => emit('sesion-caducada')

const IDIOMAS = [['ca', 'Català'], ['es', 'Castellano'], ['en', 'English']]
const ETIQUETAS = ['liderazgo', 'ingenieria', 'soporte']
const FOTO_DEFECTO = '/fotos/equipo/perfil-default.svg'

const equip = ref([])
const cargando = ref(true)
const error = ref('')
const mensaje = ref('')

const vacia = () => ({
  id: null, nombre: '', email: '', etiqueta: 'soporte', orden: (equip.value.at(-1)?.orden || 0) + 1, visible: true, foto: '',
  cargo_ca: '', cargo_es: '', cargo_en: '', descripcion_ca: '', descripcion_es: '', descripcion_en: ''
})
const actual = ref(vacia())
const mostrarFormulari = ref(false)
const guardando = ref(false)
const errorForm = ref('')
const inputFoto = ref(null)

// Texto en el idioma de la intranet; si falta, en castellano
const enIdioma = (m, campo) => m[`${campo}_${locale.value}`] || m[`${campo}_es`] || m[`${campo}_ca`] || m[`${campo}_en`] || ''

const cargar = async () => {
  cargando.value = true
  error.value = ''
  try {
    const r = await peticionIntranet('/api/equipo?todas=1', {}, caducada)
    if (!r.ok) throw new Error()
    equip.value = await r.json()
  } catch {
    error.value = t('intranet.equipo.errorCarga')
  }
  cargando.value = false
}
onMounted(cargar)

const nouMembre = () => {
  actual.value = vacia()
  errorForm.value = ''
  mostrarFormulari.value = true
}

const editarMembre = (m) => {
  actual.value = { ...m }
  errorForm.value = ''
  mostrarFormulari.value = true
}

const avisar = (texto) => {
  mensaje.value = texto
  setTimeout(() => { if (mensaje.value === texto) mensaje.value = '' }, 4000)
}

const guardarMembre = async () => {
  guardando.value = true
  errorForm.value = ''
  const nueva = !actual.value.id
  const r = await peticionIntranet(nueva ? '/api/equipo' : `/api/equipo/${actual.value.id}`, {
    method: nueva ? 'POST' : 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(actual.value)
  }, caducada)
  const d = await r.json().catch(() => ({}))
  guardando.value = false
  if (!r.ok) {
    errorForm.value = traducirError(d.error) || t('intranet.equipo.errorGuardar')
    return
  }
  await cargar()
  avisar(t('intranet.equipo.guardado'))
  // Si era nueva, el formulario sigue abierto para poder ponerle la foto
  if (nueva) actual.value = { ...d }
  else mostrarFormulari.value = false
}

const subirFoto = async (evento) => {
  const fichero = evento.target.files[0]
  evento.target.value = ''
  if (!fichero || !actual.value.id) return
  errorForm.value = ''
  const datos = new FormData()
  datos.append('foto', fichero)
  guardando.value = true
  const r = await peticionIntranet(`/api/equipo/${actual.value.id}/foto`, { method: 'POST', body: datos }, caducada)
  const d = await r.json().catch(() => ({}))
  guardando.value = false
  if (!r.ok) {
    errorForm.value = r.status === 413 ? t('intranet.docs.demasiadoGrande') : (traducirError(d.error) || t('intranet.equipo.errorGuardar'))
    return
  }
  actual.value.foto = d.foto
  await cargar()
  avisar(t('intranet.equipo.fotoSubida'))
}

const eliminarMembre = async (m) => {
  if (!confirm(t('intranet.equipo.confirmarBorrar', { nombre: m.nombre }))) return
  const r = await peticionIntranet(`/api/equipo/${m.id}`, { method: 'DELETE' }, caducada)
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    error.value = traducirError(d.error) || t('intranet.equipo.errorGuardar')
    return
  }
  if (actual.value.id === m.id) mostrarFormulari.value = false
  await cargar()
  avisar(t('intranet.equipo.borrado'))
}

const fotoDe = (m) => m.foto || FOTO_DEFECTO
</script>

<template>
  <div class="panel-admin">
    <div class="cabecera-panel">
      <div>
        <h2>{{ $t('intranet.equipo.titulo') }}</h2>
        <p class="subtitulo-panel">
          {{ $t('intranet.equipo.subtitulo') }}
          <a href="/equipo" target="_blank" class="enlace-web">{{ $t('intranet.equipo.verWeb') }}</a>
        </p>
      </div>
      <button @click="nouMembre" class="btn-accio">{{ $t('intranet.equipo.anadir') }}</button>
    </div>

    <p v-if="mensaje" class="aviso-ok">{{ mensaje }}</p>
    <p v-if="error" class="aviso-error">{{ error }}</p>

    <div v-if="mostrarFormulari" class="caja-formulari">
      <h3>{{ $t(actual.id ? 'intranet.equipo.editar' : 'intranet.equipo.nuevo') }}</h3>
      <form @submit.prevent="guardarMembre" class="grid-form">

        <div class="fila-foto">
          <img :src="fotoDe(actual)" alt="" class="foto-form" @error="e => e.target.src = FOTO_DEFECTO">
          <div>
            <label class="etiqueta">{{ $t('intranet.equipo.foto') }}</label>
            <template v-if="actual.id">
              <button type="button" class="btn-foto" :disabled="guardando" @click="inputFoto.click()">{{ $t('intranet.equipo.cambiarFoto') }}</button>
              <input ref="inputFoto" type="file" accept="image/*" hidden @change="subirFoto">
              <p class="ayuda">{{ $t('intranet.equipo.fotoAyuda') }}</p>
            </template>
            <p v-else class="ayuda">{{ $t('intranet.equipo.fotoPrimero') }}</p>
          </div>
        </div>

        <div class="campo-doble">
          <div class="campo">
            <label>{{ $t('intranet.equipo.nombre') }}</label>
            <input v-model="actual.nombre" required maxlength="100">
          </div>
          <div class="campo">
            <label>{{ $t('intranet.equipo.correo') }}</label>
            <input v-model="actual.email" type="email" placeholder="usuario@icm.csic.es">
          </div>
        </div>

        <div class="campo-doble">
          <div class="campo">
            <label>{{ $t('intranet.equipo.grupo') }}</label>
            <select v-model="actual.etiqueta">
              <option v-for="e in ETIQUETAS" :key="e" :value="e">{{ $t(`equipo.etiquetas.${e}`) }}</option>
            </select>
          </div>
          <div class="campo campo-corto">
            <label>{{ $t('intranet.equipo.orden') }}</label>
            <input v-model.number="actual.orden" type="number" min="0" max="999">
          </div>
          <label class="campo-check">
            <input v-model="actual.visible" type="checkbox"> {{ $t('intranet.equipo.visible') }}
          </label>
        </div>

        <p class="etiqueta">{{ $t('intranet.equipo.idiomas') }}</p>
        <div class="grid-idiomas">
          <div v-for="[l, nombreIdioma] in IDIOMAS" :key="l" class="bloque-idioma">
            <span class="idioma">{{ nombreIdioma }}</span>
            <label>{{ $t('intranet.equipo.cargo') }}</label>
            <input v-model="actual[`cargo_${l}`]" maxlength="200" :lang="l">
            <label>{{ $t('intranet.equipo.bio') }}</label>
            <textarea v-model="actual[`descripcion_${l}`]" rows="5" maxlength="1500" :lang="l" :placeholder="$t('intranet.equipo.bioPh')"></textarea>
          </div>
        </div>

        <p v-if="errorForm" class="aviso-error">{{ errorForm }}</p>
        <div class="accions-form">
          <button type="submit" class="btn-guardar" :disabled="guardando">{{ $t('intranet.equipo.guardar') }}</button>
          <button type="button" @click="mostrarFormulari = false" class="btn-cancelar">{{ $t('intranet.equipo.cancelar') }}</button>
        </div>
      </form>
    </div>

    <p v-if="cargando" class="mensaje-vacio">…</p>
    <div v-else class="grid-equip">
      <div v-for="membre in equip" :key="membre.id" :class="['targeta-membre', { oculta: !membre.visible }]">
        <div class="info-membre">
          <div class="cabeza-membre">
            <img :src="fotoDe(membre)" alt="" class="foto-mini" @error="e => e.target.src = FOTO_DEFECTO">
            <div>
              <h4>{{ membre.nombre }}</h4>
              <span class="badge-carrec">{{ enIdioma(membre, 'cargo') }}</span>
            </div>
          </div>
          <p class="meta-membre">
            {{ $t(`equipo.etiquetas.${membre.etiqueta}`) }} · #{{ membre.orden }}
            <span v-if="!membre.visible" class="badge-oculta">{{ $t('intranet.equipo.oculta') }}</span>
          </p>
          <p v-if="membre.email" class="email-membre">✉️ {{ membre.email }}</p>
          <p class="bio-membre">{{ enIdioma(membre, 'descripcion') }}</p>
        </div>
        <div class="accions-membre">
          <button @click="editarMembre(membre)" class="btn-editar">{{ $t('intranet.comun.editar') }}</button>
          <button v-if="props.sesion.es_admin" @click="eliminarMembre(membre)" class="btn-eliminar" :aria-label="$t('intranet.docs.borrar')">🗑️</button>
        </div>
      </div>

      <div v-if="equip.length === 0 && !error" class="mensaje-vacio">
        {{ $t('intranet.equipo.vacio') }}
      </div>
    </div>
    <p v-if="!props.sesion.es_admin" class="ayuda">{{ $t('intranet.equipo.soloAdmin') }}</p>
  </div>
</template>

<style scoped>
.panel-admin { background: #ffffff; border-radius: 10px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-top: 20px; border-top: 4px solid #17a2b8; }
.cabecera-panel { display: flex; justify-content: space-between; align-items: center; gap: 15px; margin-bottom: 25px; border-bottom: 2px solid #eee; padding-bottom: 20px; }
.cabecera-panel h2 { color: #012169; margin: 0 0 5px 0; font-size: 1.6rem; }
.subtitulo-panel { color: #666; margin: 0; font-size: 0.95rem; }
.enlace-web { color: #0086c0; font-weight: bold; margin-left: 6px; white-space: nowrap; }
.btn-accio { background: #17a2b8; color: white; padding: 10px 20px; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; transition: background 0.2s; white-space: nowrap; }
.btn-accio:hover { background: #117a8b; }
.aviso-ok { color: #257a3c; background: #eaf7ed; border-radius: 4px; padding: 8px 12px; }
.aviso-error { color: #b00020; background: #ffeeee; border-radius: 4px; padding: 8px 12px; }
.ayuda { color: #777; font-size: 0.85rem; margin: 6px 0 0; }
.etiqueta { font-size: 0.85rem; font-weight: bold; color: #444; margin: 0; display: block; }

.caja-formulari { background: #f8fcfd; border: 1px solid #bce0fd; padding: 25px; border-radius: 8px; margin-bottom: 30px; }
.caja-formulari h3 { margin-top: 0; color: #0086c0; border-bottom: 1px dashed #ccc; padding-bottom: 10px; }
.grid-form { display: flex; flex-direction: column; gap: 15px; }
.fila-foto { display: flex; gap: 20px; align-items: center; }
.foto-form { width: 96px; height: 96px; border-radius: 50%; object-fit: cover; border: 3px solid #8cc63f; background: #e9ecef; flex-shrink: 0; }
.btn-foto { margin-top: 6px; background: white; border: 1px solid #0086c0; color: #0086c0; padding: 7px 14px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.campo-doble { display: flex; gap: 20px; align-items: flex-end; }
.campo { display: flex; flex-direction: column; flex: 1; gap: 5px; }
.campo-corto { flex: 0 0 130px; }
.campo label, .bloque-idioma label { font-size: 0.85rem; font-weight: bold; color: #444; }
.campo input, .campo select, .bloque-idioma input, .bloque-idioma textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; font-size: 0.95rem; }
.campo-check { display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: #444; padding-bottom: 10px; white-space: nowrap; }
.grid-idiomas { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
.bloque-idioma { display: flex; flex-direction: column; gap: 5px; background: white; border: 1px solid #e0e6ed; border-radius: 6px; padding: 12px; }
.idioma { font-weight: bold; color: #012169; font-size: 0.9rem; }
.accions-form { display: flex; gap: 10px; margin-top: 10px; }
.btn-guardar { background: #012169; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-guardar:disabled, .btn-foto:disabled { opacity: 0.6; cursor: wait; }
.btn-cancelar { background: #eee; color: #555; padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }

.grid-equip { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.targeta-membre { background: white; border: 1px solid #eee; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s; }
.targeta-membre:hover { border-color: #bce0fd; transform: translateY(-2px); }
.targeta-membre.oculta { opacity: 0.6; border-style: dashed; }
.cabeza-membre { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; }
.foto-mini { width: 56px; height: 56px; border-radius: 50%; object-fit: cover; border: 2px solid #8cc63f; background: #e9ecef; flex-shrink: 0; }
.info-membre h4 { margin: 0 0 5px 0; color: #012169; font-size: 1.15rem; }
.badge-carrec { display: inline-block; background: #e8f4fd; color: #0086c0; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
.meta-membre { font-size: 0.8rem; color: #888; margin: 0 0 8px; }
.badge-oculta { background: #fff4e5; color: #b45d00; border-radius: 4px; padding: 1px 6px; margin-left: 6px; }
.email-membre { margin: 0 0 10px 0; font-size: 0.9rem; color: #666; }
.bio-membre { font-size: 0.9rem; color: #555; line-height: 1.4; margin-bottom: 15px; flex-grow: 1; }
.accions-membre { display: flex; gap: 10px; border-top: 1px solid #eee; padding-top: 15px; margin-top: auto; }
.btn-editar { flex: 1; background: #f4f7f9; border: 1px solid #ccc; padding: 8px; border-radius: 4px; cursor: pointer; font-weight: bold; color: #012169; }
.btn-editar:hover { background: #e0e6ed; }
.btn-eliminar { background: #ffeeee; border: 1px solid #ffcccc; color: red; padding: 8px 12px; border-radius: 4px; cursor: pointer; }
.btn-eliminar:hover { background: #ffcccc; }

.mensaje-vacio { grid-column: 1 / -1; text-align: center; padding: 40px; color: #777; font-style: italic; background: #f9f9f9; border-radius: 8px; border: 1px dashed #ccc; }

@media (max-width: 768px) {
  .panel-admin { padding: 18px; }
  .cabecera-panel { flex-direction: column; align-items: stretch; }
  .campo-doble { flex-direction: column; align-items: stretch; gap: 15px; }
  .campo-corto { flex: 1; }
  .grid-idiomas { grid-template-columns: 1fr; }
  .grid-equip { grid-template-columns: 1fr; }
}
</style>
