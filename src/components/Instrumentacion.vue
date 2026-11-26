<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { limpiarHtml } from '../utils/limpiarHtml'
import { useSolicitud } from '../composables/useSolicitud'
import DatosSolicitante from './DatosSolicitante.vue'
import EstadoSolicitud from './EstadoSolicitud.vue'

const { t, tm, rt, locale } = useI18n()

const apiUrl = '/api/instrumentos'
const emit = defineEmits(['volver'])

// --- ESTATS I DADES ---
const cargando = ref(true)
const errorCarga = ref(false)
const instrumentos = ref([])
const categoriaActiva = ref('Física')
const instrumentoExpandido = ref(null)
const equipoSeleccionado = ref(null)
const diasSeleccionados = ref([])
const institucionInvestigador = ref('')
const { nombre, email, web, estado, error, enviar } = useSolicitud('instrumento')

// --- CÀRREGA DE DADES ---
const cargarDatos = async () => {
  try {
    const respuesta = await fetch(apiUrl)
    if (!respuesta.ok) throw new Error('Error')
    const datosJson = await respuesta.json()
    
    instrumentos.value = datosJson.map(fila => ({
      id: fila.id,
      tipo: fila.categoria || 'General',
      subcategoria: fila.subcategoria || '',
      nombre: fila.nombre,
      marca: fila.marca || '',
      estado: fila.estado || 'Disponible',
      prestadoHasta: fila.prestado_hasta || null,
      ultimaCalibracion: fila.ultima_calibracion || '',
      descripcionCompleta: fila.descripcion || '',
      parametros: fila.parametros_tecnicos || '',
      numeroSerie: fila.numero_serie || ''
    }))
    cargando.value = false
    // ?i=<id> (des de la cerca): obrir aquell instrument
    const id = Number(new URLSearchParams(window.location.search).get('i'))
    const inst = id && instrumentos.value.find(x => x.id === id)
    if (inst) { categoriaActiva.value = inst.tipo; verDetalles(inst) }
  } catch (error) {
    console.error("Error carregant:", error)
    errorCarga.value = true
    cargando.value = false
  }
}

onMounted(() => cargarDatos())

// --- LÒGICA NAVEGACIÓ ---
const categorias = computed(() => Array.from(new Set(instrumentos.value.map(inst => inst.tipo))))
const instrumentosAgrupados = computed(() => {
  const filtrados = instrumentos.value.filter(inst => inst.tipo === categoriaActiva.value)
  const grupos = {}
  filtrados.forEach(inst => {
    if (!grupos[inst.subcategoria]) grupos[inst.subcategoria] = []
    grupos[inst.subcategoria].push(inst)
  })
  return grupos
})

const cambiarCategoria = (cat) => { categoriaActiva.value = cat; equipoSeleccionado.value = null; instrumentoExpandido.value = null }
// «14 de diciembre» en el idioma de la web
const fechaLocal = (iso) => {
  const [a, m, d] = iso.split('-').map(Number)
  return new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long' }).format(new Date(a, m - 1, d))
}

const verDetalles = (equipo) => { equipoSeleccionado.value = equipo; diasSeleccionados.value = []; estado.value = ''; cargarOcupacion(equipo.id) }

// Días en que el instrumento está prestado o reservado (de la intranet, sin nombres)
const ocupados = ref(new Set())
const cargarOcupacion = async (id) => {
  ocupados.value = new Set()
  try {
    const r = await fetch(`/api/ocupacion?recurso=instrument&instrumento_id=${id}`)
    if (r.ok && equipoSeleccionado.value?.id === id) ocupados.value = new Set(await r.json())
  } catch { /* sin conexión: se muestran todos libres */ }
}
const toggleAcordeon = (id) => { instrumentoExpandido.value = instrumentoExpandido.value === id ? null : id }

