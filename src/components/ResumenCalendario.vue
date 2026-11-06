<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { peticionIntranet, hoyIso } from '../utils/diario'
import {
  tipoCalendario, recurso, nombreReserva, ICONOS_AVISO,
  lunesDe, sumarDias, deIso, fechaLarga, fechaBreve, rangoTexto, resumenDia, nombreCorto, textoAviso
} from '../utils/calendario'

// Resum del calendari d'equip a la pantalla principal de la intranet: com es
// presenta el dia, la setmana i el mes. Amb «✓ Vist» es plega fins l'endemà o
// fins que aparegui un avís nou.
const props = defineProps({ sesion: { type: Object, required: true } })
const emit = defineEmits(['sesion-caducada', 'abrir'])
const { t } = useI18n()

const hoy = hoyIso()
const lunes = lunesDe(hoy)
const DIAS_MES = 30
// Els avisos es miren amb més antelació: 12 setmanes
const DIAS_AVISOS = 84
const desde = lunes < hoy ? lunes : hoy
const hasta = sumarDias(hoy, DIAS_AVISOS)

const datos = ref(null)
const error = ref(false)
const pestana = ref('avui')

onMounted(async () => {
  try {
    const r = await peticionIntranet(`/api/calendario?desde=${desde}&hasta=${hasta}`, {}, () => emit('sesion-caducada'))
    if (!r.ok) throw new Error()
    datos.value = await r.json()
  } catch {
    error.value = true
  }
})

const corto = (nombre) => nombreCorto(nombre, datos.value?.equipo || [])
const dia = computed(() => datos.value && resumenDia(datos.value, hoy))
const semana = computed(() => datos.value && Array.from({ length: 7 }, (_, i) => resumenDia(datos.value, sumarDias(lunes, i)))
  .filter(d => d.laborable || d.entradas.length || d.reservas.length))
const avisosPendientes = computed(() => (datos.value?.avisos || []).filter(a => (a.fin || a.fecha) >= hoy))
// Pròxims 30 dies: el que comença (o ja ha començat) a partir d'avui
const proximos = computed(() => {
  if (!datos.value) return []
  const limite = sumarDias(hoy, DIAS_MES)
  const enMes = (x) => x.fin >= hoy && x.inicio <= limite
  const entradas = datos.value.entradas.filter(enMes).map(e => ({ clase: 'entrada', ...e }))
  const reservas = datos.value.reservas.filter(enMes).map(r => ({ clase: 'reserva', ...r }))
  return [...entradas, ...reservas].sort((a, b) => a.inicio.localeCompare(b.inicio))
})

// Avisos agrupats per setmanes, per veure amb temps quina setmana hi haurà problemes.
// Els dies amb poc personal d'una mateixa setmana surten junts en una línia.
const avisosPorSemana = computed(() => {
  const lunesHoy = lunesDe(hoy)
  const semanas = new Map()
  for (const a of avisosPendientes.value) {
    const lunes = lunesDe(a.fecha < hoy ? hoy : a.fecha)
    if (!semanas.has(lunes)) semanas.set(lunes, [])
    semanas.get(lunes).push(a)
  }
  return [...semanas.entries()].sort(([x], [y]) => x.localeCompare(y)).map(([lunes, avisos]) => {
    const n = Math.round((deIso(lunes) - deIso(lunesHoy)) / (7 * 86400000))
    const titulo = n === 0 ? t('intranet.resumen.estaSemana') : n === 1 ? t('intranet.resumen.semanaQueViene')
      : t('intranet.resumen.semanaDel', { fecha: fechaBreve(lunes), n })
    const personal = avisos.filter(a => a.tipo === 'personal')
    const resto = avisos.filter(a => a.tipo !== 'personal').map(a => ({
      ids: [a.id], icono: ICONOS_AVISO[a.tipo], cuando: rangoTexto(a.fecha, a.fin || a.fecha), texto: textoAviso(a)
    }))
    if (personal.length) {
      const dias = personal.map(a => a.datos
        ? `${fechaBreve(a.fecha)} (${t('intranet.comun.deTotal', { n: a.datos.presentes, total: a.datos.total })})`
        : fechaBreve(a.fecha))
      resto.unshift({ ids: personal.map(a => a.id), icono: ICONOS_AVISO.personal, cuando: '', texto: t('intranet.avisos.pocPersonal', { dias: dias.join(', ') }) })
    }
    return { lunes, titulo, urgente: n <= 1, items: resto }
  })
})
const esNuevo = (item) => !!visto.value.fecha && item.ids.some(id => !(visto.value.avisos || []).includes(id))

