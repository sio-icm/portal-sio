<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { limpiarHtml } from '../utils/limpiarHtml'

// Diario público: las notas del diario de actividad que un administrador ha
// aprobado para la web. El texto de cada nota se muestra en el idioma en que se
// escribió; lo que se traduce es la página.
const { locale } = useI18n()

const notas = ref([])
const cargando = ref(true)
const error = ref(false)
const proyectoActivo = ref('') // '' = todo, 'general' = sin proyecto, o id

const fondo = 'linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url(/fondeo.webp)'

onMounted(async () => {
  try {
    const r = await fetch('/api/diario')
    if (!r.ok) throw new Error(r.status)
    notas.value = await r.json()
  } catch {
    error.value = true
  } finally {
    cargando.value = false
  }
})

// Proyectos que tienen alguna nota publicada, para filtrar
const proyectos = computed(() => {
  const vistos = new Map()
  for (const n of notas.value) if (n.proyecto_id !== null) vistos.set(n.proyecto_id, n.proyecto_titulo)
  return [...vistos].map(([id, titulo]) => ({ id, titulo }))
})
const hayGenerales = computed(() => notas.value.some(n => n.proyecto_id === null))

const notasVisibles = computed(() => notas.value.filter(n => {
  if (!proyectoActivo.value) return true
  if (proyectoActivo.value === 'general') return n.proyecto_id === null
  return n.proyecto_id === proyectoActivo.value
}))

const formatoFecha = (iso) => {
  const [a, m, d] = iso.split('-').map(Number)
  return new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(a, m - 1, d))
}
</script>

<template>
  <div class="diario-page">
    <div class="fondo" :style="{ backgroundImage: fondo }"></div>

    <div class="contenedor-ancho contenido">
      <h1 class="titulo-seccion">{{ $t('diario.titulo') }}</h1>
      <p class="subtitulo">{{ $t('diario.subtitulo') }}</p>

      <div class="panel">
        <div v-if="proyectos.length + (hayGenerales ? 1 : 0) > 1" class="filtros" role="group">
          <button type="button" :class="{ activo: proyectoActivo === '' }" @click="proyectoActivo = ''">{{ $t('diario.todos') }}</button>
          <button v-for="p in proyectos" :key="p.id" type="button" :class="{ activo: proyectoActivo === p.id }" @click="proyectoActivo = p.id">{{ p.titulo }}</button>
          <button v-if="hayGenerales" type="button" :class="{ activo: proyectoActivo === 'general' }" @click="proyectoActivo = 'general'">{{ $t('diario.general') }}</button>
        </div>

        <p v-if="cargando" class="aviso">{{ $t('diario.cargando') }}</p>
        <p v-else-if="error" class="aviso">{{ $t('diario.error') }}</p>
        <p v-else-if="notas.length === 0" class="aviso">{{ $t('diario.vacio') }}</p>

        <ol v-else class="linea-tiempo">
          <li v-for="n in notasVisibles" :key="n.id" class="entrada">
            <div class="marca" aria-hidden="true"></div>
            <p class="meta">
              <time :datetime="n.fecha">{{ formatoFecha(n.fecha) }}</time>
              <span class="tipo">{{ $t(`diario.tipos.${n.tipo}`) }}</span>
              <span class="proyecto">{{ n.proyecto_titulo || $t('diario.general') }}</span>
            </p>
            <h2>{{ n.titulo }}</h2>
            <div v-if="n.texto" class="texto" v-html="limpiarHtml(n.texto)"></div>
            <div v-if="n.fotos.length" class="fotos">
              <a v-for="f in n.fotos" :key="f" :href="`/api/fotos/${f}`" target="_blank" rel="noopener" :title="$t('diario.ampliar')">
                <img :src="`/api/fotos/${f}?mini=1`" :alt="n.titulo" loading="lazy">
              </a>
            </div>
            <p class="autor">{{ $t('diario.por', { autor: n.autor }) }}</p>
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>

<style scoped>
.diario-page { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo { position: absolute; top: 0; left: 0; width: 100%; height: 480px; background-size: cover; background-position: center; z-index: 0; }
.contenido { position: relative; z-index: 10; padding-top: 120px; }
.titulo-seccion { color: white; font-size: 2.2rem; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; margin-bottom: 15px; border-bottom: none; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 35px; max-width: 800px; }
.panel { background: white; border-radius: 12px; padding: 30px 35px; box-shadow: 0 10px 30px rgba(0,0,0,0.12); }
.filtros { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 25px; }
.filtros button { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 16px; padding: 6px 14px; cursor: pointer; font: inherit; font-size: 0.9rem; color: #012169; }
.filtros button.activo { background: #012169; color: white; border-color: #012169; }
.aviso { color: #666; font-style: italic; text-align: center; padding: 30px 0; }
.linea-tiempo { list-style: none; margin: 0; padding: 0 0 0 28px; border-left: 3px solid #d6e4f0; }
.entrada { position: relative; padding: 0 0 35px 10px; }
.marca { position: absolute; left: -38px; top: 4px; width: 15px; height: 15px; border-radius: 50%; background: #0086c0; border: 3px solid white; box-shadow: 0 0 0 2px #0086c0; }
.meta { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin: 0 0 6px; font-size: 0.85rem; }
.meta time { font-weight: bold; color: #012169; }
.tipo { background: #e8f4fd; color: #0086c0; border-radius: 10px; padding: 2px 10px; font-size: 0.78rem; font-weight: bold; }
.proyecto { color: #666; }
.entrada h2 { font-size: 1.25rem; color: #222; margin: 4px 0 8px; }
.texto { color: #333; line-height: 1.65; }
.fotos { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; margin-top: 14px; }
.fotos img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-radius: 6px; display: block; transition: transform 0.2s; }
.fotos a:hover img { transform: scale(1.02); }
.autor { margin: 10px 0 0; color: #888; font-size: 0.85rem; font-style: italic; }
@media (max-width: 768px) {
  .panel { padding: 20px 18px; }
  .linea-tiempo { padding-left: 18px; }
  .marca { left: -28px; }
}
</style>
