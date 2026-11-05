<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
const fondoInstrumentacion = '/instrumentacion.webp'

// Memoria anual: las cifras salen solas del diario de actividad y del
// calendario de equipo (/api/memoria, solo cifras globales) y las actividades
// destacadas son las notas aprobadas para la web (/api/diario).
const { t, locale } = useI18n()

// PDF de la memoria completa por año (dentro de public/). Si no hay, no se
// muestra el recuadro de descarga. Ejemplo: { 2025: '/memorias/Memoria_SIO_2025.pdf' }
const pdfsMemoria = {}

const anio = ref(new Date().getFullYear())
const datos = ref(null)
const destacadas = ref([])
const cargando = ref(true)
const error = ref(false)
let todasPublicas = []

const cargar = async () => {
  cargando.value = true
  error.value = false
  try {
    const r = await fetch(`/api/memoria?anio=${anio.value}`)
    if (!r.ok) throw new Error()
    datos.value = await r.json()
  } catch {
    error.value = true
  } finally {
    cargando.value = false
  }
  destacadas.value = todasPublicas.filter(n => n.fecha.startsWith(String(anio.value))).slice(0, 6)
}
const elegirAnio = (a) => { anio.value = a; cargar() }

onMounted(async () => {
  try {
    const r = await fetch('/api/diario?limite=200')
    if (r.ok) todasPublicas = await r.json()
  } catch { /* sin destacadas */ }
  cargar()
})

// Tarjetas de cifras: solo las que tienen valor
const metricas = computed(() => {
  const d = datos.value
  if (!d) return []
  const h = d.horas_sin_proyecto
  return [
    { clave: 'actividades', valor: d.actividades },
    { clave: 'proyectos', valor: d.proyectos },
    { clave: 'diasCampanya', valor: d.dias_campanya },
    { clave: 'diasPelagia', valor: d.dias_pelagia },
    { clave: 'diasTanque', valor: d.dias_tanque },
    { clave: 'prestamos', valor: d.prestamos },
    { clave: 'horasSoporte', valor: h.max ? (h.min === h.max ? `${h.max} h` : `${h.min}–${h.max} h`) : 0, nota: d.encargos_sin_proyecto }
  ].filter(m => m.valor)
})

// Actividades por tipo, de más a menos, con barra proporcional
const ORDEN_TIPOS = ['campanya', 'desenvolupament', 'manteniment', 'calibratge', 'divulgacio', 'formacio', 'gestio', 'altres']
const COLORES = { campanya: '#0086c0', desenvolupament: '#6f42c1', manteniment: '#fd7e14', calibratge: '#20a39e', divulgacio: '#d63384', formacio: '#198754', gestio: '#6c757d', altres: '#495057' }
const tipos = computed(() => {
  const pt = datos.value?.por_tipo || {}
  const max = Math.max(1, ...Object.values(pt))
  return ORDEN_TIPOS.filter(k => pt[k]).map(k => ({ clave: k, total: pt[k], ancho: `${Math.round(pt[k] / max * 100)}%`, color: COLORES[k] }))
    .sort((a, b) => b.total - a.total)
})

const fechaLocal = (iso) => {
  const [a, m, d] = iso.split('-').map(Number)
  return new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long' }).format(new Date(a, m - 1, d))
}
const textoPlano = (html) => {
  const div = document.createElement('div')
  div.innerHTML = html || ''
  const texto = (div.textContent || '').trim()
  return texto.length > 140 ? texto.slice(0, 140) + '…' : texto
}

const backgroundStyle = computed(() => `linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('${fondoInstrumentacion}')`)
</script>

