<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'

// Compres del departament i dels projectes: llista compartida del que cal comprar.
// Cada article és d'un proveïdor (amb la seva comanda mínima per no pagar ports) i del
// departament o d'un projecte. Quan un proveïdor arriba al mínim es demana el pressupost
// (per correu si el proveïdor en té) i els articles passen a l'historial i a les despeses.
defineProps({ sesion: { type: Object, required: true } })
const emit = defineEmits(['sesion-caducada'])
const { t, locale } = useI18n()
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })

const datos = ref(null)
const error = ref('')
const mensaje = ref('')
const guardando = ref(false)
const enviando = ref(null) // id del proveïdor que s'està enviant
const ultimoProveedor = () => {
  try { return Number(localStorage.getItem('sio_compras_proveedor')) || '' } catch { return '' }
}
const vacio = () => ({ descripcion: '', cantidad: 1, precio: '', proveedor_id: ultimoProveedor(), referencia: '', proyecto_id: '' })
const nuevo = ref(vacio())
const editando = ref(null) // còpia de la fila que s'està editant
const formProveedor = ref(null) // { id?, nombre, minimo, portes, email }

const euros = (n) => new Intl.NumberFormat(locale.value, { style: 'currency', currency: 'EUR' }).format(n || 0)
const fecha = (iso) => iso ? new Intl.DateTimeFormat(locale.value, { day: '2-digit', month: '2-digit', year: '2-digit' }).format(new Date(iso.slice(0, 10) + 'T12:00:00')) : ''
const nombreProyecto = (g) => g.proyecto_id == null ? t('intranet.compras.departamento') : g.proyecto

// Primer els proveïdors amb coses pendents
const proveedores = computed(() => [...(datos.value?.proveedores || [])].sort((a, b) => (b.pendientes > 0) - (a.pendientes > 0)))
const porcentaje = (p) => p.minimo > 0 ? Math.min(100, Math.round(100 * p.total / p.minimo)) : 100
const llega = (p) => p.total >= p.minimo
const totalGastos = computed(() => ({
  pendiente: datos.value?.total_pendiente || 0,
  pedido: datos.value?.total_pedido || 0,
  total: (datos.value?.total_pendiente || 0) + (datos.value?.total_pedido || 0)
}))

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
  if (r.ok) {
    datos.value = await r.json()
    // Si només hi ha un proveïdor, ja queda triat
    if (!nuevo.value.proveedor_id && datos.value.proveedores.length === 1) nuevo.value.proveedor_id = datos.value.proveedores[0].id
  } else error.value = t('intranet.compras.errorCarga')
}
onMounted(cargar)

// ---------- Articles ----------
const anadir = async () => {
  guardando.value = true
  try {
    const cuerpo = { ...nuevo.value, proyecto_id: nuevo.value.proyecto_id || null }
    if (await respuesta(await api('/api/compras', json('POST', cuerpo)), t('intranet.compras.anadido'))) {
      try { localStorage.setItem('sio_compras_proveedor', String(nuevo.value.proveedor_id)) } catch { /* sense emmagatzematge */ }
      // Es manté el proveïdor i el projecte: sovint s'apunten diverses coses seguides
      nuevo.value = { ...vacio(), proveedor_id: nuevo.value.proveedor_id, proyecto_id: nuevo.value.proyecto_id }
    }
  } finally {
    guardando.value = false
  }
}
const empezarEdicion = (f) => { editando.value = { ...f, proyecto_id: f.proyecto_id ?? '' } }
const guardarEdicion = async () => {
  const cuerpo = { ...editando.value, proyecto_id: editando.value.proyecto_id || null }
  if (await respuesta(await api(`/api/compras/${editando.value.id}`, json('PUT', cuerpo)), t('intranet.compras.guardado'))) editando.value = null
}
const borrar = async (f) => {
  if (!confirm(t('intranet.compras.confirmarBorrar', { descripcion: f.descripcion }))) return
  await respuesta(await api(`/api/compras/${f.id}`, { method: 'DELETE' }), t('intranet.comun.borrado'))
}
const borrarDelHistorial = async (f) => {
  if (!confirm(t('intranet.compras.confirmarBorrarHistorial', { descripcion: f.descripcion }))) return
  await respuesta(await api(`/api/compras/${f.id}`, { method: 'DELETE' }), t('intranet.compras.borradoHistorial'))
}

