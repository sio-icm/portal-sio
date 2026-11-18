<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { traducirError } from '../i18n'
import { peticionIntranet } from '../utils/diario'

// Compres: a dalt es tria de qui són les compres (el departament o un projecte) i tot el que
// hi ha a sota és només d'aquell compte: la comanda en curs de cada proveïdor (amb el seu mínim
// per no pagar ports), el formulari per afegir-hi (només si s'hi pot comprar), la llista
// pendent i les comandes fetes. Cada compte fa la seva comanda (el mínim compta per separat).
// Al final hi ha el resum de totes les despeses.
const props = defineProps({ sesion: { type: Object, required: true } })
const emit = defineEmits(['sesion-caducada'])
const { t, locale } = useI18n()
const api = (url, opciones) => peticionIntranet(url, opciones, () => emit('sesion-caducada'))
const json = (metodo, cuerpo) => ({ method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })
const leer = (clave) => { try { return localStorage.getItem(clave) } catch { return null } }
const guardar = (clave, valor) => { try { localStorage.setItem(clave, valor) } catch { /* sense emmagatzematge */ } }

const datos = ref(null)
const error = ref('')
const mensaje = ref('')
const guardando = ref(false)
const enviando = ref(null) // id del proveïdor que s'està enviant
const vacio = () => ({ descripcion: '', cantidad: 1, precio: '', proveedor_id: Number(leer('sio_compras_proveedor')) || '', referencia: '', solicitante_id: props.sesion.usuario_id || '' })
const nuevo = ref(vacio())
const editando = ref(null) // còpia de la fila que s'està editant
const formProveedor = ref(null) // { id?, nombre, minimo, portes, email }

const euros = (n) => new Intl.NumberFormat(locale.value, { style: 'currency', currency: 'EUR' }).format(n || 0)
const fecha = (iso) => iso ? new Intl.DateTimeFormat(locale.value, { day: '2-digit', month: '2-digit', year: '2-digit' }).format(new Date(iso.slice(0, 10) + 'T12:00:00')) : ''
const nombreUsuario = (id) => datos.value?.usuarios.find(u => u.id === id)?.nombre || ''
const suma = (filas) => filas.reduce((s, f) => s + f.importe, 0)

// ---------- Compte que es mira: '' = departament, o l'id d'un projecte ----------
const contexto = ref(leer('sio_compras_contexto') || '')
watch(contexto, (v) => { guardar('sio_compras_contexto', String(v)); editando.value = null; mensaje.value = ''; error.value = '' })
const ctx = computed(() => {
  const pr = contexto.value && (datos.value?.proyectos || []).find(p => String(p.id) === String(contexto.value))
  return pr ? { id: pr.id, titulo: pr.titulo } : { id: null, titulo: '' }
})
const esDelCtx = (f) => (f.proyecto_id ?? null) === ctx.value.id

// Pendent del compte, agrupat per proveïdor (cada proveïdor = una comanda amb el seu mínim)
const pendientesCtx = computed(() => (datos.value?.pendientes || []).filter(esDelCtx))
const comandas = computed(() => (datos.value?.proveedores || [])
  .map(p => {
    const filas = pendientesCtx.value.filter(f => f.proveedor_id === p.id)
    return { ...p, filas, pendientes: filas.length, total: Math.round(suma(filas) * 100) / 100 }
  })
  .filter(p => p.pendientes > 0))
const otrosProveedores = computed(() => (datos.value?.proveedores || []).filter(p => !comandas.value.some(c => c.id === p.id)))
const porcentaje = (p) => p.minimo > 0 ? Math.min(100, Math.round(100 * p.total / p.minimo)) : 100
const llega = (p) => p.total >= p.minimo

// Comandes fetes d'aquest compte (només els seus articles)
const enviosCtx = computed(() => (datos.value?.envios || [])
  .map(e => { const items = e.items.filter(esDelCtx); return { ...e, items, totalCtx: suma(items) } })
  .filter(e => e.items.length))
const totalesCtx = computed(() => ({
  pendiente: suma(pendientesCtx.value),
  pedido: enviosCtx.value.reduce((s, e) => s + e.totalCtx, 0)
}))
const totalGastos = computed(() => ({
  pendiente: datos.value?.total_pendiente || 0,
  pedido: datos.value?.total_pedido || 0,
  total: (datos.value?.total_pendiente || 0) + (datos.value?.total_pedido || 0)
}))
const nombreGasto = (g) => g.proyecto_id == null ? t('intranet.compras.departamento') : g.proyecto

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
    if (contexto.value && !datos.value.proyectos.some(p => String(p.id) === String(contexto.value))) contexto.value = ''
    if (!nuevo.value.proveedor_id && datos.value.proveedores.length === 1) nuevo.value.proveedor_id = datos.value.proveedores[0].id
  } else error.value = t('intranet.compras.errorCarga')
}
onMounted(cargar)

