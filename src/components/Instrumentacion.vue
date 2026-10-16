<script setup>
import { ref, computed, onMounted } from 'vue'

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
const dniInvestigador = ref('')
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
      subcategoria: fila.subcategoria || 'Sense Subcategoria',
      nombre: fila.nombre,
      marca: fila.marca || '',
      estado: fila.estado || 'Disponible',
      ultimaCalibracion: fila.ultima_calibracion || 'N/A',
      descripcionCompleta: fila.descripcion || 'No hi ha descripció disponible.',
      parametros: fila.parametros_tecnicos || 'No hi ha paràmetres tècnics.'
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
const nombresMeses = ['Gener', 'Febrer', 'Març', 'Abril', 'Maig', 'Juny', 'Juliol', 'Agost', 'Setembre', 'Octubre', 'Novembre', 'Desembre']
const nombreMes = computed(() => nombresMeses[mesActual.value])
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

const diasOrdenadosTexto = computed(() => diasSeleccionados.value.length === 0 ? 'Cap dia' : diasSeleccionados.value.sort((a, b) => a - b).join(', '))

const generarDocumento = () => {
    if (diasSeleccionados.value.length === 0 || !nombreInvestigador.value) return alert("Emplena les dades abans")
    alert("Generant PDF per a " + nombreInvestigador.value)
}
</script>