// ---------- Enviar / marcar com a demanat ----------
const enviar = async (p, forzar = false) => {
  const datosMsg = { n: p.pendientes, total: euros(p.total), proveedor: p.nombre, destino: p.email, portes: euros(p.portes) }
  let pregunta = p.email ? t('intranet.compras.confirmarEnviar', datosMsg) : t('intranet.compras.confirmarMarcar', datosMsg)
  if (forzar) pregunta = t('intranet.compras.avisoPortes', datosMsg) + '\n\n' + pregunta
  if (!confirm(pregunta)) return
  enviando.value = p.id
  try {
    const ok = p.email ? t('intranet.compras.enviado', datosMsg) : t('intranet.compras.marcado', datosMsg)
    await respuesta(await api(`/api/compras/enviar/${p.id}`, json('POST', { forzar })), ok)
  } finally {
    enviando.value = null
  }
}

// ---------- Proveïdors ----------
const nuevoProveedor = () => { formProveedor.value = { nombre: '', minimo: '', portes: '', email: '' } }
const editarProveedor = (p) => { formProveedor.value = { id: p.id, nombre: p.nombre, minimo: p.minimo, portes: p.portes, email: p.email } }
const guardarProveedor = async () => {
  const f = formProveedor.value
  const r = f.id
    ? await api(`/api/compras/proveedores/${f.id}`, json('PUT', f))
    : await api('/api/compras/proveedores', json('POST', f))
  if (await respuesta(r, t('intranet.compras.proveedorGuardado', { nombre: f.nombre }))) {
    if (!f.id && !nuevo.value.proveedor_id) {
      const creado = datos.value.proveedores.find(p => p.nombre.toLowerCase() === f.nombre.trim().toLowerCase())
      if (creado) nuevo.value.proveedor_id = creado.id
    }
    formProveedor.value = null
  }
}
const borrarProveedor = async (p) => {
  if (!confirm(t('intranet.compras.confirmarBorrarProveedor', { nombre: p.nombre }))) return
  if (await respuesta(await api(`/api/compras/proveedores/${p.id}`, { method: 'DELETE' }), t('intranet.comun.borrado'))) {
    if (nuevo.value.proveedor_id === p.id) nuevo.value.proveedor_id = ''
  }
}
</script>