// ---------- Articles ----------
const anadir = async () => {
  guardando.value = true
  try {
    const cuerpo = { ...nuevo.value, proyecto_id: ctx.value.id }
    if (await respuesta(await api('/api/compras', json('POST', cuerpo)), t('intranet.compras.anadido'))) {
      guardar('sio_compras_proveedor', String(nuevo.value.proveedor_id))
      // Es manté el proveïdor i qui ho demana: sovint s'apunten diverses coses seguides
      nuevo.value = { ...vacio(), proveedor_id: nuevo.value.proveedor_id, solicitante_id: nuevo.value.solicitante_id }
    }
  } finally {
    guardando.value = false
  }
}
const empezarEdicion = (f) => { editando.value = { ...f, proyecto_id: f.proyecto_id ?? '', solicitante_id: f.solicitante_id ?? '' } }
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

// ---------- Enviar / marcar com a demanat (només la comanda d'aquest compte) ----------
const enviar = async (p, forzar = false) => {
  const datosMsg = { n: p.pendientes, total: euros(p.total), proveedor: p.nombre, destino: p.email, portes: euros(p.portes) }
  let pregunta = p.email ? t('intranet.compras.confirmarEnviar', datosMsg) : t('intranet.compras.confirmarMarcar', datosMsg)
  if (ctx.value.id) pregunta = t('intranet.compras.paraProyecto', { proyecto: ctx.value.titulo }) + '\n\n' + pregunta
  if (forzar) pregunta = t('intranet.compras.avisoPortes', datosMsg) + '\n\n' + pregunta
  if (!confirm(pregunta)) return
  enviando.value = p.id
  try {
    const ok = p.email ? t('intranet.compras.enviado', datosMsg) : t('intranet.compras.marcado', datosMsg)
    await respuesta(await api(`/api/compras/enviar/${p.id}`, json('POST', { forzar, proyecto_id: ctx.value.id })), ok)
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
const verProyecto = (id) => { contexto.value = id == null ? '' : id; window.scrollTo({ top: 0, behavior: 'smooth' }) }
</script>

<template>
  <div class="panel-compras">
    <h2>{{ $t('intranet.compras.titulo') }}</h2>

    <template v-if="datos">
      <!-- De qui són les compres que es miren -->
      <div class="contexto">
        <label>{{ $t('intranet.compras.verComprasDe') }}
          <select v-model="contexto">
            <option value="">🏢 {{ $t('intranet.compras.departamento') }}</option>
            <option v-for="pr in datos.proyectos" :key="pr.id" :value="String(pr.id)">📁 {{ pr.titulo }}</option>
          </select>
        </label>
      </div>

      <section class="cuenta" :class="{ proyecto: ctx.id }">
        <h3 class="titulo-cuenta">{{ ctx.id ? $t('intranet.compras.tituloProyecto', { proyecto: ctx.titulo }) : $t('intranet.compras.tituloDepartamento') }}</h3>
        <p class="ayuda">
          {{ ctx.id ? $t('intranet.compras.ayudaCtxProyecto') : $t('intranet.compras.ayudaCtxDepartamento') }}
        </p>
        <p class="totales">
          <span>{{ $t('intranet.compras.pendiente') }}: <b>{{ euros(totalesCtx.pendiente) }}</b></span>
          <span>{{ $t('intranet.compras.pedido') }}: <b>{{ euros(totalesCtx.pedido) }}</b></span>
          <span class="gris">{{ $t('intranet.compras.sinIva') }}</span>
        </p>

        <p v-if="mensaje" class="ok" role="status">{{ mensaje }}</p>
        <p v-if="error" class="error" role="alert">{{ error }}</p>

        <!-- Comanda en curs de cada proveïdor -->
        <div class="bloque">
          <div class="cabecera">
            <h4>{{ $t('intranet.compras.comandaEnCurso') }}</h4>
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

          <p v-if="!comandas.length" class="vacio">{{ $t('intranet.compras.ninguno') }}</p>
          <div class="tarjetas">
            <article v-for="p in comandas" :key="p.id" class="tarjeta" :class="{ completo: llega(p) }">
              <header>
                <strong>{{ p.nombre }}</strong>
                <button type="button" class="btn-icono" :title="$t('intranet.compras.editarProveedor')" :aria-label="$t('intranet.compras.editarProveedor')" @click="editarProveedor(p)">✏️</button>
              </header>
              <p class="condiciones">
                <template v-if="p.minimo > 0">{{ $t('intranet.compras.condiciones', { minimo: euros(p.minimo), portes: euros(p.portes) }) }}</template>
                <template v-else-if="p.portes > 0">{{ $t('intranet.compras.siemprePortes', { portes: euros(p.portes) }) }}</template>
                <template v-else>{{ $t('intranet.compras.sinMinimo') }}</template>
                <br><span class="gris">{{ p.email ? '📧 ' + p.email : $t('intranet.compras.sinEmail') }}</span>
              </p>
              <div class="cifras"><strong>{{ euros(p.total) }}</strong><span v-if="p.minimo > 0"> / {{ euros(p.minimo) }}</span> <span class="gris">· {{ $t('intranet.compras.articulos', { n: p.pendientes }) }}</span></div>
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
            </article>
          </div>
          <p v-if="otrosProveedores.length" class="otros">
            {{ $t('intranet.compras.otrosProveedores') }}
            <span v-for="p in otrosProveedores" :key="p.id" class="otro">
              {{ p.nombre }}
              <button type="button" class="btn-icono" :title="$t('intranet.compras.editarProveedor')" :aria-label="$t('intranet.compras.editarProveedor')" @click="editarProveedor(p)">✏️</button>
              <button v-if="p.borrable" type="button" class="btn-icono" :title="$t('intranet.comun.borrar')" :aria-label="$t('intranet.comun.borrar')" @click="borrarProveedor(p)">🗑️</button>
            </span>
          </p>
        </div>

        <!-- Afegir -->
        <form class="bloque nuevo" @submit.prevent="anadir">
          <h4>{{ ctx.id ? $t('intranet.compras.anadirProyecto', { proyecto: ctx.titulo }) : $t('intranet.compras.anadirDepartamento') }}</h4>
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
            <label>{{ $t('intranet.compras.pedidoPor') }}
              <select v-model="nuevo.solicitante_id" required>
                <option v-for="u in datos.usuarios" :key="u.id" :value="u.id">{{ u.nombre }}</option>
              </select>
            </label>
            <button type="submit" class="btn-principal" :disabled="guardando">{{ $t('intranet.compras.anadir') }}</button>
          </div>
          <p class="nota">{{ $t('intranet.compras.notaProveedor') }}</p>
        </form>

        <!-- Llista pendent d'aquest compte, per proveïdor -->
        <div class="bloque">
          <h4>{{ $t('intranet.compras.pendientes', { n: pendientesCtx.length }) }}</h4>
          <p v-if="!pendientesCtx.length" class="vacio">{{ $t('intranet.compras.ninguno') }}</p>
          <div v-else class="tabla-scroll">
            <table class="tabla">
              <thead><tr>
                <th>{{ $t('intranet.compras.pedidoPor') }}</th>
                <th>{{ $t('intranet.compras.descripcion') }}</th><th class="num">{{ $t('intranet.compras.cantCorta') }}</th>
                <th class="num">{{ $t('intranet.compras.precioCorto') }}</th><th class="num">{{ $t('intranet.compras.importe') }}</th><th></th>
              </tr></thead>
              <tbody v-for="g in comandas" :key="g.id">
                <tr class="grupo">
                  <th colspan="4">{{ g.nombre }}</th>
                  <th class="num">{{ euros(g.total) }}</th><th></th>
                </tr>
                <tr v-for="f in g.filas" :key="f.id">
                  <template v-if="editando && editando.id === f.id">
                    <td>
                      <select v-model="editando.solicitante_id" class="input-fila" :aria-label="$t('intranet.compras.pedidoPor')">
                        <option v-for="u in datos.usuarios" :key="u.id" :value="u.id">{{ u.nombre }}</option>
                      </select>
                    </td>
                    <td class="desc">
                      <input v-model="editando.descripcion" class="input-fila" maxlength="300" :aria-label="$t('intranet.compras.descripcion')">
                      <input v-model="editando.referencia" class="input-fila mas" maxlength="60" :placeholder="$t('intranet.compras.referencia')" :aria-label="$t('intranet.compras.referencia')">
                      <span class="mas-fila">
                        <select v-model="editando.proveedor_id" class="input-fila" :aria-label="$t('intranet.compras.proveedor')">
                          <option v-for="p in datos.proveedores" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                        </select>
                        <select v-model="editando.proyecto_id" class="input-fila" :aria-label="$t('intranet.compras.proyecto')">
                          <option value="">{{ $t('intranet.compras.departamento') }}</option>
                          <option v-for="pr in datos.proyectos" :key="pr.id" :value="pr.id">{{ pr.titulo }}</option>
                        </select>
                      </span>
                    </td>
                    <td><input v-model.number="editando.cantidad" class="input-fila corto" type="number" min="1" max="9999" :aria-label="$t('intranet.compras.cantidad')"></td>
                    <td><input v-model="editando.precio" class="input-fila corto" type="number" min="0.01" step="0.01" required :aria-label="$t('intranet.compras.precio')"></td>
                    <td></td>
                    <td><div class="acciones">
                      <button class="btn-mini guardar" :disabled="editando.precio === '' || editando.precio == null" @click="guardarEdicion">{{ $t('intranet.comun.guardar') }}</button>
                      <button class="btn-mini" @click="editando = null">{{ $t('intranet.comun.cancelar') }}</button>
                    </div></td>
                  </template>
                  <template v-else>
                    <td>{{ f.pedido_por }}<br><span class="gris">{{ fecha(f.fecha) }}<template v-if="f.usuario_id && f.usuario_id !== f.solicitante_id"> · {{ $t('intranet.compras.apuntadoPor', { nombre: nombreUsuario(f.usuario_id) }) }}</template></span></td>
                    <td class="desc">{{ f.descripcion }}<br v-if="f.referencia"><span v-if="f.referencia" class="gris">{{ $t('intranet.compras.refCorta') }} {{ f.referencia }}</span></td>
                    <td class="num">{{ f.cantidad }}</td>
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
                <td colspan="4" class="num"><b>{{ $t('intranet.compras.totalPendiente') }}</b></td>
                <td class="num"><b>{{ euros(totalesCtx.pendiente) }}</b></td><td></td>
              </tr></tfoot>
            </table>
          </div>
        </div>

        <!-- Comandes fetes d'aquest compte -->
        <div class="bloque">
          <h4>{{ $t('intranet.compras.historial') }}</h4>
          <p v-if="!enviosCtx.length" class="vacio">{{ $t('intranet.compras.sinHistorial') }}</p>
          <template v-else>
            <p class="nota">{{ $t('intranet.compras.ayudaHistorial') }}</p>
            <details v-for="e in enviosCtx" :key="e.id" class="envio">
              <summary>
                {{ fecha(e.fecha) }} · {{ e.proveedor }} · {{ e.enviado_por }} · {{ $t('intranet.compras.articulos', { n: e.items.length }) }} · {{ euros(e.totalCtx) }}
                <span class="gris">{{ e.destinatario ? '📧 ' + e.destinatario : $t('intranet.compras.sinCorreoEnviado') }}</span>
              </summary>
              <ul>
                <li v-for="a in e.items" :key="a.id">
                  <span>{{ a.cantidad }} × {{ a.descripcion }}<span v-if="a.referencia" class="gris"> ({{ a.referencia }})</span>
                    · {{ euros(a.importe) }}<span class="gris"> · {{ a.pedido_por }}</span></span>
                  <button v-if="a.editable" type="button" class="btn-icono" :title="$t('intranet.compras.noComprado')" :aria-label="$t('intranet.compras.noComprado')" @click="borrarDelHistorial(a)">🗑️</button>
                </li>
              </ul>
            </details>
          </template>
        </div>
      </section>

      <!-- Resum de totes les compres -->
      <details v-if="datos.gastos.length" class="caja plegable">
        <summary><h3>{{ $t('intranet.compras.resumenTodo') }}</h3></summary>
        <p class="nota">{{ $t('intranet.compras.ayudaGastos') }} {{ $t('intranet.compras.ayudaResumenTodo') }}</p>
        <div class="tabla-scroll">
          <table class="tabla gastos">
            <thead><tr>
              <th>{{ $t('intranet.compras.proyecto') }}</th>
              <th class="num">{{ $t('intranet.compras.pendiente') }}</th>
              <th class="num">{{ $t('intranet.compras.pedido') }}</th>
              <th class="num">{{ $t('intranet.compras.total') }}</th>
            </tr></thead>
            <tbody>
              <tr v-for="g in datos.gastos" :key="g.proyecto_id ?? 'dpto'" class="clicable" :class="{ actual: (g.proyecto_id ?? null) === ctx.id }" @click="verProyecto(g.proyecto_id)">
                <td><a href="#" @click.prevent>{{ nombreGasto(g) }}</a></td>
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
      </details>

    </template>
    <p v-else-if="error" class="error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.panel-compras { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #012169; }
.panel-compras h2 { margin: 0 0 14px; color: #012169; }
.ok { color: #198754; font-weight: bold; }
.error { color: #b02a37; font-weight: bold; }
.aviso { color: #7a4300; font-size: 0.85rem; margin: 6px 0 0; }
.nota { color: #666; font-size: 0.83rem; margin: 2px 0 8px; }
.vacio { color: #666; font-style: italic; margin: 4px 0; }
.gris { color: #777; }

/* Selector del compte */
.contexto { margin-bottom: 14px; }
.contexto label { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-weight: bold; color: #012169; }
.contexto select { font: inherit; font-size: 1.05rem; padding: 9px 12px; border: 2px solid #012169; border-radius: 6px; background: white; color: #012169; min-width: 320px; max-width: 100%; }

/* El compte que es mira: tot el que és seu, dins un mateix marc */
.cuenta { border: 2px solid #012169; border-radius: 10px; padding: 16px 20px; margin-bottom: 18px; background: #fbfcfe; }
.cuenta.proyecto { border-color: #2a7ab0; background: #f7fbfe; }
.titulo-cuenta { margin: 0; color: #012169; font-size: 1.3rem; }
.cuenta.proyecto .titulo-cuenta { color: #1d5f8c; }
.ayuda { color: #555; font-size: 0.9rem; margin: 4px 0 8px; }
.totales { display: flex; gap: 18px; flex-wrap: wrap; margin: 0 0 12px; font-size: 0.95rem; }
.bloque { background: #f0f4f8; border-radius: 8px; padding: 12px 16px; margin-top: 12px; }
.bloque h4 { margin: 0 0 8px; color: #012169; font-size: 1rem; }
.cabecera { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 8px; }
.cabecera h4 { margin: 0; }

/* Proveïdors */
.form-proveedor { background: white; border: 1px solid #d0d7de; border-radius: 8px; padding: 12px 15px; margin-bottom: 12px; }
.tarjetas { display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 12px; }
.tarjeta { background: white; border-radius: 8px; padding: 12px 14px; border-left: 4px solid #f0a640; display: flex; flex-direction: column; gap: 4px; }
.tarjeta.completo { border-left-color: #198754; }
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
.otros { margin: 10px 0 0; font-size: 0.85rem; color: #555; }
.otro { display: inline-flex; align-items: center; background: white; border: 1px solid #dde3ea; border-radius: 12px; padding: 0 4px 0 10px; margin: 2px 4px; }

/* Formularis */
.fila { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; margin-bottom: 8px; }
.fila label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; color: #333; }
.fila input, .fila select { padding: 8px; border: 1px solid #ccd5df; border-radius: 4px; font: inherit; background: white; }
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
.tabla td.desc { min-width: 200px; }
.tabla tr.grupo th { background: #e3eaf3; color: #012169; font-size: 0.9rem; }
.tabla.gastos { max-width: 720px; }
.tabla.gastos tr.clicable { cursor: pointer; }
.tabla.gastos tr.clicable:hover td { background: #f3f7fb; }
.tabla.gastos tr.actual td { background: #e8f1fb; font-weight: bold; }
.input-fila { width: 100%; min-width: 80px; box-sizing: border-box; padding: 5px 8px; }
.input-fila.corto { width: 80px; min-width: 0; }
.input-fila.mas { margin-top: 4px; }
.mas-fila { display: flex; gap: 4px; margin-top: 4px; }
.acciones { display: flex; gap: 6px; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.8rem; }
.btn-mini.guardar { background: #e6f4ea; color: #1e6b34; border-color: #a8d5b5; }
.btn-mini.peligro { color: #b02a37; }
.envio { background: white; border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; }
.envio summary { cursor: pointer; font-weight: bold; color: #012169; }
.envio summary .gris { font-weight: normal; font-size: 0.83rem; margin-left: 4px; }
.envio ul { margin: 8px 0 0; padding-left: 20px; font-size: 0.88rem; }
.envio li { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; padding: 3px 0; border-bottom: 1px dashed #e3e8ee; }

/* Plegables del final */
.caja { background: #f4f7f9; border-radius: 8px; padding: 12px 20px; margin-bottom: 12px; }
.plegable summary { cursor: pointer; }
.plegable summary h3 { display: inline; margin: 0; color: #012169; font-size: 1.05rem; }

@media (max-width: 768px) {
  .panel-compras { padding: 14px; }
  .cuenta { padding: 12px; }
  .bloque { padding: 10px; }
  .contexto select { min-width: 0; width: 100%; }
  .fila label, .ancho { width: 100%; min-width: 0; }
  .corto { width: calc(50% - 6px); }
  .tarjetas { grid-template-columns: 1fr; }
}
</style>