// --- CALENDARI (Corregit per incloure les funcions que et faltaven) ---
const fechaHoy = new Date()
const mesActual = ref(fechaHoy.getMonth())
const anioActual = ref(fechaHoy.getFullYear())
// Mes y año en el idioma de la web (p. ej. "octubre de 2026", "October 2026")
const nombreMes = computed(() => {
  const texto = new Intl.DateTimeFormat(locale.value, { month: 'long', year: 'numeric' })
    .format(new Date(anioActual.value, mesActual.value, 1))
  return texto.charAt(0).toUpperCase() + texto.slice(1)
})
const esHoyInstr = (n) => anioActual.value === fechaHoy.getFullYear() && mesActual.value === fechaHoy.getMonth() && n === fechaHoy.getDate()
const diasEnMes = computed(() => new Date(anioActual.value, mesActual.value + 1, 0).getDate())

const cambiarMes = (dir) => {
  let nuevoMes = mesActual.value + dir
  if (nuevoMes > 11) { nuevoMes = 0; anioActual.value++ }
  else if (nuevoMes < 0) { nuevoMes = 11; anioActual.value-- }
  mesActual.value = nuevoMes
  diasSeleccionados.value = []
}

const esOcupado = (n) => ocupados.value.has(
  `${anioActual.value}-${String(mesActual.value + 1).padStart(2, '0')}-${String(n).padStart(2, '0')}`)
const toggleDia = (n) => {
    if (esOcupado(n)) return
    const i = diasSeleccionados.value.indexOf(n)
    i > -1 ? diasSeleccionados.value.splice(i, 1) : diasSeleccionados.value.push(n)
}

const diasOrdenadosTexto = computed(() => [...diasSeleccionados.value].sort((a, b) => a - b).join(', '))

// Dies triats en format AAAA-MM-DD (per passar-los al calendari des de la intranet)
const diasIso = () => [...diasSeleccionados.value].sort((a, b) => a - b)
  .map(n => `${anioActual.value}-${String(mesActual.value + 1).padStart(2, '0')}-${String(n).padStart(2, '0')}`)

// ---------- Document de préstec ----------
// Es genera aquí mateix, amb les dades de qui el demana. L'ha de signar digitalment
// (AutoFirma, Adobe amb certificat...) i adjuntar-lo: sense document signat no s'envia.
const docPrestec = ref(null)
const inputDoc = ref(null)
const elegirDoc = (e) => { docPrestec.value = e.target.files?.[0] || null }
const puedeGenerar = computed(() => diasSeleccionados.value.length > 0 && nombre.value.trim() && email.value.trim())
const generarDocumento = async () => {
  if (!puedeGenerar.value) { alert(t('instrumentacion.doc.faltan')); return }
  const { jsPDF } = await import('jspdf')
  const pdf = new jsPDF({ unit: 'mm', format: 'a4' })
  const M = 20, ANCHO = 170
  let y = 22
  const linea = (texto, { mida = 10, negreta = false, espai = 5 } = {}) => {
    pdf.setFont('helvetica', negreta ? 'bold' : 'normal'); pdf.setFontSize(mida)
    for (const l of pdf.splitTextToSize(texto, ANCHO)) {
      if (y > 275) { pdf.addPage(); y = 22 }
      pdf.text(l, M, y); y += mida * 0.45
    }
    y += espai - 2
  }
  const eq = equipoSeleccionado.value
  const hoyTexto = new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date())
  pdf.setDrawColor(1, 33, 105); pdf.setLineWidth(0.8); pdf.line(M, 14, M + ANCHO, 14)
  linea(t('instrumentacion.doc.organismo'), { mida: 9, espai: 3 })
  linea(t('instrumentacion.doc.titulo'), { mida: 15, negreta: true, espai: 6 })
  linea(t('instrumentacion.doc.intro'), { espai: 6 })
  linea(t('instrumentacion.doc.datos'), { mida: 11, negreta: true, espai: 3 })
  const campos = [
    [t('instrumentacion.doc.nombre'), nombre.value.trim()],
    [t('instrumentacion.doc.email'), email.value.trim()],
    [t('instrumentacion.doc.institucion'), institucionInvestigador.value.trim() || '—'],
    [t('instrumentacion.doc.instrumento'), `${eq.nombre}${eq.marca ? ' (' + eq.marca + ')' : ''}`],
    [t('instrumentacion.doc.numeroSerie'), eq.numeroSerie || '—'],
    [t('instrumentacion.doc.fechas'), diasIso().map(d => d.split('-').reverse().join('/')).join(', ')]
  ]
  for (const [k, v] of campos) linea(`${k}: ${v}`, { espai: 2 })
  y += 3
  linea(t('instrumentacion.doc.clausulasTitulo'), { mida: 11, negreta: true, espai: 3 })
  tm('instrumentacion.doc.clausulas').forEach((c, i) => linea(`${i + 1}. ${rt(c)}`, { espai: 3 }))
  y += 4
  linea(t('instrumentacion.doc.firmaTitulo'), { mida: 11, negreta: true, espai: 3 })
  linea(t('instrumentacion.doc.firmaTexto', { nombre: nombre.value.trim(), fecha: hoyTexto }), { espai: 4 })
  pdf.setDrawColor(150); pdf.setLineWidth(0.3); pdf.rect(M, y, 80, 30)
  pdf.setFontSize(8); pdf.text(t('instrumentacion.doc.recuadro'), M + 2, y + 5)
  y += 38
  linea(t('instrumentacion.doc.pie'), { mida: 8, espai: 2 })
  pdf.save(`Prestec_SIO_${eq.nombre.replace(/[^\w\d-]+/g, '_')}.pdf`)
}