<template>
  <div class="panel-compras">
    <h2>{{ $t('intranet.compras.titulo') }}</h2>
    <p class="ayuda">{{ $t('intranet.compras.ayuda') }}</p>

    <p v-if="mensaje" class="ok" role="status">{{ mensaje }}</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <template v-if="datos">
      <!-- Proveïdors: comanda mínima, ports i botó per demanar -->
      <section class="caja">
        <div class="cabecera">
          <h3>{{ $t('intranet.compras.proveedores') }}</h3>
          <button v-if="!formProveedor" type="button" class="btn-mini" @click="nuevoProveedor">{{ $t('intranet.compras.nuevoProveedor') }}</button>
        </div>

        <form v-if="formProveedor" class="form-proveedor" @submit.prevent="guardarProveedor">
          <h4>{{ formProveedor.id ? $t('intranet.compras.editarProveedor') : $t('intranet.compras.nuevoProveedorTitulo') }}</h4>
          <p class="nota">{{ $t('intranet.compras.ayudaProveedor') }}</p>
          <div class="fila">
            <label class="ancho">{{ $t('intranet.compras.nombreProveedor') }}
              <input v-model="formProveedor.nombre" maxlength="100" required :placeholder="$t('intranet.compras.nombreProveedorPh')">
            </label>
            <label class="corto">{{ $t('intranet.compras.minimo') }}
              <input v-model="formProveedor.minimo" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0">
            </label>
            <label class="corto">{{ $t('intranet.compras.portes') }}
              <input v-model="formProveedor.portes" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0">
            </label>
          </div>
          <div class="fila">
            <label class="ancho">{{ $t('intranet.compras.emailProveedor') }}
              <input v-model="formProveedor.email" type="email" maxlength="200" :placeholder="$t('intranet.compras.emailProveedorPh')">
            </label>
            <button type="submit" class="btn-principal">{{ $t('intranet.comun.guardar') }}</button>
            <button type="button" class="btn-mini" @click="formProveedor = null">{{ $t('intranet.comun.cancelar') }}</button>
          </div>
        </form>

        <div class="tarjetas">
          <article v-for="p in proveedores" :key="p.id" class="tarjeta" :class="{ completo: p.pendientes && llega(p), vacia: !p.pendientes }">
            <header>
              <strong>{{ p.nombre }}</strong>
              <span class="acciones">
                <button type="button" class="btn-icono" :title="$t('intranet.compras.editarProveedor')" :aria-label="$t('intranet.compras.editarProveedor')" @click="editarProveedor(p)">✏️</button>
                <button v-if="p.borrable" type="button" class="btn-icono" :title="$t('intranet.comun.borrar')" :aria-label="$t('intranet.comun.borrar')" @click="borrarProveedor(p)">🗑️</button>
              </span>
            </header>
            <p class="condiciones">
              <template v-if="p.minimo > 0">{{ $t('intranet.compras.condiciones', { minimo: euros(p.minimo), portes: euros(p.portes) }) }}</template>
              <template v-else-if="p.portes > 0">{{ $t('intranet.compras.siemprePortes', { portes: euros(p.portes) }) }}</template>
              <template v-else>{{ $t('intranet.compras.sinMinimo') }}</template>
              <br><span class="gris">{{ p.email ? '📧 ' + p.email : $t('intranet.compras.sinEmail') }}</span>
            </p>
            <template v-if="p.pendientes">
              <div class="cifras"><strong>{{ euros(p.total) }}</strong><span v-if="p.minimo > 0"> / {{ euros(p.minimo) }}</span> <span class="gris">{{ $t('intranet.compras.sinIva') }}</span></div>
              <div v-if="p.minimo > 0" class="barra" role="progressbar" :aria-valuenow="porcentaje(p)" aria-valuemin="0" aria-valuemax="100"><i :style="{ width: porcentaje(p) + '%' }"></i></div>
              <p v-if="llega(p)" class="estado-ok">✅ {{ p.minimo > 0 ? $t('intranet.compras.alcanzado') : $t('intranet.compras.listo') }}</p>
              <p v-else class="estado">{{ $t('intranet.compras.falta', { falta: euros(p.minimo - p.total) }) }}</p>
              <div class="botones">
                <button v-if="llega(p)" type="button" class="btn-enviar" :disabled="enviando === p.id || (!!p.email && !datos.correo_configurado)" @click="enviar(p)">
                  {{ p.email ? $t('intranet.compras.enviar') : $t('intranet.compras.marcar') }}
                </button>
                <button v-else type="button" class="btn-forzar" :disabled="enviando === p.id || (!!p.email && !datos.correo_configurado)" @click="enviar(p, true)">
                  {{ $t('intranet.compras.forzar', { portes: euros(p.portes) }) }}
                </button>
              </div>
              <p v-if="p.email && !datos.correo_configurado" class="aviso">{{ $t('intranet.compras.sinCorreo') }}</p>
            </template>
            <p v-else class="gris">{{ $t('intranet.compras.nadaPendiente') }}</p>
          </article>
        </div>
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
            <input v-model="nuevo.precio" type="number" min="0.01" step="0.01" inputmode="decimal" required :placeholder="$t('intranet.compras.precioPh')">
          </label>
        </div>
        <div class="fila">
          <label>{{ $t('intranet.compras.proveedor') }}
            <select v-model="nuevo.proveedor_id" required>
              <option value="" disabled>{{ $t('intranet.compras.eligeProveedor') }}</option>
              <option v-for="p in datos.proveedores" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </label>
          <label>{{ $t('intranet.compras.referencia') }}
            <input v-model="nuevo.referencia" maxlength="60" :placeholder="$t('intranet.compras.referenciaPh')">
          </label>
          <label class="ancho">{{ $t('intranet.compras.paraQuien') }}
            <select v-model="nuevo.proyecto_id">
              <option value="">{{ $t('intranet.compras.departamento') }}</option>
              <option v-for="pr in datos.proyectos" :key="pr.id" :value="pr.id">{{ pr.titulo }}</option>
            </select>
          </label>
          <button type="submit" class="btn-principal" :disabled="guardando">{{ $t('intranet.compras.anadir') }}</button>
        </div>
        <p class="nota">{{ $t('intranet.compras.notaProveedor') }}</p>
      </form>

      <!-- Llista pendent -->
      <section class="caja">
        <h3>{{ $t('intranet.compras.pendientes', { n: datos.pendientes.length }) }}</h3>
        <p v-if="!datos.pendientes.length" class="vacio">{{ $t('intranet.compras.ninguno') }}</p>
        <div v-else class="tabla-scroll">
          <table class="tabla">
            <thead><tr>
              <th>{{ $t('intranet.compras.pedidoPor') }}</th>
              <th>{{ $t('intranet.compras.descripcion') }}</th><th class="num">{{ $t('intranet.compras.cantCorta') }}</th>
              <th>{{ $t('intranet.compras.proyecto') }}</th>
              <th>{{ $t('intranet.compras.proveedor') }}</th>
              <th class="num">{{ $t('intranet.compras.precioCorto') }}</th><th class="num">{{ $t('intranet.compras.importe') }}</th><th></th>
            </tr></thead>
            <tbody>
              <tr v-for="f in datos.pendientes" :key="f.id">
                <template v-if="editando && editando.id === f.id">
                  <td>{{ f.pedido_por }}<br><span class="gris">{{ fecha(f.fecha) }}</span></td>
                  <td class="desc"><input v-model="editando.descripcion" class="input-fila" maxlength="300" :aria-label="$t('intranet.compras.descripcion')">
                    <input v-model="editando.referencia" class="input-fila ref" maxlength="60" :placeholder="$t('intranet.compras.referencia')" :aria-label="$t('intranet.compras.referencia')"></td>
                  <td><input v-model.number="editando.cantidad" class="input-fila corto" type="number" min="1" max="9999" :aria-label="$t('intranet.compras.cantidad')"></td>
                  <td>
                    <select v-model="editando.proyecto_id" class="input-fila" :aria-label="$t('intranet.compras.proyecto')">
                      <option value="">{{ $t('intranet.compras.departamento') }}</option>
                      <option v-for="pr in datos.proyectos" :key="pr.id" :value="pr.id">{{ pr.titulo }}</option>
                    </select>
                  </td>
                  <td>
                    <select v-model="editando.proveedor_id" class="input-fila" :aria-label="$t('intranet.compras.proveedor')">
                      <option v-for="p in datos.proveedores" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                    </select>
                  </td>
                  <td><input v-model="editando.precio" class="input-fila corto" type="number" min="0.01" step="0.01" required :aria-label="$t('intranet.compras.precio')"></td>
                  <td></td>
                  <td><div class="acciones">
                    <button class="btn-mini guardar" :disabled="editando.precio === '' || editando.precio == null" @click="guardarEdicion">{{ $t('intranet.comun.guardar') }}</button>
                    <button class="btn-mini" @click="editando = null">{{ $t('intranet.comun.cancelar') }}</button>
                  </div></td>
                </template>
                <template v-else>
                  <td>{{ f.pedido_por }}<br><span class="gris">{{ fecha(f.fecha) }}</span></td>
                  <td class="desc">{{ f.descripcion }}<br v-if="f.referencia"><span v-if="f.referencia" class="gris">{{ $t('intranet.compras.refCorta') }} {{ f.referencia }}</span></td>
                  <td class="num">{{ f.cantidad }}</td>
                  <td><span class="etiqueta" :class="{ dpto: !f.proyecto_id }">{{ f.proyecto_id ? f.proyecto : $t('intranet.compras.departamentoCorto') }}</span></td>
                  <td>{{ f.proveedor }}</td>
                  <td class="num">{{ euros(f.precio) }}</td>
                  <td class="num">{{ euros(f.importe) }}</td>
                  <td><div class="acciones">
                    <template v-if="f.editable">
                      <button class="btn-mini" @click="empezarEdicion(f)" :aria-label="$t('intranet.comun.editar')">✏️</button>
                      <button class="btn-mini peligro" @click="borrar(f)" :aria-label="$t('intranet.comun.borrar')">🗑️</button>
                    </template>
                  </div></td>
                </template>
              </tr>
            </tbody>
            <tfoot><tr>
              <td colspan="6" class="num"><b>{{ $t('intranet.compras.totalPendiente') }}</b></td>
              <td class="num"><b>{{ euros(datos.total_pendiente) }}</b></td><td></td>
            </tr></tfoot>
          </table>
        </div>
      </section>

      <!-- Despeses per projecte -->
      <section v-if="datos.gastos.length" class="caja">
        <h3>{{ $t('intranet.compras.gastos') }}</h3>
        <p class="nota">{{ $t('intranet.compras.ayudaGastos') }}</p>
        <div class="tabla-scroll">
          <table class="tabla gastos">
            <thead><tr>
              <th>{{ $t('intranet.compras.proyecto') }}</th>
              <th class="num">{{ $t('intranet.compras.pendiente') }}</th>
              <th class="num">{{ $t('intranet.compras.pedido') }}</th>
              <th class="num">{{ $t('intranet.compras.total') }}</th>
            </tr></thead>
            <tbody>
              <tr v-for="g in datos.gastos" :key="g.proyecto_id ?? 'dpto'">
                <td>{{ nombreProyecto(g) }}</td>
                <td class="num">{{ euros(g.pendiente) }}</td>
                <td class="num">{{ euros(g.pedido) }}</td>
                <td class="num"><b>{{ euros(g.total) }}</b></td>
              </tr>
            </tbody>
            <tfoot><tr>
              <td><b>{{ $t('intranet.compras.totalTodo') }}</b></td>
              <td class="num"><b>{{ euros(totalGastos.pendiente) }}</b></td>
              <td class="num"><b>{{ euros(totalGastos.pedido) }}</b></td>
              <td class="num"><b>{{ euros(totalGastos.total) }}</b></td>
            </tr></tfoot>
          </table>
        </div>
      </section>

      <!-- Comandes anteriors -->
      <section v-if="datos.envios.length" class="caja">
        <h3>{{ $t('intranet.compras.historial') }}</h3>
        <p class="nota">{{ $t('intranet.compras.ayudaHistorial') }}</p>
        <details v-for="e in datos.envios" :key="e.id" class="envio">
          <summary>
            {{ fecha(e.fecha) }} · {{ e.proveedor }} · {{ e.enviado_por }} · {{ $t('intranet.compras.articulos', { n: e.articulos }) }} · {{ euros(e.total) }}
            <span class="gris">{{ e.destinatario ? '📧 ' + e.destinatario : $t('intranet.compras.sinCorreoEnviado') }}</span>
          </summary>
          <ul>
            <li v-for="a in e.items" :key="a.id">
              <span>{{ a.cantidad }} × {{ a.descripcion }}<span v-if="a.referencia" class="gris"> ({{ a.referencia }})</span>
                · {{ euros(a.importe) }} · <span class="etiqueta" :class="{ dpto: !a.proyecto_id }">{{ a.proyecto_id ? a.proyecto : $t('intranet.compras.departamentoCorto') }}</span>
                <span class="gris"> · {{ a.pedido_por }}</span></span>
              <button v-if="a.editable" type="button" class="btn-icono" :title="$t('intranet.compras.noComprado')" :aria-label="$t('intranet.compras.noComprado')" @click="borrarDelHistorial(a)">🗑️</button>
            </li>
          </ul>
        </details>
      </section>
    </template>
  </div>
