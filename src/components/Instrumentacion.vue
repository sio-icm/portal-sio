<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

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
const nombreInvestigador = ref('')
const institucionInvestigador = ref('')

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
      ultimaCalibracion: fila.ultima_calibracion || '',
      descripcionCompleta: fila.descripcion || '',
      parametros: fila.parametros_tecnicos || ''
    }))
    cargando.value = false
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
const verDetalles = (equipo) => { equipoSeleccionado.value = equipo; diasSeleccionados.value = [] }
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
const diasEnMes = computed(() => new Date(anioActual.value, mesActual.value + 1, 0).getDate())

const cambiarMes = (dir) => {
  let nuevoMes = mesActual.value + dir
  if (nuevoMes > 11) { nuevoMes = 0; anioActual.value++ }
  else if (nuevoMes < 0) { nuevoMes = 11; anioActual.value-- }
  mesActual.value = nuevoMes
  diasSeleccionados.value = []
}

// Aquestes són les funcions que faltaven al teu script!
const esOcupado = (n) => {
    // Si vols una lògica real d'ocupació, l'hauries de fer aquí
    return false 
}
const toggleDia = (n) => {
    const i = diasSeleccionados.value.indexOf(n)
    i > -1 ? diasSeleccionados.value.splice(i, 1) : diasSeleccionados.value.push(n)
}

const diasOrdenadosTexto = computed(() => [...diasSeleccionados.value].sort((a, b) => a - b).join(', '))

// Obre el correu de l'usuari amb la sol·licitud preparada (sense serveis externs)
const enviarSolicitud = () => {
  if (diasSeleccionados.value.length === 0 || !nombreInvestigador.value.trim()) {
    alert(t('instrumentacion.faltanDatos'))
    return
  }
  const destinatario = "sio@icm.csic.es"
  const instrumento = equipoSeleccionado.value.nombre
  const dias = t('instrumentacion.correo.diasValor', { dias: diasOrdenadosTexto.value, mes: nombreMes.value })
  const institucion = institucionInvestigador.value.trim()
  const asunto = encodeURIComponent(t('instrumentacion.correo.asunto', { instrumento }))
  const cuerpo = encodeURIComponent(
    `${t('instrumentacion.correo.saludo')}\n\n` +
    `${t('instrumentacion.correo.intro')}\n\n` +
    `${t('instrumentacion.correo.instrumento')}: ${instrumento}\n` +
    `${t('instrumentacion.correo.dias')}: ${dias}\n` +
    `${t('instrumentacion.correo.nombre')}: ${nombreInvestigador.value.trim()}\n` +
    (institucion ? `${t('instrumentacion.correo.institucion')}: ${institucion}\n` : '') +
    `\n${t('instrumentacion.correo.despedida')}`
  )
  window.location.href = `mailto:${destinatario}?subject=${asunto}&body=${cuerpo}`
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
                        <div v-if="inst.descripcionCompleta" class="texto-wiki" v-html="inst.descripcionCompleta" style="white-space: pre-wrap;"></div>
                        <div v-else class="texto-wiki">{{ $t('instrumentacion.sinDescripcion') }}</div>
                      </div>
                      <div class="bloque-info-wiki">
                        <h4>{{ $t('instrumentacion.especificaciones') }}</h4>
                        <div v-if="inst.parametros" v-html="inst.parametros" style="white-space: pre-wrap; font-family: inherit; line-height: 1.6;"></div>
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
                <span :class="['badge-grande', equipoSeleccionado.estado.toLowerCase().replace(' ', '-')]">
                  {{ equipoSeleccionado.estado }}
                </span>
              </div>
              
              <div class="calendario-mini">
                <h3 class="titulo-mini">{{ $t('instrumentacion.paso1') }}</h3>
                
                <div class="controles-mes">
                  <button @click.prevent="cambiarMes(-1)" class="btn-mes" :aria-label="$t('instrumentacion.mesAnterior')">◀</button>
                  <span class="mes-actual">{{ nombreMes }}</span>
                  <button @click.prevent="cambiarMes(1)" class="btn-mes" :aria-label="$t('instrumentacion.mesSiguiente')">▶</button>
                </div>

                <div class="grid-dias">
                  <div v-for="n in diasEnMes" :key="n" @click="toggleDia(n)" :class="['dia', { ocupado: esOcupado(n), seleccionado: diasSeleccionados.includes(n), disponible: !esOcupado(n) }]">
                    {{ n }}
                  </div>
                </div>
                <p class="leyenda">{{ $t('instrumentacion.leyenda') }}</p>
              </div>

              <div class="formulario-reserva">
                <h3 class="titulo-mini">{{ $t('instrumentacion.paso2') }}</h3>
                <p class="txt-p" style="font-size: 0.85rem; margin-bottom: 15px;">
                  {{ $t('instrumentacion.explicacion') }}
                  <a href="mailto:sio@icm.csic.es">sio@icm.csic.es</a>. {{ $t('instrumentacion.explicacionFin') }}
                </p>

                <div class="form-grupo">
                  <label for="nombre-investigador">{{ $t('instrumentacion.nombre') }}:</label>
                  <input type="text" id="nombre-investigador" v-model="nombreInvestigador" :placeholder="$t('instrumentacion.nombrePh')" class="input-form">
                </div>
                <div class="form-grupo">
                  <label for="institucion-investigador">{{ $t('instrumentacion.institucion') }}:</label>
                  <input type="text" id="institucion-investigador" v-model="institucionInvestigador" :placeholder="$t('instrumentacion.institucionPh')" class="input-form">
                </div>

                <button
                  type="button"
                  @click="enviarSolicitud"
                  :class="['btn-submit', { 'btn-desactivado': diasSeleccionados.length === 0 }]"
                  :disabled="diasSeleccionados.length === 0"
                >
                  📧 {{ $t('instrumentacion.preparar') }}
                </button>
              </div>
              
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