// ---------- «✓ Vist» ----------
// Es recorda al navegador per a cada usuari: el dia i els avisos que ja s'han vist
const CLAVE = `sio_resum_vist_${props.sesion.usuario_id ?? 'admin'}`
const leerVisto = () => { try { return JSON.parse(localStorage.getItem(CLAVE)) || {} } catch { return {} } }
const visto = ref(leerVisto())
const plegado = computed(() => visto.value.fecha === hoy &&
  avisosPendientes.value.every(a => (visto.value.avisos || []).includes(a.id)))
const marcarVisto = () => {
  visto.value = { fecha: hoy, avisos: avisosPendientes.value.map(a => a.id) }
  try { localStorage.setItem(CLAVE, JSON.stringify(visto.value)) } catch { /* sense emmagatzematge: només per a aquesta visita */ }
}
const mostrar = () => { visto.value = {} ; try { localStorage.removeItem(CLAVE) } catch { /* res */ } }

const etiquetaEntrada = (e) => `${tipoCalendario(e.tipo).icono} ${e.persona ? corto(e.persona) : t('intranet.comun.todoEquipo')}`
</script>

<template>
  <section v-if="datos && dia" class="resumen" :class="{ plegado, 'con-avisos': avisosPendientes.length }" :aria-label="$t('intranet.resumen.aria')">
    <!-- Plegat: una sola línia -->
    <div v-if="plegado" class="linea">
      <span>🗓️ <b>{{ $t('intranet.comun.hoy') }}</b>
        <template v-if="dia.laborable && dia.plantilla.length"> · {{ $t('intranet.resumen.alCentro', { n: dia.presentes.length, total: dia.plantilla.length }) }}</template>
        <template v-else-if="dia.festiu"> · {{ $t('intranet.comun.festivo') }}: {{ dia.festiu }}</template>
        <template v-if="avisosPendientes.length"> · {{ $t('intranet.resumen.avisosVistos', { n: avisosPendientes.length }, avisosPendientes.length) }}</template>
      </span>
      <button type="button" class="btn-enlace" @click="mostrar">{{ $t('intranet.resumen.mostrar') }}</button>
    </div>

    <template v-else>
      <div class="cabecera">
        <h3>🗓️ {{ fechaLarga(hoy) }}</h3>
        <div class="pestanas" role="tablist">
          <button v-for="[valor, texto] in [['avui', $t('intranet.comun.hoy')], ['setmana', $t('intranet.comun.semana')], ['mes', $t('intranet.comun.mes')]]" :key="valor"
            type="button" role="tab" :aria-selected="pestana === valor" :class="{ activa: pestana === valor }"
            @click="pestana = valor">{{ texto }}</button>
        </div>
      </div>

      <!-- Avisos de les pròximes 12 setmanes, per setmanes: sempre a dalt, sigui quina sigui la pestanya -->
      <div v-if="avisosPorSemana.length" class="avisos" role="status">
        <p class="avisos-titulo">{{ $t('intranet.resumen.problemas', { n: DIAS_AVISOS / 7 }) }}</p>
        <div v-for="s in avisosPorSemana" :key="s.lunes" class="semana-avisos" :class="{ urgente: s.urgente }">
          <p class="semana-titulo">{{ s.titulo }}</p>
          <p v-for="it in s.items" :key="it.ids[0]" class="aviso" :class="{ nuevo: esNuevo(it) }" :data-nuevo="$t('intranet.resumen.nuevo')">
            {{ it.icono }} <b v-if="it.cuando">{{ it.cuando }}</b><template v-if="it.cuando"> · </template>{{ it.texto }}
          </p>
        </div>
      </div>

      <!-- AVUI -->
      <div v-if="pestana === 'avui'" class="contenido" role="tabpanel">
        <p v-if="dia.festiu" class="festiu">🎉 {{ $t('intranet.comun.festivo') }}: {{ dia.festiu }}</p>
        <p v-else-if="!dia.laborable" class="festiu">{{ $t('intranet.comun.finDeSemana') }}</p>
        <p v-if="dia.laborable && dia.plantilla.length" class="presentes">
          👥 {{ $t('intranet.comun.alCentro') }}: <b>{{ $t('intranet.comun.deTotal', { n: dia.presentes.length, total: dia.plantilla.length }) }}</b>
          <span v-if="dia.presentes.length"> ({{ dia.presentes.map(u => corto(u.nombre)).join(', ') }})</span>
        </p>
        <ul v-if="dia.entradas.length || dia.reservas.length" class="lista">
          <li v-for="e in dia.entradas" :key="'e' + e.id">
            <span class="tag" :style="{ background: tipoCalendario(e.tipo).color }">{{ tipoCalendario(e.tipo).icono }} {{ tipoCalendario(e.tipo).etiqueta }}</span>
            {{ e.persona || $t('intranet.comun.todoEquipo') }}<span v-if="e.fin !== hoy" class="gris"> · {{ $t('intranet.comun.hasta', { fecha: fechaBreve(e.fin) }) }}</span><span v-if="e.nota" class="gris"> · {{ e.nota }}</span><span v-if="e.proyecto" class="gris"> · 📁 {{ e.proyecto }}</span>
          </li>
          <li v-for="r in dia.reservas" :key="'r' + r.id">
            <span class="tag reserva">{{ recurso(r.recurso).icono }} {{ nombreReserva(r) }}</span>
            {{ r.persona || r.para }}<span v-if="r.proposito" class="gris"> · {{ r.proposito }}</span>
          </li>
        </ul>
        <p v-else-if="dia.laborable" class="gris">{{ $t('intranet.resumen.todosEnCentro') }}</p>
      </div>

      <!-- SETMANA -->
      <div v-else-if="pestana === 'setmana'" class="contenido" role="tabpanel">
        <table class="semana">
          <tbody>
            <tr v-for="d in semana" :key="d.dia" :class="{ hoy: d.dia === hoy, pasado: d.dia < hoy, alerta: d.avisos.length }">
              <th scope="row">{{ fechaBreve(d.dia) }}</th>
              <td class="num">
                <template v-if="d.laborable && d.plantilla.length">👥 {{ d.presentes.length }}/{{ d.plantilla.length }}</template>
                <template v-else-if="d.festiu">🎉</template>
              </td>
              <td>
                <span v-if="d.festiu" class="gris">{{ d.festiu }} </span>
                <span v-for="e in d.entradas" :key="'e' + e.id" class="mini" :style="{ borderColor: tipoCalendario(e.tipo).color }" :title="tipoCalendario(e.tipo).etiqueta">{{ etiquetaEntrada(e) }}</span>
                <span v-for="r in d.reservas" :key="'r' + r.id" class="mini reserva">{{ recurso(r.recurso).icono }} {{ nombreReserva(r) }}</span>
                <span v-if="d.avisos.length" :aria-label="$t('intranet.comun.aviso')">⚠️</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- MES -->
      <div v-else class="contenido" role="tabpanel">
        <p v-if="!proximos.length" class="gris">{{ $t('intranet.resumen.nadaProximo', { n: DIAS_MES }) }}</p>
        <ul v-if="proximos.length" class="lista">
          <li v-for="x in proximos.slice(0, 12)" :key="x.clase + x.id">
            <span class="fecha">{{ rangoTexto(x.inicio, x.fin) }}</span>
            <template v-if="x.clase === 'entrada'">
              <span class="tag" :style="{ background: tipoCalendario(x.tipo).color }">{{ tipoCalendario(x.tipo).icono }} {{ tipoCalendario(x.tipo).etiqueta }}</span>
              {{ x.persona || $t('intranet.comun.todoEquipo') }}
            </template>
            <template v-else>
              <span class="tag reserva">{{ recurso(x.recurso).icono }} {{ nombreReserva(x) }}</span>
              {{ x.persona || x.para }}
            </template>
          </li>
        </ul>
        <p v-if="proximos.length > 12" class="gris">{{ $t('intranet.resumen.masEnCalendario', { n: proximos.length - 12 }) }}</p>
      </div>

      <div class="pie">
        <button type="button" class="btn-secundario" @click="emit('abrir')">{{ $t('intranet.resumen.abrir') }}</button>
        <button type="button" class="btn-visto" @click="marcarVisto">{{ $t('intranet.resumen.visto') }}</button>
      </div>
    </template>
  </section>
  <p v-else-if="error" class="error-resumen">{{ $t('intranet.resumen.errorCarga') }}</p>