<template>
  <div class="memoria-page">
    <div class="fondo-cabecera" :style="{ backgroundImage: backgroundStyle }"></div>

    <div class="contenedor-ancho contenido-pagina">
      <h1 class="titulo-seccion">{{ $t('memoria.titulo') }}</h1>
      <p class="subtitulo">{{ $t('memoria.subtitulo') }}</p>

      <div class="bloque-blanco">
        <div class="cabecera-bloque">
          <h2>{{ $t('memoria.resumen', { anio }) }}</h2>
          <div v-if="datos && datos.anios.length > 1" class="anios" role="group" :aria-label="$t('memoria.elegirAnio')">
            <button v-for="a in datos.anios" :key="a" type="button" :class="{ activo: a === anio }" :aria-pressed="a === anio" @click="elegirAnio(a)">{{ a }}</button>
          </div>
        </div>
        <p class="intro-memoria">{{ $t('memoria.intro') }}</p>

        <p v-if="cargando" class="estado">{{ $t('memoria.cargando') }}</p>
        <p v-else-if="error" class="estado">{{ $t('memoria.error') }}</p>
        <template v-else>
          <p v-if="!metricas.length" class="estado">{{ $t('memoria.sinDatos') }}</p>
          <div v-else class="grid-metricas">
            <div v-for="m in metricas" :key="m.clave" class="tarjeta-metrica">
              <span class="numero">{{ m.valor }}</span>
              <span class="etiqueta">{{ $t(`memoria.metricas.${m.clave}`) }}</span>
              <span v-if="m.nota" class="nota-metrica">{{ $t('memoria.encargos', { n: m.nota }, m.nota) }}</span>
            </div>
          </div>

          <section v-if="tipos.length" class="seccion">
            <h3>{{ $t('memoria.porTipo') }}</h3>
            <ul class="barras">
              <li v-for="tp in tipos" :key="tp.clave">
                <span class="barra-etiqueta">{{ $t(`memoria.tipos.${tp.clave}`) }}</span>
                <span class="barra-fondo"><span class="barra" :style="{ width: tp.ancho, background: tp.color }"></span></span>
                <span class="barra-total">{{ tp.total }}</span>
              </li>
            </ul>
          </section>

          <section v-if="destacadas.length" class="seccion">
            <h3>{{ $t('memoria.destacadas') }}</h3>
            <div class="grid-destacadas">
              <router-link v-for="n in destacadas" :key="n.id" to="/diario" class="destacada">
                <img v-if="n.fotos && n.fotos.length" :src="`/api/fotos/${n.fotos[0]}?mini=1`" alt="" loading="lazy">
                <div class="destacada-texto">
                  <span class="destacada-fecha">{{ fechaLocal(n.fecha) }}</span>
                  <strong>{{ n.titulo }}</strong>
                  <span v-if="!(n.fotos && n.fotos.length) && n.texto" class="destacada-resumen">{{ textoPlano(n.texto) }}</span>
                </div>
              </router-link>
            </div>
            <router-link to="/diario" class="ver-diario">{{ $t('memoria.verDiario') }} →</router-link>
          </section>
        </template>

        <div v-if="pdfsMemoria[anio]" class="caja-descarga">
          <div class="icono-doc">📄</div>
          <div>
            <h3>{{ $t('memoria.completa', { anio }) }}</h3>
            <p>{{ $t('memoria.completaTexto') }}</p>
          </div>
          <a :href="pdfsMemoria[anio]" class="btn-descarga" download>{{ $t('memoria.descargar') }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.memoria-page { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-cabecera { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-size: cover; background-position: center; z-index: 0; }
.contenido-pagina { position: relative; z-index: 10; padding-top: 120px; }
.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 40px; max-width: 800px; }

.bloque-blanco { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-top: 4px solid #dc3545; }
.cabecera-bloque { display: flex; justify-content: space-between; align-items: center; gap: 15px; flex-wrap: wrap; border-bottom: 2px solid #eee; padding-bottom: 10px; }
.bloque-blanco h2 { color: #012169; margin: 0; font-size: 1.8rem; }
.anios { display: flex; gap: 6px; flex-wrap: wrap; }
.anios button { background: #f4f7f9; border: 1px solid #d0d7de; border-radius: 15px; padding: 5px 14px; cursor: pointer; font: inherit; color: #012169; }
.anios button.activo { background: #012169; color: white; border-color: #012169; font-weight: bold; }
.intro-memoria { color: #555; font-size: 1.05rem; line-height: 1.6; margin: 20px 0 30px; }
.estado { color: #666; font-style: italic; }

.grid-metricas { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 20px; margin-bottom: 35px; }
.tarjeta-metrica { background: #f8f9fa; padding: 25px 15px; border-radius: 8px; text-align: center; border: 1px solid #e9ecef; display: flex; flex-direction: column; align-items: center; }
.numero { display: block; font-size: 2.4rem; font-weight: bold; color: #dc3545; margin-bottom: 5px; }
.etiqueta { font-size: 0.9rem; color: #666; font-weight: bold; text-transform: uppercase; }
.nota-metrica { font-size: 0.8rem; color: #888; margin-top: 4px; }

.seccion { margin-bottom: 35px; }
.seccion h3 { color: #012169; margin: 0 0 15px; font-size: 1.25rem; }
.barras { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.barras li { display: grid; grid-template-columns: 170px 1fr 40px; align-items: center; gap: 12px; }
.barra-etiqueta { color: #444; font-size: 0.95rem; }
.barra-fondo { background: #eef1f4; border-radius: 4px; height: 14px; overflow: hidden; }
.barra { display: block; height: 100%; border-radius: 4px; }
.barra-total { font-weight: bold; color: #012169; text-align: right; }

.grid-destacadas { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 16px; }
.destacada { display: flex; flex-direction: column; border: 1px solid #e3e8ee; border-radius: 8px; overflow: hidden; text-decoration: none; color: #333; background: white; transition: box-shadow 0.2s; }
.destacada:hover { box-shadow: 0 6px 18px rgba(0,0,0,0.1); }
.destacada img { width: 100%; height: 140px; object-fit: cover; }
.destacada-texto { padding: 12px; display: flex; flex-direction: column; gap: 4px; }
.destacada-fecha { font-size: 0.8rem; color: #0086c0; font-weight: bold; }
.destacada-resumen { font-size: 0.88rem; color: #555; }
.ver-diario { display: inline-block; margin-top: 12px; color: #0086c0; font-weight: bold; text-decoration: none; }

.caja-descarga { display: flex; align-items: center; gap: 20px; background: #eaf2f8; padding: 25px; border-radius: 8px; border-left: 4px solid #0086c0; }
.icono-doc { font-size: 3rem; }
.caja-descarga h3 { margin: 0 0 5px 0; color: #012169; }
.caja-descarga p { margin: 0; color: #555; font-size: 0.95rem; }
.btn-descarga { margin-left: auto; background-color: #0086c0; color: white; padding: 12px 25px; border-radius: 6px; text-decoration: none; font-weight: bold; transition: background 0.3s; white-space: nowrap; }
.btn-descarga:hover { background-color: #012169; }

@media (max-width: 768px) {
  .contenido-pagina { padding-top: 150px; }
  .bloque-blanco { padding: 22px 16px; }
  .bloque-blanco h2 { font-size: 1.4rem; }
  .barras li { grid-template-columns: 110px 1fr 32px; gap: 8px; }
  .caja-descarga { flex-direction: column; text-align: center; }
  .btn-descarga { margin-left: 0; margin-top: 15px; width: 100%; text-align: center; }
}
</style>