</template>

<style scoped>
.panel-compras { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #012169; }
.panel-compras h2 { margin: 0; color: #012169; }
.ayuda { color: #666; font-size: 0.9rem; margin: 8px 0 18px; max-width: 800px; }
.caja { background: #f4f7f9; border-radius: 8px; padding: 15px 20px; margin-bottom: 15px; }
.caja h3 { margin: 0 0 10px; color: #012169; font-size: 1.05rem; }
.cabecera { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 10px; }
.cabecera h3 { margin: 0; }
.ok { color: #198754; font-weight: bold; }
.error { color: #b02a37; font-weight: bold; }
.aviso { color: #7a4300; font-size: 0.85rem; margin: 6px 0 0; }

/* Proveïdors */
.form-proveedor { background: white; border: 1px solid #d0d7de; border-radius: 8px; padding: 12px 15px; margin-bottom: 12px; }
.form-proveedor h4 { margin: 0 0 4px; color: #012169; }
.tarjetas { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.tarjeta { background: white; border-radius: 8px; padding: 12px 14px; border-left: 4px solid #f0a640; display: flex; flex-direction: column; gap: 4px; }
.tarjeta.completo { border-left-color: #198754; }
.tarjeta.vacia { border-left-color: #c8d0d8; }
.tarjeta header { display: flex; justify-content: space-between; align-items: center; gap: 6px; color: #012169; }
.condiciones { margin: 0; font-size: 0.83rem; color: #444; }
.cifras strong { font-size: 1.35rem; color: #012169; }
.barra { height: 10px; background: #e3e8ee; border-radius: 5px; overflow: hidden; margin: 4px 0; }
.barra i { display: block; height: 100%; background: #f0a640; transition: width 0.4s; }
.tarjeta.completo .barra i { background: #198754; }
.estado { margin: 0; color: #555; font-size: 0.88rem; }
.estado-ok { margin: 0; color: #198754; font-weight: bold; font-size: 0.88rem; }
.botones { margin-top: 6px; }
.btn-enviar { background: #198754; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; }
.btn-forzar { background: white; color: #7a4300; border: 1px solid #e0b36a; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-enviar:disabled, .btn-forzar:disabled { background: #aab4bf; color: white; border-color: #aab4bf; cursor: not-allowed; }
.btn-icono { background: none; border: none; cursor: pointer; padding: 2px 4px; font-size: 0.9rem; opacity: 0.75; }
.btn-icono:hover { opacity: 1; }

/* Formularis */
.fila { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; margin-bottom: 8px; }
.fila label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; color: #333; }
.fila input, .fila select { padding: 8px; border: 1px solid #ccd5df; border-radius: 4px; font: inherit; background: white; }
.fila select { max-width: 100%; }
.ancho { flex: 1; min-width: 220px; }
.corto { width: 120px; }
.btn-principal { background: #012169; color: white; border: none; padding: 9px 18px; border-radius: 4px; font-weight: bold; cursor: pointer; }

/* Taules */
.tabla-scroll { overflow-x: auto; }
.tabla { width: 100%; border-collapse: collapse; background: white; }
.tabla th, .tabla td { border-bottom: 1px solid #e3e8ee; padding: 8px; text-align: left; font-size: 0.88rem; vertical-align: top; }
.tabla th { color: #555; white-space: nowrap; }
.tabla .num { text-align: right; white-space: nowrap; }
.tabla tfoot td { border-bottom: none; }
.tabla.gastos { max-width: 720px; }
.etiqueta { font-size: 0.75rem; background: #e0ebff; color: #012169; border-radius: 8px; padding: 1px 8px; white-space: nowrap; display: inline-block; max-width: 220px; overflow: hidden; text-overflow: ellipsis; vertical-align: middle; }
.etiqueta.dpto { background: #e3e8ee; color: #555; }
.input-fila { width: 100%; min-width: 80px; box-sizing: border-box; padding: 5px 8px; }
.input-fila.ref { margin-top: 4px; }
.input-fila.corto { width: 80px; min-width: 0; }
.acciones { display: flex; gap: 6px; }
.tabla td.desc { min-width: 180px; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.8rem; }
.btn-mini.guardar { background: #e6f4ea; color: #1e6b34; border-color: #a8d5b5; }
.btn-mini.peligro { color: #b02a37; }
.vacio { color: #666; font-style: italic; }
.nota { color: #666; font-size: 0.83rem; margin: 2px 0 8px; }
.envio { background: white; border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; }
.envio summary { cursor: pointer; font-weight: bold; color: #012169; }
.envio summary .gris { font-weight: normal; font-size: 0.83rem; margin-left: 4px; }
.envio ul { margin: 8px 0 0; padding-left: 20px; font-size: 0.88rem; }
.envio li { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; padding: 3px 0; border-bottom: 1px dashed #e3e8ee; }
.gris { color: #777; }

@media (max-width: 768px) {
  .panel-compras { padding: 14px; }
  .caja { padding: 12px; }
  .fila label, .ancho { width: 100%; min-width: 0; }
  .corto { width: calc(50% - 6px); }
  .tarjetas { grid-template-columns: 1fr; }
}
</style>
