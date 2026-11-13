<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'

// Compres sense projecte: llista compartida del que cal comprar (sobretot a RS).
// Quan els articles de RS pendents arriben al mínim (95 € sense IVA, així no paguem
// els ports), s'activa el botó per enviar a RS la petició de pressupost per correu.
defineProps({ sesion: { type: Object, required: true } })
const emit = defineEmits(['sesion-caducada'])
const { t, locale } = useI18n()
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })

const PROVEEDOR_RS = 'RS Components'
const datos = ref(null)
const error = ref('')
const mensaje = ref('')
const guardando = ref(false)
const enviando = ref(false)
const vacio = () => ({ descripcion: '', cantidad: 1, precio: '', proveedor: PROVEEDOR_RS, referencia: '' })
const nuevo = ref(vacio())
const editando = ref(null) // còpia de la fila que s'està editant

const euros = (n) => new Intl.NumberFormat(locale.value, { style: 'currency', currency: 'EUR' }).format(n || 0)
const fecha = (iso) => iso ? new Intl.DateTimeFormat(locale.value, { day: '2-digit', month: '2-digit', year: '2-digit' }).format(new Date(iso.slice(0, 10) + 'T12:00:00')) : ''
const importe = (f) => f.precio == null ? null : f.precio * f.cantidad

const rs = computed(() => (datos.value?.pendientes || []).filter(f => f.es_rs))
const otros = computed(() => (datos.value?.pendientes || []).filter(f => !f.es_rs))
const total = computed(() => datos.value?.total_rs || 0)
const minimo = computed(() => datos.value?.minimo || 95)
const falta = computed(() => Math.max(0, minimo.value - total.value))
const porcentaje = computed(() => Math.min(100, Math.round(100 * total.value / minimo.value)))
const puedeEnviar = computed(() => rs.value.length > 0 && total.value >= minimo.value && datos.value?.correo_configurado)

const respuesta = async (r, textoOk) => {
  if (r.ok) {
    datos.value = await r.json()
    error.value = ''
    mensaje.value = textoOk || ''
    return true
  }
  const d = await r.json().catch(() => ({}))
  mensaje.value = ''
  error.value = traducirError(d.error) || t('intranet.comun.errorDesconocido')
  return false
}

const cargar = async () => {
  const r = await api('/api/compras')
  if (r.ok) datos.value = await r.json()
  else error.value = t('intranet.compras.errorCarga')
}
onMounted(cargar)

