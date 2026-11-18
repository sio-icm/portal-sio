<script setup>
import {
  tipoCalendario, recurso, nombreReserva, ICONOS_AVISO,
  fechaLarga, rangoTexto, horario, nombreCorto, textoAviso
} from '../utils/calendario'

// Detall d'un dia del calendari d'equip: festiu, qui és al centre, avisos, entrades i
// reserves. Es fa servir a la finestra que s'obre en clicar un dia i a sota del calendari.
defineProps({
  detalle: { type: Object, required: true }, // resumenDia(...) de utils/calendario
  equipo: { type: Array, default: () => [] },
  titulo: { type: Boolean, default: true }
})
defineEmits(['editar', 'borrar'])
</script>

<template>
  <div class="detalle-dia">
    <h3 v-if="titulo">{{ fechaLarga(detalle.dia) }}</h3>
    <p v-if="detalle.festiu" class="festiu-texto">🎉 {{ $t('intranet.comun.festivo') }}: {{ detalle.festiu }}</p>
    <p v-else-if="!detalle.laborable" class="festiu-texto">{{ $t('intranet.comun.finDeSemana') }}</p>
    <p v-if="detalle.laborable && detalle.plantilla.length" class="presentes">
      👥 {{ $t('intranet.comun.alCentro') }}: <b>{{ $t('intranet.comun.deTotal', { n: detalle.presentes.length, total: detalle.plantilla.length }) }}</b>
      <span v-if="detalle.presentes.length"> ({{ detalle.presentes.map(u => nombreCorto(u.nombre, equipo)).join(', ') }})</span>
    </p>
    <p v-for="a in detalle.avisos" :key="a.id" class="aviso">{{ ICONOS_AVISO[a.tipo] }} {{ textoAviso(a) }}</p>

    <p v-if="!detalle.entradas.length && !detalle.reservas.length" class="vacio">{{ $t('intranet.calendario.nadaApuntado') }}</p>
    <ul class="lista">
      <li v-for="e in detalle.entradas" :key="'e' + e.id">
        <span class="tag" :style="{ background: tipoCalendario(e.tipo).color }">{{ tipoCalendario(e.tipo).icono }} {{ tipoCalendario(e.tipo).etiqueta }}</span>
        <b>{{ e.persona || $t('intranet.comun.todoEquipo') }}</b>
        <span class="rango">{{ rangoTexto(e.inicio, e.fin) }}</span>
        <span v-if="horario(e)" class="rango">🕘 {{ horario(e) }}</span>
        <span v-if="e.nota" class="nota">· {{ e.nota }}</span>
        <span v-if="e.proyecto" class="nota">· 📁 {{ e.proyecto }}</span>
        <span v-if="e.editable" class="acciones">
          <button class="btn-mini" @click="$emit('editar', 'entrada', e)" :aria-label="$t('intranet.comun.editar')">✏️</button>
          <button class="btn-mini peligro" @click="$emit('borrar', 'entrada', e)" :aria-label="$t('intranet.calendario.borrarAria')">🗑️</button>
        </span>
      </li>
      <li v-for="x in detalle.reservas" :key="'r' + x.id">
        <span class="tag reserva">{{ recurso(x.recurso).icono }} {{ nombreReserva(x) }}</span>
        <b>{{ x.persona || x.para }}</b><span v-if="x.persona && x.para"> → {{ x.para }}</span>
        <span class="rango">{{ rangoTexto(x.inicio, x.fin) }}</span>
        <span v-if="x.proposito" class="nota">· {{ x.proposito }}</span>
        <span v-if="x.editable" class="acciones">
          <button class="btn-mini" @click="$emit('editar', 'reserva', x)" :aria-label="$t('intranet.comun.editar')">✏️</button>
          <button class="btn-mini peligro" @click="$emit('borrar', 'reserva', x)" :aria-label="$t('intranet.calendario.borrarAria')">🗑️</button>
        </span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
h3 { margin: 0 0 10px; color: #012169; }
h3::first-letter { text-transform: uppercase; }
.festiu-texto { color: #b02a37; margin: 0 0 6px; }
.presentes { margin: 0 0 6px; color: #333; }
.aviso { background: #fff4e5; border-left: 3px solid #f0a640; padding: 6px 10px; margin: 6px 0; color: #7a4300; }
.vacio { color: #666; font-style: italic; }
.lista { list-style: none; padding: 0; margin: 8px 0 0; }
.lista li { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; padding: 8px 0; border-bottom: 1px solid #e3e8ee; font-size: 0.92rem; }
.tag { color: white; border-radius: 10px; padding: 2px 9px; font-size: 0.78rem; }
.tag.reserva { background: #012169; }
.rango { color: #555; font-size: 0.85rem; }
.nota { color: #555; }
.acciones { margin-left: auto; display: flex; gap: 4px; }
.btn-mini { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.8rem; }
.btn-mini.peligro { color: #b02a37; }
</style>
