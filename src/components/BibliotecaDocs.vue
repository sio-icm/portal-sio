<script setup>
import { ref, computed } from 'vue'

// Llista COMPLETA de documents amb rutes reals apuntant a public/manuals/
const documentos = ref([
  // --- ESTACIONS METEOROLÒGIQUES ---
  { id: 1, categoria: 'Estacions Meteorològiques', fabricante: 'Davis Instruments', titulo: 'Manual Consola Vantage Pro2', descripcion: 'Manual complet de l\'estació meteorològica Vantage Pro2.', formato: 'PDF', enlace: '/manuals/Vantage_pro2_console_manual.pdf' },
  { id: 2, categoria: 'Estacions Meteorològiques', fabricante: 'Davis Instruments', titulo: 'Manual de Instalación Vantage Pro/Pro2', descripcion: 'Guia completa d\'instal·lació i muntatge de màstil.', formato: 'PDF', enlace: '/manuals/Installation_vantage.pdf' },
  { id: 3, categoria: 'Estacions Meteorològiques', fabricante: 'Davis Instruments', titulo: 'Guía de Inicio WeatherLink Software', descripcion: 'Guia del programari WeatherLink per a PC.', formato: 'PDF', enlace: '/manuals/Weatherlink_software_getting_started_guide... 1_28.pdf' },
  { id: 4, categoria: 'Estacions Meteorològiques', fabricante: 'Davis Instruments', titulo: 'Manual Sensores UV y Radiación Solar', descripcion: 'Manual tècnic de sensors UV i radiació solar.', formato: 'PDF', enlace: '/manuals/Uv_and_solar_Vantage_pro.pdf' },

  // --- REGISTRADORS DE DADES ---
  { id: 6, categoria: 'Registradors de Dades (Data Loggers)', fabricante: 'RBR Ltd.', titulo: 'Manual de Usuario RBR Logger', descripcion: 'Operació per a registradors RBR.', formato: 'PDF', enlace: '/manuals/Rbr_logger_users_manual.pdf' },

  // --- PERFILADORS ACÚSTICS (ADCP) ---
  { id: 7, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Principios de Operación de ADCP', descripcion: 'Fonaments teòrics del perfilador acústic Doppler.', formato: 'PDF', enlace: '/manuals/ADCP_principles_operation.pdf' },
  { id: 8, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Manual Técnico WorkHorse ADCP', descripcion: 'Especificacions tècniques detallades del hardware WorkHorse.', formato: 'PDF', enlace: '/manuals/WorkHorse_Technical_Manual.pdf' },
  { id: 9, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Manual de Comandos y Formato de Datos', descripcion: 'Comandaments de configuració.', formato: 'PDF', enlace: '/manuals/WorkHorse_Commands_and_Output_Data_Format.pdf' },
  { id: 10, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Manual de Usuario WorkHorse ADCP', descripcion: 'Instal·lació, operació i desplegament.', formato: 'PDF', enlace: '/manuals/WorkHorse_Users_Guide.pdf' },
  { id: 11, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Manual de Usuario VmDas', descripcion: 'Programari d\'adquisició de dades en temps real.', formato: 'PDF', enlace: '/manuals/VmDas_Users_Guide.pdf' },
  { id: 12, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Guía Rápida VmDas', descripcion: 'Inici ràpid VmDas.', formato: 'PDF', enlace: '/manuals/VmDas_Quick_Start_Guide.pdf' },
  { id: 13, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Manual de Usuario WinRiver II', descripcion: 'Programari de processament de dades.', formato: 'PDF', enlace: '/manuals/WinRiver_II_User_Guide.pdf' },
  { id: 14, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Guía Rápida WinRiver II', descripcion: 'Inici ràpid WinRiver II.', formato: 'PDF', enlace: '/manuals/WinRiver_II_Quick_Start_Guide.pdf' },
  { id: 15, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Manual Sección por Sección WinRiver', descripcion: 'Guia detallada de WinRiver.', formato: 'PDF', enlace: '/manuals/WinRiver_Section_By_Section_User_Guide.pdf' },
  { id: 16, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Guía Rápida Sección por Sección WinRiver', descripcion: 'Inici ràpid per seccions.', formato: 'PDF', enlace: '/manuals/WinRiver_Section_By_Section_Quick_Start.pdf' },
  { id: 17, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Manual de Usuario WinADCP', descripcion: 'Visualització i anàlisi de perfils.', formato: 'PDF', enlace: '/manuals/WinADCP_User_Guide.pdf' },
  { id: 18, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Manual de Usuario WinSC y PlanADCP', descripcion: 'Planificació de desplegaments.', formato: 'PDF', enlace: '/manuals/WinSC_PlanADCP_User_Guide.pdf' },
  { id: 19, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Teledyne RD Instruments', titulo: 'Manual de Usuario RDI Tools', descripcion: 'Eines de diagnòstic i actualització.', formato: 'PDF', enlace: '/manuals/RDI_Tools_User_Guide.pdf' },
  { id: 20, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Nortek', titulo: 'Manual Aquadopp', descripcion: 'Manual d\'usuari del perfilador Aquadopp.', formato: 'PDF', enlace: '/manuals/Aquadopp_Manual.pdf' },
  { id: 21, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'SonTek / Xylem', titulo: 'Manual SonTek ADP v7.10', descripcion: 'Manual complet del perfilador acústic.', formato: 'PDF', enlace: '/manuals/SonTek_ADP_Manual_v710.pdf' },
  { id: 22, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Aplicacions', titulo: 'PCADP en Medición de Oleaje', descripcion: 'Tècniques de mesura d\'ones.', formato: 'PDF', enlace: '/manuals/PCADP_in_waves.pdf' },
  { id: 23, categoria: 'Perfiladors Acústics (ADCP)', fabricante: 'Aplicacions', titulo: 'Estimaciones Velocidad Cizalla', descripcion: 'Estudi en Grays Harbor.', formato: 'PDF', enlace: '/manuals/Shear_velocity_estimates_inner_shelf_Grays_Harbor.pdf' },

  // --- SONDES CTD ---
  { id: 24, categoria: 'Sondes CTD', fabricante: 'Sea & Sun Technology', titulo: 'Manual de Usuario Sea & Sun CTD', descripcion: 'Configuració i manteniment.', formato: 'PDF', enlace: '/manuals/Sea_Sun_User_Manual.pdf' },
  { id: 25, categoria: 'Sondes CTD', fabricante: 'Sea & Sun Technology', titulo: 'Manual CTD60M V2', descripcion: 'Manual d\'usuari CTD 60M.', formato: 'PDF', enlace: '/manuals/SeaSun_CTD60M_Manual_V2.pdf' },
  { id: 26, categoria: 'Sondes CTD', fabricante: 'Sea & Sun Technology', titulo: 'Calibración CTD SN 180', descripcion: 'Certificat de calibratge (2023).', formato: 'PDF', enlace: '/manuals/SeaSun_CTD_SN180_Calibracion_230525.pdf' },
  { id: 27, categoria: 'Sondes CTD', fabricante: 'Sea & Sun Technology', titulo: 'Manual 154', descripcion: 'Manual tècnic addicional.', formato: 'PDF', enlace: '/manuals/SeaSun_Manual_154.pdf' },
  { id: 28, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Manual SBE 19plus V2 SeaCAT CTD', descripcion: 'Sonda multiparamètrica.', formato: 'PDF', enlace: '/manuals/19plus_V2_SeaCAT318_revH.pdf' },
  { id: 29, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Guía Rápida SBE 19plus', descripcion: 'Instruccions de perfilat.', formato: 'PDF', enlace: '/manuals/SBE_Quickstart_19plus.pdf' },
  { id: 30, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Manual SBE 37-SI MicroCAT CTD', descripcion: 'CTD autònom.', formato: 'PDF', enlace: '/manuals/SBE_37-SI_-_Manual.pdf' },
  { id: 31, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Manual SBE-44 Subsea Pressure Sensor', descripcion: 'Sensor de pressió submarina.', formato: 'PDF', enlace: '/manuals/Manual-SBE-44_024.pdf' },
  { id: 32, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Manual Seasave v7.26', descripcion: 'Programari d\'adquisició.', formato: 'PDF', enlace: '/manuals/Seasave_Manual_v7.26.pdf' },
  { id: 33, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Manual SBE Data Processing v7.26', descripcion: 'Post-processament.', formato: 'PDF', enlace: '/manuals/SBE_Data_Processing_Manual_v7.26.pdf' },
  { id: 34, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'App Note 31: Cálculo Salinidad', descripcion: 'Algoritmes TEOS-10.', formato: 'PDF', enlace: '/manuals/SBE_AppNote31_Computation_Salinity.pdf' },
  { id: 35, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'App Note 45: Corrección Masa Térmica', descripcion: 'Efectes d\'inèrcia.', formato: 'PDF', enlace: '/manuals/SBE_AppNote45_Thermal_Mass.pdf' },
  { id: 36, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'App Note 47: Alineación de Sensores', descripcion: 'Alineació temporal.', formato: 'PDF', enlace: '/manuals/SBE_AppNote47_Sensor_Alignment.pdf' },
  { id: 37, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'App Note 57: Procesamiento Datos', descripcion: 'Control de qualitat.', formato: 'PDF', enlace: '/manuals/SBE_AppNote57_Data_Processing.pdf' },
  { id: 38, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'App Note 64: Calibración de Sensores', descripcion: 'Procediments de calibratge.', formato: 'PDF', enlace: '/manuals/SBE_AppNote64_Sensor_Calibration.pdf' },
  { id: 39, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'App Note 64-3: Calibración Oxígeno', descripcion: 'Mètode Winkler.', formato: 'PDF', enlace: '/manuals/SBE_AppNote64-3_DO_Calibration.pdf' },
  { id: 40, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Ref. Técnica: Sensores de Conductividad', descripcion: 'Tipus i especificacions.', formato: 'PDF', enlace: '/manuals/SBE_Tech_Ref_Conductivity_Sensors.pdf' },
  { id: 41, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Módulo 7: Máxima Precisión', descripcion: 'Formació tècnica.', formato: 'PDF', enlace: '/manuals/SBE_Training_Module7_HighestAccuracy.pdf' },
  { id: 42, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Módulo 15: Resolución de Problemas', descripcion: 'Formació tècnica.', formato: 'PDF', enlace: '/manuals/SBE_Training_Module15_Troubleshooting.pdf' },
  { id: 43, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Módulo 17: Mantenimiento', descripcion: 'Formació tècnica.', formato: 'PDF', enlace: '/manuals/SBE_Training_Module17_Maintenance.pdf' },
  { id: 44, categoria: 'Sondes CTD', fabricante: 'Sea-Bird Scientific', titulo: 'Módulo 18: Servicio Técnico', descripcion: 'Formació tècnica.', formato: 'PDF', enlace: '/manuals/SBE_Training_Module18_Servicing.pdf' },

  // --- SENSORS ÒPTICS ---
  { id: 45, categoria: 'Sensors Òptics', fabricante: 'TriOS', titulo: 'Manual IMMSpec', descripcion: 'Espectròmetre submergible.', formato: 'PDF', enlace: '/manuals/Manual-IMMSpec_013.pdf' },
  { id: 46, categoria: 'Sensors Òptics', fabricante: 'Seapoint Sensors', titulo: 'Manual Seapoint Turbidity Meter', descripcion: 'Mesura de terbolesa.', formato: 'PDF', enlace: '/manuals/Seapoint_Turbidity_Meter.pdf' },

  // --- ALTRES EQUIPS ---
  { id: 47, categoria: 'Sensors Acústics de Sediments', fabricante: 'Aquatec Group', titulo: 'Manual Sistema ABS Aquatec', descripcion: 'Concentració de sediments.', formato: 'PDF', enlace: '/manuals/Aquatec_ABS_System_Manual.pdf' },
  { id: 48, categoria: 'Sensors de Temperatura', fabricante: 'Oceano Technology', titulo: 'Manual Oceano TT801', descripcion: 'Transductor d\'alta precisió.', formato: 'PDF', enlace: '/manuals/Oceano_TT801_Manual.pdf' },
  { id: 49, categoria: 'Instrumentació de Laboratori', fabricante: 'General', titulo: 'Manual EC300', descripcion: 'Mesurador de conductivitat.', formato: 'PDF', enlace: '/manuals/EC300-Manual.pdf' },
  { id: 50, categoria: 'Infraestructura de Suport', fabricante: 'GGM', titulo: 'Manual Máquina de Hielo GGM', descripcion: 'Manteniment.', formato: 'PDF', enlace: '/manuals/ICE_MAKER_MANUAL-GGM.pdf' },
  { id: 51, categoria: 'Sistemes d\'Alimentació', fabricante: 'Morningstar', titulo: 'Manual SunSaver', descripcion: 'Controlador de càrrega solar.', formato: 'PDF', enlace: '/manuals/SunSaver_manual_de_uso_e_instalacion.pdf' },

  // --- DOCS I PROJECTES ---
  { id: 52, categoria: 'Material Didàctic', fabricante: 'General', titulo: 'Introducció a l\'Oceanografia Física', descripcion: 'Conceptes fonamentals.', formato: 'DOC', enlace: '/manuals/Una_Introducción_a_la_Oceanografía_Física.doc' },
  { id: 53, categoria: 'Tècniques de Mostreig', fabricante: 'Universitat de Perpinyà', titulo: 'Técnicas de Muestreo (1990)', descripcion: 'Metodologies històriques.', formato: 'PDF', enlace: '/manuals/1990_Universite_Perpignan_Techniques_Prelevement.pdf' },
  { id: 54, categoria: 'Projectes i Sistemes', fabricante: 'ICM - CSIC', titulo: 'SPY-ICM', descripcion: 'Documentació del sistema.', formato: 'PDF', enlace: '/manuals/SPY-ICM.pdf' },
  { id: 55, categoria: 'Treballs (TFG)', fabricante: 'General', titulo: 'TFG - Oriol Mulet Morales', descripcion: 'Documentació.', formato: 'PDF', enlace: '/manuals/Mulet_Morales_Oriol_TFG.pdf' }
])

const buscador = ref('')
const mostrarFormulario = ref(false)

const nuevoDoc = ref({
  titulo: '',
  descripcion: '',
  categoria: '',
  fabricante: '',
  formato: 'PDF',
  enlace: '#'
})

const documentosFiltrados = computed(() => {
  if (!buscador.value) return documentos.value
  const query = buscador.value.toLowerCase()
  return documentos.value.filter(doc => 
    doc.titulo.toLowerCase().includes(query) || 
    doc.fabricante.toLowerCase().includes(query) ||
    doc.categoria.toLowerCase().includes(query)
  )
})

const bibliotecaAgrupada = computed(() => {
  const grupos = {}
  documentosFiltrados.value.forEach(doc => {
    if (!grupos[doc.categoria]) grupos[doc.categoria] = {}
    if (!grupos[doc.categoria][doc.fabricante]) grupos[doc.categoria][doc.fabricante] = []
    grupos[doc.categoria][doc.fabricante].push(doc)
  })
  return grupos
})

const acordeonesAbiertos = ref({})

const toggleCategoria = (categoria) => {
  if (acordeonesAbiertos.value[categoria] === undefined) {
    acordeonesAbiertos.value[categoria] = true
  }
  acordeonesAbiertos.value[categoria] = !acordeonesAbiertos.value[categoria]
}

const agregarDocumento = () => {
  if (!nuevoDoc.value.titulo || !nuevoDoc.value.categoria || !nuevoDoc.value.fabricante) {
    alert("Por favor, rellena los campos obligatorios")
    return
  }
  documentos.value.push({
    id: Date.now(),
    titulo: nuevoDoc.value.titulo,
    descripcion: nuevoDoc.value.descripcion,
    categoria: nuevoDoc.value.categoria,
    fabricante: nuevoDoc.value.fabricante,
    formato: nuevoDoc.value.formato,
    enlace: nuevoDoc.value.enlace
  })
  acordeonesAbiertos.value[nuevoDoc.value.categoria] = true
  nuevoDoc.value = { titulo: '', descripcion: '', categoria: '', fabricante: '', formato: 'PDF', enlace: '#' }
  mostrarFormulario.value = false
  alert("✅ Document afegit correctament a la biblioteca!")
}

const getIconoFormato = (formato) => {
  if (formato === 'PDF') return '📄'
  if (formato === 'JPG' || formato === 'PNG') return '🖼️'
  if (formato === 'DOC' || formato === 'DOCX') return '📝'
  return '📁'
}
</script>

<template>
  <div class="panel-biblioteca">
    <div class="cabecera-panel">
      <div>
        <h2>📚 Biblioteca Tècnica i Manuals SIO</h2>
        <p class="subtitulo-panel">Repositori de documentació d'equips del servei.</p>
      </div>
      <div class="acciones-cabecera">
        <input v-model="buscador" type="text" class="buscador-docs" placeholder="🔍 Cercar manual o fabricant...">
        <button @click="mostrarFormulario = !mostrarFormulario" class="btn-nou-doc">
          {{ mostrarFormulario ? '❌ Cancel·lar' : '+ Pujar Document' }}
        </button>
      </div>
    </div>

    <div v-if="mostrarFormulario" class="formulario-doc-box">
      <h3>➕ Afegir Nou Document a la Biblioteca</h3>
      <form @submit.prevent="agregarDocumento" class="grid-form-docs">
        <div class="campo">
          <label>Títol del Document / Manual: *</label>
          <input v-model="nuevoDoc.titulo" placeholder="Ex: Manual Técnico WorkHorse ADCP" required>
        </div>
        <div class="campo-doble">
          <div class="subcampo">
            <label>Categoria del Sistema: *</label>
            <select v-model="nuevoDoc.categoria" required>
              <option value="" disabled selected>Selecciona Categoria</option>
              <option value="Sondes CTD">Sondes CTD</option>
              <option value="Perfiladors Acústics (ADCP)">Perfiladors Acústics (ADCP)</option>
              <option value="Estacions Meteorològiques">Estacions Meteorològiques</option>
              <option value="Sensors Òptics">Sensors Òptics</option>
              <option value="Material Didàctic">Material Didàctic</option>
            </select>
          </div>
          <div class="subcampo">
            <label>Fabricant / Proveïdor: *</label>
            <input v-model="nuevoDoc.fabricante" placeholder="Ex: Teledyne RDI, Sea-Bird, Davis">
          </div>
        </div>
        <div class="campo-doble">
          <div class="subcampo">
            <label>Format de l'arxiu:</label>
            <select v-model="nuevoDoc.formato">
              <option value="PDF">PDF</option>
              <option value="JPG">JPG / Imatge</option>
              <option value="DOC">DOC / Word</option>
              <option value="ZIP">ZIP / Rar</option>
            </select>
          </div>
          <div class="subcampo">
            <label>Ruta de l'arxiu o Enllaç (Opcional):</label>
            <input v-model="nuevoDoc.enlace" placeholder="Ex: /manuals/manual_adcp.pdf">
          </div>
        </div>
        <div class="campo">
          <label>Descripció del contingut (Estil WikiSIO):</label>
          <textarea v-model="nuevoDoc.descripcion" rows="3" placeholder="Escriu els punts clau..."></textarea>
        </div>
        <button type="submit" class="btn-guardar-doc">💾 Desar a la Biblioteca</button>
      </form>
    </div>

    <div class="contenedor-biblioteca">
      <div v-for="(fabricantes, categoria) in bibliotecaAgrupada" :key="categoria" class="grupo-categoria">
        <div class="header-categoria" @click="toggleCategoria(categoria)">
          <h3>📁 {{ categoria }}</h3>
          <span class="icono-desplegable">{{ acordeonesAbiertos[categoria] !== false ? '▼' : '▶' }}</span>
        </div>
        <div v-show="acordeonesAbiertos[categoria] !== false" class="cuerpo-categoria">
          <div v-for="(docs, fabricante) in fabricantes" :key="fabricante" class="grupo-fabricante">
            <h4 class="titulo-fabricante">🛠️ {{ fabricante }}</h4>
            <div class="grid-documentos">
              <div v-for="doc in docs" :key="doc.id" class="tarjeta-documento">
                <div class="icono-doc">{{ getIconoFormato(doc.formato) }}</div>
                <div class="info-doc">
                  <h5>{{ doc.titulo }}</h5>
                  <p class="desc-wiki">{{ doc.descripcion || 'Sense descripció disponible.' }}</p>
                  <div class="pie-tarjeta">
                    <span class="badge-formato">{{ doc.formato }}</span>
                    <a :href="'/portal-sio' + doc.enlace" target="_blank" class="btn-descargar">Descarregar</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="Object.keys(bibliotecaAgrupada).length === 0" class="mensaje-vacio">
        No s'ha trobat cap document que coincideixi amb la cerca.
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-biblioteca { background: #ffffff; border-radius: 10px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-top: 20px; border-top: 4px solid #17a2b8; }
.cabecera-panel { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px; border-bottom: 2px solid #eee; padding-bottom: 20px; }
.cabecera-panel h2 { color: #012169; margin: 0 0 5px 0; font-size: 1.6rem; }
.subtitulo-panel { color: #666; margin: 0; font-size: 0.95rem; }
.acciones-cabecera { display: flex; gap: 15px; }

.buscador-docs { padding: 10px 15px; border: 1px solid #ccc; border-radius: 6px; width: 250px; font-size: 0.95rem; }
.btn-nou-doc { background: #17a2b8; color: white; padding: 10px 20px; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; transition: background 0.2s; }
.btn-nou-doc:hover { background: #117a8b; }

.formulario-doc-box { background: #f8f9fa; border: 1px solid #dee2e6; padding: 25px; border-radius: 8px; margin-bottom: 30px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02); }
.formulario-doc-box h3 { color: #012169; margin-top: 0; margin-bottom: 20px; font-size: 1.2rem; border-bottom: 1px solid #ddd; padding-bottom: 8px; }
.grid-form-docs { display: flex; flex-direction: column; gap: 15px; max-width: 700px; }
.grid-form-docs label { font-size: 0.85rem; font-weight: bold; color: #444; margin-bottom: 5px; display: block; }
.grid-form-docs input, .grid-form-docs select, .grid-form-docs textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: 100%; box-sizing: border-box; font-family: inherit; }
.campo-doble { display: flex; gap: 15px; }
.subcampo { flex: 1; }
.btn-guardar-doc { background: #012169; color: white; border: none; padding: 12px; font-weight: bold; border-radius: 4px; cursor: pointer; margin-top: 5px; transition: background 0.2s; width: 200px; }
.btn-guardar-doc:hover { background: #0086c0; }

.grupo-categoria { margin-bottom: 15px; border: 1px solid #e0e6ed; border-radius: 8px; overflow: hidden; }
.header-categoria { background: #f8fcfd; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.header-categoria:hover { background: #eef7f9; }
.header-categoria h3 { margin: 0; color: #012169; font-size: 1.15rem; }
.cuerpo-categoria { padding: 20px; background: white; border-top: 1px solid #e0e6ed; }
.titulo-fabricante { color: #666; margin: 0 0 15px 0; font-size: 1rem; padding-bottom: 5px; border-bottom: 2px dashed #eee; }
.grupo-fabricante { margin-bottom: 25px; }
.grupo-fabricante:last-child { margin-bottom: 0; }

.grid-documentos { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.tarjeta-documento { display: flex; gap: 15px; padding: 15px; border: 1px solid #eee; border-radius: 8px; background: #fdfdfd; transition: all 0.2s; }
.tarjeta-documento:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); background: white; border-color: #b3d7ff; }
.icono-doc { font-size: 2.3rem; }
.info-doc { flex-grow: 1; display: flex; flex-direction: column; }
.info-doc h5 { margin: 0 0 5px 0; color: #012169; font-size: 1rem; }
.desc-wiki { margin: 0 0 15px 0; color: #555; font-size: 0.85rem; line-height: 1.4; flex-grow: 1; white-space: pre-line; }
.pie-tarjeta { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.badge-formato { background: #e1eef5; color: #0086c0; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
.btn-descargar { background: #f4f7f9; color: #012169; text-decoration: none; padding: 5px 12px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; border: 1px solid #ccc; }
.btn-descargar:hover { background: #012169; color: white; border-color: #012169; }

.mensaje-vacio { text-align: center; padding: 40px; color: #777; font-style: italic; }
</style>