<template>

  <div class="servicios-hub">
    <div class="fondo-servicios"></div>

    <div class="contenido-hub">
      <h1 class="titulo-seccion">Instrumentación Oceanográfica</h1>
      <p class="subtitulo">Catálogo técnico, calibraciones y gestión de préstamos del SIO.</p>

      <div v-if="cargando" class="alerta-estado carga">⏳ Connectant amb la Base de Dades del SIO...</div>
      <div v-else-if="errorCarga" class="alerta-estado error">❌ Error de connexió. No s'ha pogut carregar el catàleg d'instruments.</div>

      <div v-else>
        <div class="tabs-sio">
          <button v-for="cat in categorias" :key="cat" :class="['tab-btn', { activa: categoriaActiva === cat }]" @click="cambiarCategoria(cat)">
            {{ cat }}
          </button>
        </div>

        <div class="grid-layout">
          <!-- ZONA IZQUIERDA: CATÁLOGO CON ACORDEÓN -->
          <div class="seccion-bloque ficha-wiki">
            <div v-if="Object.keys(instrumentosAgrupados).length === 0" style="color: #666; font-style: italic;">No hi ha instruments catalogats en aquesta secció.</div>

            <div v-for="(lista, subcat) in instrumentosAgrupados" :key="subcat" class="bloque-subcat">
              <h3 class="titulo-subcat">{{ subcat }}</h3>
              <ul class="lista-wiki">
                <li v-for="inst in lista" :key="inst.id">
                  <div class="item-header">
                    <span class="punto-azul">•</span>
                    <span class="enlace-wiki" @click="verDetalles(inst)" title="Click para reservar">{{ inst.nombre }}</span>
                    <span class="marca-wiki">({{ inst.marca }})</span>
                  </div>
                  <div class="caja-gris-wiki">
                    <div v-if="inst.ultimaCalibracion"><strong>- Última calibració:</strong> {{ inst.ultimaCalibracion }}</div>
                    
                    <button class="btn-acordeon" @click="toggleAcordeon(inst.id)">
                      <span v-if="instrumentoExpandido === inst.id">▲ Ocultar informació tècnica</span>
                      <span v-else>▼ Veure informació tècnica i manuals</span>
                    </button>
                    
                    <div v-show="instrumentoExpandido === inst.id" class="contenido-acordeon">
                      <div class="bloque-info-wiki">
                        <h4>Descripció General</h4>
                        <div class="texto-wiki" v-html="inst.descripcionCompleta" style="white-space: pre-wrap;"></div>
                        <div class="bloque-info-wiki">
                         <h4>Especificacions Tècniques / Manuals</h4>
                         <div v-html="inst.parametros" style="white-space: pre-wrap; font-family: inherit; line-height: 1.6;"></div>
                         </div>

                      <div v-html="inst.parametros" style="white-space: pre-wrap; font-family: inherit; line-height: 1.6;"></div>
                      </div>
                      
                      <button class="btn-acordeon btn-cerrar-acordeon" @click="toggleAcordeon(inst.id)">
                        ▲ Ocultar informació tècnica
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
                <h3 class="titulo-mini">Pàs 1: Selecciona els dies de reserva</h3>
                
                <div class="controles-mes">
                  <button @click.prevent="cambiarMes(-1)" class="btn-mes">◀</button>
                  <span class="mes-actual">{{ nombreMes }} {{ anioActual }}</span>
                  <button @click.prevent="cambiarMes(1)" class="btn-mes">▶</button>
                </div>

                <div class="grid-dias">
                  <div v-for="n in diasEnMes" :key="n" @click="toggleDia(n)" :class="['dia', { ocupado: esOcupado(n), seleccionado: diasSeleccionados.includes(n), disponible: !esOcupado(n) }]">
                    {{ n }}
                  </div>
                </div>
                <p class="leyenda">* Gris: Disponible | Blau: Ocupat | Verd: La teva selecció</p>
              </div>

              <div class="generador-doc-box">
                <h3 class="titulo-mini">Pàs 2: Generar Document de Responsabilitat</h3>
                <p class="txt-p" style="font-size: 0.85rem; margin-bottom: 15px;">Emplena les teves dades per generar el document amb les dates de reserva ja incloses. Desa'l com a PDF per signar-lo.</p>
                
                <div class="form-grupo">
                  <label>Nom i Cognoms:</label>
                  <input type="text" v-model="nombreInvestigador" placeholder="Ex: Eve Galimany Sanromà" class="input-form">
                </div>
                <div class="form-grupo" style="display: flex; gap: 10px;">
                  <div style="flex: 1;">
                    <label>DNI / Passaport:</label>
                    <input type="text" v-model="dniInvestigador" placeholder="Ex: 38110059W" class="input-form">
                  </div>
                  <div style="flex: 1;">
                    <label>Institució (Opcional):</label>
                    <input type="text" v-model="institucionInvestigador" placeholder="Ex: ICATMAR" class="input-form">
                  </div>
                </div>
                
                <button @click="generarDocumento" class="btn-generar" :disabled="diasSeleccionados.length === 0">
                  📄 Generar i Desar PDF
                </button>
              </div>

              <form action="https://formsubmit.co/sio@icm.csic.es" method="POST" enctype="multipart/form-data" class="formulario-reserva">
                <h3 class="titulo-mini">Pàs 3: Envia la Sol·licitud</h3>
                
                <input type="hidden" name="_subject" :value="'Nova Reserva SIO: ' + equipoSeleccionado.nombre">
                <input type="hidden" name="_template" value="table">
                <input type="hidden" name="Equip_Sol·licitat" :value="equipoSeleccionado.nombre">
                <input type="hidden" name="Dies_Reserva" :value="diasOrdenadosTexto">
                <input type="hidden" name="Investigador" :value="nombreInvestigador">

                <div class="form-grupo">
                  <label>Correu Electrònic (Per confirmar la reserva):</label>
                  <input type="email" name="email" required placeholder="exemple@icm.csic.es" class="input-form">
                </div>

                <div class="form-grupo">
                  <label>Adjunta el PDF Generat i Signat Digitalment:</label>
                  <input type="file" name="Document_Signat" accept="application/pdf" required class="input-form file-input">
                </div>

                <button 
                  type="submit" 
                  :class="['btn-submit', { 'btn-desactivado': diasSeleccionados.length === 0 }]"
                  :disabled="diasSeleccionados.length === 0"
                >
                  📤 Enviar Sol·licitud de Reserva
                </button>
              </form>
              
              <button class="btn-cerrar" @click="equipoSeleccionado = null">Tancar Detalls</button>
            </div>

            <div v-else>
              <h2 class="titulo-fija">Préstecs SIO</h2>
              <p class="txt-p">Feu clic a l'enllaç blau de qualsevol instrument a l'esquerra per veure la seva fitxa tècnica completa i disponibilitat.</p>
              <hr style="border: 0; border-top: 1px solid #eee; margin: 25px 0;">
              <h3 class="titulo-mini">Com funciona?</h3>
              <ol style="color: #666; font-size: 0.9rem; line-height: 1.6; padding-left: 20px;">
                <li>Selecciona un instrument de la llista.</li>
                <li>Fes clic als dies del calendari que necessitis.</li>
                <li>Emplena el teu Nom i DNI per generar el document en PDF.</li>
                <li>Signa el PDF al teu ordinador i adjunta'l al formulari final.</li>
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
  background-image: linear-gradient(rgba(1, 33, 105, 0.75), rgba(1, 33, 105, 0.9)), url('/instrumentacion.jpg');
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
.generador-doc-box { background-color: #eef5fa; padding: 20px; border-radius: 8px; border: 1px dashed #0086c0; margin-bottom: 20px; }
.formulario-reserva { background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; margin-top: 15px; }
.form-grupo { margin-bottom: 15px; }
.form-grupo label { display: block; font-size: 0.85rem; color: #333; margin-bottom: 5px; font-weight: bold; }
.input-form { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.95rem; box-sizing: border-box; font-family: inherit;}
.file-input { background: white; font-size: 0.85rem; cursor: pointer; }

.btn-generar { width: 100%; background-color: #0086c0; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 5px; }
.btn-generar:hover:not(:disabled) { background-color: #006b99; }
.btn-generar:disabled { background-color: #a0cadd; cursor: not-allowed; }

.btn-submit { width: 100%; background-color: #012169; color: white; border: none; padding: 15px; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 10px; }
.btn-submit:hover:not(.btn-desactivado) { background-color: #0056b3; transform: translateY(-2px); }
.btn-desactivado { background-color: #ccc; cursor: not-allowed; }

.btn-cerrar { margin-top: 30px; width: 100%; background: #eee; color: #555; border: none; padding: 10px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; }
.btn-cerrar:hover { background: #e0e0e0; color: #333; }

@media (max-width: 992px) { 
  .grid-layout { grid-template-columns: 1fr; } 
}
</style>