</template>

<style scoped>
.resumen { background: white; border-radius: 10px; padding: 18px 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 5px solid #0086c0; margin-bottom: 20px; }
.resumen.con-avisos { border-left-color: #f0a640; }
.resumen.plegado { padding: 10px 18px; }
.linea { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; color: #333; font-size: 0.92rem; }
.btn-enlace { background: none; border: none; color: #0086c0; cursor: pointer; font: inherit; text-decoration: underline; padding: 0; }
.cabecera { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
h3 { margin: 0; color: #012169; }
h3::first-letter { text-transform: uppercase; }
.pestanas { display: flex; border: 1px solid #c9d3dd; border-radius: 6px; overflow: hidden; }
.pestanas button { background: white; border: none; padding: 6px 14px; cursor: pointer; font: inherit; font-size: 0.88rem; color: #012169; }
.pestanas button + button { border-left: 1px solid #c9d3dd; }
.pestanas button.activa { background: #012169; color: white; font-weight: bold; }
.contenido { font-size: 0.92rem; color: #333; }
.festiu { color: #b02a37; margin: 0 0 6px; }
.presentes { margin: 0 0 8px; }
.aviso { background: #fff4e5; border-left: 3px solid #f0a640; padding: 6px 10px; margin: 6px 0; color: #7a4300; }
.aviso.nuevo::after { content: attr(data-nuevo); background: #f0a640; color: white; border-radius: 8px; padding: 0 6px; margin-left: 8px; font-size: 0.72rem; font-weight: bold; }
.avisos { margin-bottom: 8px; }
.avisos-titulo { margin: 0 0 4px; font-weight: bold; color: #7a4300; font-size: 0.9rem; }
.semana-avisos { margin: 6px 0 8px; }
.semana-titulo { margin: 0; font-size: 0.8rem; font-weight: bold; color: #666; text-transform: uppercase; letter-spacing: 0.03em; }
.semana-avisos.urgente .semana-titulo { color: #b02a37; }
.gris { color: #666; }
.lista { list-style: none; padding: 0; margin: 6px 0 0; }
.lista li { padding: 5px 0; border-bottom: 1px solid #eef1f4; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.fecha { color: #555; font-size: 0.85rem; min-width: 150px; }
.tag { color: white; border-radius: 10px; padding: 1px 8px; font-size: 0.78rem; }
.tag.reserva { background: #012169; }
.semana { width: 100%; border-collapse: collapse; }
.semana th, .semana td { padding: 6px 6px; border-bottom: 1px solid #eef1f4; text-align: left; vertical-align: top; }
.semana th { font-weight: bold; color: #012169; white-space: nowrap; width: 1%; }
.semana .num { white-space: nowrap; width: 1%; color: #444; }
.semana tr.hoy th { color: #0086c0; }
.semana tr.pasado { opacity: 0.55; }
.semana tr.alerta td, .semana tr.alerta th { background: #fffaf2; }
.mini { display: inline-block; border: 1px solid; border-left-width: 4px; border-radius: 4px; padding: 0 6px; margin: 1px 4px 1px 0; font-size: 0.8rem; }
.mini.reserva { border-color: #012169; }
.pie { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }
.btn-secundario { background: #f4f7f9; color: #012169; border: 1px solid #c9d3dd; padding: 7px 14px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-visto { background: #8cc63f; color: #012169; border: none; padding: 7px 16px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.error-resumen { color: #b02a37; }
@media (max-width: 768px) {
  .resumen { padding: 14px; }
  .fecha { min-width: 0; width: 100%; }
}
</style>