// Envia la sol·licitud al SIO des de la web (sense obrir el programa de correu)
const enviarSolicitud = async () => {
  if (diasSeleccionados.value.length === 0) {
    alert(t('instrumentacion.faltanDatos'))
    return
  }
  if (!docPrestec.value) {
    alert(t('instrumentacion.doc.falta'))
    return
  }
  const instrumento = equipoSeleccionado.value.nombre
  const dias = t('instrumentacion.correo.diasValor', { dias: diasOrdenadosTexto.value, mes: nombreMes.value })
  const institucion = institucionInvestigador.value.trim()
  const cuerpo = (
    `${t('instrumentacion.correo.saludo')}\n\n` +
    `${t('instrumentacion.correo.intro')}\n\n` +
    `${t('instrumentacion.correo.instrumento')}: ${instrumento}\n` +
    `${t('instrumentacion.correo.dias')}: ${dias}\n` +
    `${t('instrumentacion.correo.nombre')}: ${nombre.value.trim()}\n` +
    (institucion ? `${t('instrumentacion.correo.institucion')}: ${institucion}\n` : '') +
    `\n${t('instrumentacion.doc.adjuntoCorreo')}\n` +
    `\n${t('instrumentacion.correo.despedida')}`
  )
  if (await enviar({ asunto: t('instrumentacion.correo.asunto', { instrumento }), cuerpo, adjunto: docPrestec.value,
    dias: diasIso(), institucion, instrumentoId: equipoSeleccionado.value.id })) {
    diasSeleccionados.value = []
    docPrestec.value = null
    if (inputDoc.value) inputDoc.value.value = ''
  }
}
</script>