const anadir = async () => {
  guardando.value = true
  try {
    if (await respuesta(await api('/api/compras', json('POST', nuevo.value)), t('intranet.compras.anadido'))) nuevo.value = vacio()
  } finally {
    guardando.value = false
  }
}
const empezarEdicion = (f) => { editando.value = { ...f, precio: f.precio ?? '' } }
const guardarEdicion = async () => {
  if (await respuesta(await api(`/api/compras/${editando.value.id}`, json('PUT', editando.value)), t('intranet.compras.guardado'))) editando.value = null
}
const borrar = async (f) => {
  if (!confirm(t('intranet.compras.confirmarBorrar', { descripcion: f.descripcion }))) return
  await respuesta(await api(`/api/compras/${f.id}`, { method: 'DELETE' }), t('intranet.comun.borrado'))
}
const enviar = async () => {
  const pregunta = t('intranet.compras.confirmarEnviar', { n: rs.value.length, total: euros(total.value), destino: datos.value.destino })
  if (!confirm(pregunta)) return
  enviando.value = true
  try {
    await respuesta(await api('/api/compras/enviar', { method: 'POST' }), t('intranet.compras.enviado', { destino: datos.value.destino }))
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <div class="panel-compras">
    <h2>{{ $t('intranet.compras.titulo') }}</h2>
    <p class="ayuda">{{ $t('intranet.compras.ayuda', { minimo: euros(minimo), portes: euros(datos?.portes || 16) }) }}</p>

    <p v-if="mensaje" class="ok" role="status">{{ mensaje }}</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <template v-if="datos">
      <!-- Comptador fins al mínim -->
      <section class="caja progreso" :class="{ completo: total >= minimo }">
        <div class="progreso-cifras">
          <strong>{{ euros(total) }}</strong> <span>/ {{ euros(minimo) }} {{ $t('intranet.compras.sinIva') }}</span>
        </div>
        <div class="barra" role="progressbar" :aria-valuenow="porcentaje" aria-valuemin="0" aria-valuemax="100"><i :style="{ width: porcentaje + '%' }"></i></div>
        <p v-if="total >= minimo" class="estado-ok">✅ {{ $t('intranet.compras.alcanzado') }}</p>
        <p v-else class="estado">{{ $t('intranet.compras.falta', { falta: euros(falta) }) }}</p>
        <p v-if="datos.sin_precio_rs" class="aviso">⚠️ {{ $t('intranet.compras.sinPrecio', { n: datos.sin_precio_rs }) }}</p>
        <button type="button" class="btn-enviar" :disabled="!puedeEnviar || enviando" @click="enviar">
          📧 {{ $t('intranet.compras.enviar', { destino: datos.destino }) }}
        </button>
        <p v-if="!datos.correo_configurado" class="aviso">{{ $t('intranet.compras.sinCorreo') }}</p>
      </section>

      <!-- Afegir -->
      <form class="caja nuevo" @submit.prevent="anadir">
        <h3>{{ $t('intranet.compras.nuevo') }}</h3>
        <div class="fila">
          <label class="ancho">{{ $t('intranet.compras.descripcion') }}
            <input v-model="nuevo.descripcion" maxlength="300" required :placeholder="$t('intranet.compras.descripcionPh')">
          </label>
          <label class="corto">{{ $t('intranet.compras.cantidad') }}
            <input v-model.number="nuevo.cantidad" type="number" min="1" max="9999" required>
          </label>
          <label class="corto">{{ $t('intranet.compras.precio') }}
            <input v-model="nuevo.precio" type="number" min="0" step="0.01" inputmode="decimal" :placeholder="$t('intranet.compras.precioPh')">
          </label>
        </div>
        <div class="fila">
          <label>{{ $t('intranet.compras.proveedor') }}
            <input v-model="nuevo.proveedor" maxlength="100" list="proveedores-compras">
          </label>
          <label>{{ $t('intranet.compras.referencia') }}
            <input v-model="nuevo.referencia" maxlength="60" :placeholder="$t('intranet.compras.referenciaPh')">
          </label>
          <button type="submit" class="btn-principal" :disabled="guardando">{{ $t('intranet.compras.anadir') }}</button>
        </div>
        <datalist id="proveedores-compras"><option :value="PROVEEDOR_RS"></option></datalist>
      </form>

      <!-- Llista pendent -->
      <section class="caja">
        <h3>{{ $t('intranet.compras.pendientes', { n: datos.pendientes.length }) }}</h3>
        <p v-if="!datos.pendientes.length" class="vacio">{{ $t('intranet.compras.ninguno') }}</p>
        <div v-else class="tabla-scroll">
          <table class="tabla">
            <thead><tr>
              <th>{{ $t('intranet.compras.fecha') }}</th><th>{{ $t('intranet.compras.pedidoPor') }}</th>
              <th>{{ $t('intranet.compras.descripcion') }}</th><th class="num">{{ $t('intranet.compras.cantCorta') }}</th>
              <th>{{ $t('intranet.compras.proveedor') }}</th><th>{{ $t('intranet.compras.referencia') }}</th>
              <th class="num">{{ $t('intranet.compras.precioCorto') }}</th><th class="num">{{ $t('intranet.compras.importe') }}</th><th></th>
            </tr></thead>
            <tbody>
              <tr v-for="f in [...rs, ...otros]" :key="f.id" :class="{ 'no-rs': !f.es_rs }">
                <template v-if="editando && editando.id === f.id">
                  <td>{{ fecha(f.fecha) }}</td><td>{{ f.pedido_por }}</td>
                  <td><input v-model="editando.descripcion" class="input-fila" maxlength="300" :aria-label="$t('intranet.compras.descripcion')"></td>
                  <td><input v-model.number="editando.cantidad" class="input-fila corto" type="number" min="1" max="9999" :aria-label="$t('intranet.compras.cantidad')"></td>
                  <td><input v-model="editando.proveedor" class="input-fila" maxlength="100" list="proveedores-compras" :aria-label="$t('intranet.compras.proveedor')"></td>
                  <td><input v-model="editando.referencia" class="input-fila" maxlength="60" :aria-label="$t('intranet.compras.referencia')"></td>
                  <td><input v-model="editando.precio" class="input-fila corto" type="number" min="0" step="0.01" :aria-label="$t('intranet.compras.precio')"></td>
                  <td></td>
                  <td class="acciones">
                    <button class="btn-mini guardar" @click="guardarEdicion">{{ $t('intranet.comun.guardar') }}</button>
                    <button class="btn-mini" @click="editando = null">{{ $t('intranet.comun.cancelar') }}</button>
                  </td>
                </template>
                <template v-else>
                  <td>{{ fecha(f.fecha) }}</td><td>{{ f.pedido_por }}</td>
                  <td>{{ f.descripcion }}<span v-if="!f.es_rs" class="etiqueta">{{ $t('intranet.compras.noRs') }}</span></td>
                  <td class="num">{{ f.cantidad }}</td>
                  <td>{{ f.proveedor }}</td><td>{{ f.referencia || '—' }}</td>
                  <td class="num">{{ f.precio == null ? '—' : euros(f.precio) }}</td>
                  <td class="num">{{ importe(f) == null ? '—' : euros(importe(f)) }}</td>
                  <td class="acciones">
                    <template v-if="f.editable">
                      <button class="btn-mini" @click="empezarEdicion(f)" :aria-label="$t('intranet.comun.editar')">✏️</button>
                      <button class="btn-mini peligro" @click="borrar(f)" :aria-label="$t('intranet.comun.borrar')">🗑️</button>
                    </template>
                  </td>
                </template>
              </tr>
            </tbody>
            <tfoot v-if="rs.length"><tr>
              <td colspan="7" class="num"><b>{{ $t('intranet.compras.totalRs') }}</b></td>
              <td class="num"><b>{{ euros(total) }}</b></td><td></td>
            </tr></tfoot>
          </table>
        </div>
        <p v-if="otros.length" class="nota">{{ $t('intranet.compras.notaOtros') }}</p>
      </section>

      <!-- Enviaments anteriors -->
      <section v-if="datos.envios.length" class="caja">
        <h3>{{ $t('intranet.compras.historial') }}</h3>
        <details v-for="e in datos.envios" :key="e.id" class="envio">
          <summary>{{ fecha(e.fecha) }} · {{ e.enviado_por }} · {{ $t('intranet.compras.articulos', { n: e.articulos }) }} · {{ euros(e.total) }}</summary>
          <ul>
            <li v-for="(a, k) in e.items" :key="k">{{ a.cantidad }} × {{ a.descripcion }}<span v-if="a.referencia" class="gris"> ({{ a.referencia }})</span> · {{ a.pedido_por }}</li>
          </ul>
        </details>
      </section>
    </template>
  </div>
</template>

<style scoped>
.panel-compras { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #012169; }
.panel-compras h2 { margin: 0; color: #012169; }
.ayuda { color: #666; font-size: 0.9rem; margin: 8px 0 18px; max-width: 760px; }
.caja { background: #f4f7f9; border-radius: 8px; padding: 15px 20px; margin-bottom: 15px; }
.caja h3 { margin: 0 0 10px; color: #012169; font-size: 1.05rem; }
.ok { color: #198754; font-weight: bold; }
.error { color: #b02a37; font-weight: bold; }
.aviso { color: #7a4300; font-size: 0.88rem; margin: 6px 0 0; }

.progreso { border-left: 4px solid #f0a640; }
.progreso.completo { border-left-color: #198754; }
.progreso-cifras strong { font-size: 1.6rem; color: #012169; }
.progreso-cifras span { color: #555; }
.barra { height: 12px; background: #e3e8ee; border-radius: 6px; overflow: hidden; margin: 8px 0; }
.barra i { display: block; height: 100%; background: #f0a640; transition: width 0.4s; }
.progreso.completo .barra i { background: #198754; }
.estado { margin: 4px 0 0; color: #555; }
.estado-ok { margin: 4px 0 0; color: #198754; font-weight: bold; }
.btn-enviar { margin-top: 12px; background: #198754; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 0.95rem; }
.btn-enviar:disabled { background: #aab4bf; cursor: not-allowed; }

.fila { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; margin-bottom: 8px; }
.fila label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; color: #333; }
.fila input { padding: 8px; border: 1px solid #ccd5df; border-radius: 4px; font: inherit; }
.ancho { flex: 1; min-width: 240px; }
.corto { width: 110px; }
.btn-principal { background: #012169; color: white; border: none; padding: 9px 18px; border-radius: 4px; font-weight: bold; cursor: pointer; }

.tabla-scroll { overflow-x: auto; }
.tabla { width: 100%; border-collapse: collapse; background: white; }
.tabla th, .tabla td { border-bottom: 1px solid #e3e8ee; padding: 8px; text-align: left; font-size: 0.88rem; vertical-align: top; }
.tabla th { color: #555; white-space: nowrap; }
.tabla .num { text-align: right; white-space: nowrap; }
.tabla tfoot td { border-bottom: none; }
.no-rs td { color: #777; }
.etiqueta { margin-left: 6px; font-size: 0.72rem; background: #e3e8ee; color: #555; border-radius: 8px; padding: 1px 7px; white-space: nowrap; }
.input-fila { width: 100%; min-width: 80px; box-sizing: border-box; padding: 5px 8px; }
.input-fila.corto { width: 80px; min-width: 0; }
.acciones { display: flex; gap: 6px; flex-wrap: wrap; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.8rem; }
.btn-mini.guardar { background: #e6f4ea; color: #1e6b34; border-color: #a8d5b5; }
.btn-mini.peligro { color: #b02a37; }
.vacio { color: #666; font-style: italic; }
.nota { color: #666; font-size: 0.85rem; margin: 8px 0 0; }
.envio { background: white; border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; }
.envio summary { cursor: pointer; font-weight: bold; color: #012169; }
.envio ul { margin: 8px 0 0; padding-left: 20px; font-size: 0.88rem; }
.gris { color: #777; }

@media (max-width: 768px) {
  .panel-compras { padding: 14px; }
  .caja { padding: 12px; }
}
</style>