<template>

  <div class="servicios-hub">
    <div class="fondo-servicios"></div>

    <div class="contenido-hub">
      <h1 class="titulo-seccion">{{ $t('instrumentacion.titulo') }}</h1>
      <p class="subtitulo">{{ $t('instrumentacion.subtitulo') }}</p>

      <div v-if="cargando" class="alerta-estado carga">⏳ {{ $t('instrumentacion.cargando') }}</div>
      <div v-else-if="errorCarga" class="alerta-estado error">❌ {{ $t('instrumentacion.errorCarga') }}</div>

      <div v-else>
        <div class="tabs-sio">
          <button v-for="cat in categorias" :key="cat" :class="['tab-btn', { activa: categoriaActiva === cat }]" @click="cambiarCategoria(cat)">
            {{ cat }}
          </button>
        </div>

        <div class="grid-layout">
          <!-- ZONA IZQUIERDA: CATÁLOGO CON ACORDEÓN -->
          <div class="seccion-bloque ficha-wiki">
            <div v-if="Object.keys(instrumentosAgrupados).length === 0" style="color: #666; font-style: italic;">{{ $t('instrumentacion.sinInstrumentos') }}</div>

            <div v-for="(lista, subcat) in instrumentosAgrupados" :key="subcat" class="bloque-subcat">
              <h3 class="titulo-subcat">{{ subcat || $t('instrumentacion.sinSubcategoria') }}</h3>
              <ul class="lista-wiki">
                <li v-for="inst in lista" :key="inst.id">
                  <div class="item-header">
                    <span class="punto-azul">•</span>
                    <button type="button" class="enlace-wiki btn-enlace" @click="verDetalles(inst)" :title="$t('instrumentacion.verFicha')">{{ inst.nombre }}</button>
                    <span v-if="inst.marca" class="marca-wiki">({{ inst.marca }})</span>
                    <span v-if="inst.prestadoHasta" class="etiqueta-prestamo">{{ $t('instrumentacion.enPrestamoHasta', { fecha: fechaLocal(inst.prestadoHasta) }) }}</span>
                  </div>
                  <div class="caja-gris-wiki">
                    <div v-if="inst.ultimaCalibracion"><strong>- {{ $t('instrumentacion.ultimaCalibracion') }}:</strong> {{ inst.ultimaCalibracion }}</div>
                    
                    <button class="btn-acordeon" :aria-expanded="instrumentoExpandido === inst.id" @click="toggleAcordeon(inst.id)">
                      <span v-if="instrumentoExpandido === inst.id">▲ {{ $t('instrumentacion.ocultarInfo') }}</span>
                      <span v-else>▼ {{ $t('instrumentacion.verInfo') }}</span>
                    </button>
                    
                    <div v-show="instrumentoExpandido === inst.id" class="contenido-acordeon">
                      <div class="bloque-info-wiki">
                        <h4>{{ $t('instrumentacion.descripcion') }}</h4>
                        <div v-if="inst.descripcionCompleta" class="texto-wiki" v-html="limpiarHtml(inst.descripcionCompleta)" style="white-space: pre-wrap;"></div>
                        <div v-else class="texto-wiki">{{ $t('instrumentacion.sinDescripcion') }}</div>
                      </div>
                      <div class="bloque-info-wiki">
                        <h4>{{ $t('instrumentacion.especificaciones') }}</h4>
                        <div v-if="inst.parametros" v-html="limpiarHtml(inst.parametros)" style="white-space: pre-wrap; font-family: inherit; line-height: 1.6;"></div>
                        <div v-else>{{ $t('instrumentacion.sinParametros') }}</div>
                      </div>
                      
                      <button class="btn-acordeon btn-cerrar-acordeon" @click="toggleAcordeon(inst.id)">
                        ▲ {{ $t('instrumentacion.ocultarInfo') }}
                      </button>
                    </div>

                  </div>
                </li>
              </ul>
            </div>
          </div>

          <!-- ZONA DERECHA: GESTIÓN DE RESERVAS -->
          <div class="seccion-bloque ficha-gestion">
            
            <div v-if="equipoSeleccionado" class="detalles-equipo">
              <div class="cabecera-estado">
                <h2 class="titulo-fija">{{ equipoSeleccionado.nombre }}</h2>
                <span v-if="equipoSeleccionado.prestadoHasta" class="badge-grande prestado">{{ $t('instrumentacion.enPrestamo') }}</span>
                <span v-else :class="['badge-grande', equipoSeleccionado.estado.toLowerCase().replace(' ', '-')]">
                  {{ equipoSeleccionado.estado }}
                </span>
              </div>
              <p v-if="equipoSeleccionado.prestadoHasta" class="aviso-prestamo">{{ $t('instrumentacion.avisoPrestamo', { fecha: fechaLocal(equipoSeleccionado.prestadoHasta) }) }}</p>
              
              <div class="calendario-mini">
                <h3 class="titulo-mini">{{ $t('instrumentacion.paso1') }}</h3>
                
                <div class="controles-mes">
                  <button @click.prevent="cambiarMes(-1)" class="btn-mes" :aria-label="$t('instrumentacion.mesAnterior')">◀</button>
                  <span class="mes-actual">{{ nombreMes }}</span>
                  <button @click.prevent="cambiarMes(1)" class="btn-mes" :aria-label="$t('instrumentacion.mesSiguiente')">▶</button>
                </div>

                <div class="grid-dias">
                  <div v-for="n in diasEnMes" :key="n" @click="toggleDia(n)" :class="['dia', { ocupado: esOcupado(n), seleccionado: diasSeleccionados.includes(n), disponible: !esOcupado(n), hoy: esHoyInstr(n) }]">
                    {{ n }}
                  </div>
                </div>
                <p class="leyenda">{{ $t('instrumentacion.leyenda') }}</p>
              </div>

              <form class="formulario-reserva" @submit.prevent="enviarSolicitud">
                <h3 class="titulo-mini">{{ $t('instrumentacion.paso2') }}</h3>
                <p class="txt-p" style="font-size: 0.85rem; margin-bottom: 15px;">
                  {{ $t('instrumentacion.explicacion') }} {{ $t('instrumentacion.explicacionFin') }}
                </p>

                <DatosSolicitante v-model:nombre="nombre" v-model:email="email" v-model:web="web" />
                <div class="form-grupo">
                  <label for="institucion-investigador">{{ $t('instrumentacion.institucion') }}:</label>
                  <input type="text" id="institucion-investigador" v-model="institucionInvestigador" :placeholder="$t('instrumentacion.institucionPh')" class="input-form">
                </div>

                <!-- Document de préstec: descarregar, signar digitalment i adjuntar -->
                <div class="bloque-doc">
                  <h4>📄 {{ $t('instrumentacion.doc.bloqueTitulo') }}</h4>
                  <ol>
                    <li>{{ $t('instrumentacion.doc.paso1') }}
                      <button type="button" class="btn-doc" :disabled="!puedeGenerar" @click="generarDocumento">⬇️ {{ $t('instrumentacion.doc.descargar') }}</button>
                      <small v-if="!puedeGenerar" class="nota-doc">{{ $t('instrumentacion.doc.faltan') }}</small>
                    </li>
                    <li>{{ $t('instrumentacion.doc.paso2') }}</li>
                    <li>{{ $t('instrumentacion.doc.paso3') }}
                      <input ref="inputDoc" type="file" accept=".pdf,application/pdf" class="input-doc" @change="elegirDoc">
                      <small v-if="docPrestec" class="ok-doc">✔ {{ docPrestec.name }}</small>
                    </li>
                  </ol>
                </div>

                <button
                  type="submit"
                  :class="['btn-submit', { 'btn-desactivado': diasSeleccionados.length === 0 || !docPrestec || estado === 'enviando' }]"
                  :disabled="diasSeleccionados.length === 0 || !docPrestec || estado === 'enviando'"
                >
                  {{ estado === 'enviando' ? $t('solicitud.enviando') : $t('instrumentacion.preparar') }}
                </button>
                <EstadoSolicitud :estado="estado" :error="error" />
              </form>
              
              <button class="btn-cerrar" @click="equipoSeleccionado = null">{{ $t('instrumentacion.cerrar') }}</button>
            </div>

            <div v-else>
              <h2 class="titulo-fija">{{ $t('instrumentacion.prestamos') }}</h2>
              <p class="txt-p">{{ $t('instrumentacion.ayuda') }}</p>
              <hr style="border: 0; border-top: 1px solid #eee; margin: 25px 0;">
              <h3 class="titulo-mini">{{ $t('instrumentacion.comoFunciona') }}</h3>
              <ol style="color: #666; font-size: 0.9rem; line-height: 1.6; padding-left: 20px;">
                <li v-for="(paso, i) in $tm('instrumentacion.pasos')" :key="i">{{ $rt(paso) }}</li>
              </ol>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bloque-doc { background: #f4f7f9; border-left: 4px solid #0086c0; border-radius: 6px; padding: 10px 14px; margin: 12px 0; font-size: 0.85rem; color: #333; }
.bloque-doc h4 { margin: 0 0 6px; color: #012169; font-size: 0.95rem; }
.bloque-doc ol { margin: 0; padding-left: 18px; line-height: 1.5; }
.bloque-doc li { margin-bottom: 6px; }
.btn-doc { display: block; margin-top: 4px; background: #012169; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; cursor: pointer; font-size: 0.85rem; }
.btn-doc:disabled { background: #9aa5b4; cursor: not-allowed; }
.input-doc { display: block; margin-top: 4px; font-size: 0.82rem; max-width: 100%; }
.nota-doc { color: #7a4300; display: block; }
.ok-doc { color: #1e7e34; font-weight: bold; display: block; }
/* ESTILOS GLOBALES UNIFICADOS */
.servicios-hub { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-servicios { 
  position: absolute; top: 0; left: 0; width: 100%; height: 550px; 
  background-image: linear-gradient(rgba(1, 33, 105, 0.75), rgba(1, 33, 105, 0.9)), url('/instrumentacion.webp');
  background-size: cover; background-position: center; z-index: 0; 
}
.contenido-hub { position: relative; z-index: 10; padding-top: 120px; max-width: 1300px; margin: 0 auto; padding-left: 20px; padding-right: 20px; }
.titulo-seccion { color: white; font-size: 2.2rem; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; margin-bottom: 15px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 25px; max-width: 800px; }

/* ALERTAS ESTADO */
.alerta-estado { text-align: center; padding: 20px; border-radius: 8px; font-weight: bold; margin-bottom: 30px; font-size: 1.2rem; }
.alerta-estado.carga { background: rgba(255, 255, 255, 0.9); color: #012169; border: 2px solid #0086c0; }
.alerta-estado.error { background: #ffebee; color: #c62828; border: 2px solid #ef5350; }

/* TABS */
.tabs-sio { display: flex; gap: 10px; margin-bottom: 25px; overflow-x: auto; }
.tab-btn { padding: 10px 20px; background: rgba(255, 255, 255, 0.1); border: 1px solid white; color: white; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; white-space: nowrap; }
.tab-btn.activa { background: #8cc63f; border-color: #8cc63f; color: #012169; }

/* GRID PRINCIPAL */
.grid-layout { display: grid; grid-template-columns: 1.8fr 1.3fr; gap: 30px; }
.seccion-bloque { background: white; border-radius: 12px; padding: 35px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); min-height: auto; }
.titulo-fija { color: #012169; margin-top: 0; font-size: 1.4rem; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }

/* ESTILO LISTADO (ZONA IZQUIERDA) */
.bloque-subcat { margin-bottom: 30px; }
.titulo-subcat { font-size: 1.1rem; color: #333; margin-bottom: 15px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
.lista-wiki { list-style: none; padding-left: 0; margin: 0; }
.item-header { margin-bottom: 8px; font-size: 0.95rem; }
.punto-azul { color: #0056b3; margin-right: 8px; font-size: 1.2rem; line-height: 0; }
.enlace-wiki { color: #0056b3; font-weight: 500; cursor: pointer; text-decoration: none; font-size: 1.05rem; }
.enlace-wiki:hover { text-decoration: underline; }
.btn-enlace { background: none; border: none; padding: 0; font-family: inherit; text-align: left; }
.marca-wiki { color: #666; font-size: 0.9rem; margin-left: 5px; }
.caja-gris-wiki { background-color: #f1f3f4; border-radius: 6px; padding: 10px 15px; margin-left: 15px; margin-bottom: 20px; font-family: 'Consolas', 'Courier New', Courier, monospace; font-size: 0.85rem; color: #202124; line-height: 1.6; }

/* ESTILOS ACORDEÓN E IMAGEN */
.btn-acordeon { background: none; border: none; color: #0086c0; font-family: inherit; font-size: 0.85rem; font-weight: bold; cursor: pointer; padding: 5px 0 0 0; display: block; margin-top: 5px; text-align: left; }
.btn-acordeon:hover { text-decoration: underline; }
.btn-cerrar-acordeon { width: 100%; text-align: center; margin-top: 15px; padding-top: 12px; border-top: 1px dashed #ddd; color: #666; font-size: 0.8rem; }
.btn-cerrar-acordeon:hover { color: #d32f2f; text-decoration: none; }
.contenido-acordeon { background: white; border-left: 3px solid #8cc63f; padding: 15px; margin-top: 10px; border-radius: 0 6px 6px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); animation: fadeIn 0.3s; }

.bloque-info-wiki { margin-bottom: 15px; }
.bloque-info-wiki h4 { color: #012169; font-size: 0.95rem; margin: 0 0 5px 0; font-family: system-ui, -apple-system, sans-serif; }
.texto-wiki { margin: 0; white-space: pre-line; color: #555; font-size: 0.9rem; }
.parametros-wiki { background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 0.8rem; border: 1px dashed #ccc; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }

/* PANEL DERECHO (GESTIÓN) */
.cabecera-estado { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px;}
.cabecera-estado .titulo-fija { border-bottom: none; margin-bottom: 0; padding-bottom: 0; font-size: 1.3rem;}
.badge-grande { padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; }
.badge-grande.prestado { background: #fff4e5; color: #b45d00; }
.etiqueta-prestamo { margin-left: 8px; background: #fff4e5; color: #b45d00; border: 1px solid #f3c98b; border-radius: 10px; padding: 1px 8px; font-size: 0.78rem; font-weight: bold; white-space: nowrap; }
.aviso-prestamo { background: #fff4e5; color: #7a4300; border-left: 3px solid #f0a640; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; margin: 0 0 15px; }
.badge-grande.disponible { background: #e6f4ea; color: #1e7e34; }
.badge-grande.en-uso { background: #fff4e5; color: #b45d00; }
.badge-grande.mantenimiento { background: #fdeaea; color: #c53030; }
.txt-p { font-size: 0.95rem; color: #666; line-height: 1.5; margin-bottom: 20px; }

/* ESTILOS NUEVOS DEL CALENDARIO */
.calendario-mini { margin-bottom: 20px; }
.titulo-mini { font-size: 1.1rem; color: #012169; margin-bottom: 10px; font-weight: bold; }
.controles-mes { display: flex; justify-content: space-between; align-items: center; background: #012169; color: white; padding: 8px 15px; border-radius: 6px 6px 0 0; }
.btn-mes { background: transparent; border: none; color: white; font-size: 1.2rem; cursor: pointer; transition: transform 0.2s; }
.btn-mes:hover { transform: scale(1.2); }
.mes-actual { font-weight: bold; font-size: 1rem; }
.grid-dias { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; padding: 10px; background: #f9f9f9; border: 1px solid #eee; border-radius: 0 0 6px 6px; }
.dia { padding: 8px; text-align: center; font-size: 0.85rem; border-radius: 4px; font-weight: bold; transition: 0.2s; user-select: none; }
.dia.disponible { background: white; color: #666; cursor: pointer; border: 1px solid #ddd;}
.dia.disponible:hover { border-color: #8cc63f; background: #f0f7e6; }
.dia.ocupado { background: #0086c0; color: white; cursor: not-allowed; opacity: 0.6; }
.dia.seleccionado { background: #8cc63f; color: #012169; border: 1px solid #012169; transform: scale(1.05); }
/* Avui, ben marcat */
.dia.hoy { outline: 3px solid #012169; outline-offset: -3px; position: relative; }
.dia.hoy::after { content: ''; position: absolute; left: 50%; bottom: 3px; width: 5px; height: 5px; margin-left: -2.5px; border-radius: 50%; background: #012169; }
.dia.hoy.ocupado::after, .dia.hoy.seleccionado::after { background: white; }
.leyenda { font-size: 0.75rem; color: #999; margin-top: 10px; text-align: center; }

/* GENERADOR DE DOCUMENTO Y FORMULARIO RESERVA */
.formulario-reserva { background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; margin-top: 15px; }
.form-grupo { margin-bottom: 15px; }
.form-grupo label { display: block; font-size: 0.85rem; color: #333; margin-bottom: 5px; font-weight: bold; }
.input-form { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.95rem; box-sizing: border-box; font-family: inherit;}


.btn-submit { width: 100%; background-color: #012169; color: white; border: none; padding: 15px; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 10px; }
.btn-submit:hover:not(.btn-desactivado) { background-color: #0056b3; transform: translateY(-2px); }
.btn-desactivado { background-color: #ccc; cursor: not-allowed; }

.btn-cerrar { margin-top: 30px; width: 100%; background: #eee; color: #555; border: none; padding: 10px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; }
.btn-cerrar:hover { background: #e0e0e0; color: #333; }

@media (max-width: 992px) { 
  .grid-layout { grid-template-columns: 1fr; } 
}
</style>