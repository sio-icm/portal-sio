<script setup>
import { ref, computed, onMounted } from 'vue'

const proyectos = ref([]) 
const descripcionesVisibles = ref({})

// Filtres dinàmics
const enCurso = computed(() => proyectos.value.filter(p => p.estado === 'En Curs'));
const solicitados = computed(() => proyectos.value.filter(p => p.estado === 'Sol·licitat'));
const aprovados = computed(() => proyectos.value.filter(p => p.estado === 'Aprovat'));
const finalizados = computed(() => proyectos.value.filter(p => p.estado === 'Finalitzat'));

// Funció per carregar els projectes reals de la BD
const cargarProyectos = async () => {
  try {
    const res = await fetch('http://localhost:5000/api/proyectos')
    proyectos.value = await res.json()
  } catch (error) {
    console.error("Error carregant projectes:", error)
  }
}

onMounted(cargarProyectos)

const toggleDesc = (id) => {
  descripcionesVisibles.value[id] = !descripcionesVisibles.value[id]
}

const clasePorTipo = (tipo) => {
  switch (tipo) {
    case 'Infraestructura': return 'badge-verde';
    case 'Contrato': return 'badge-turquesa';
    case 'Plan Nacional': return 'badge-amarillo';
    case 'Otro': return 'badge-naranja';
    case 'Divulgación científica': return 'badge-morado';
    default: return 'badge-gris';
  }
}
</script>

<template>
  <div class="proyectos-hub">
    <div class="fondo-proyectos"></div>

    <div class="contenedor-ancho contenido-hub">
      <h1 class="titulo-seccion">Proyectos y Campañas</h1>
      <p class="subtitulo">Visualiza el estado actual de los proyectos técnicos y las solicitudes en curso del servicio.</p>

      <div class="grid-horizontal">

        <div class="columna-esquerra">
          <div class="seccion-bloque">
            <div class="cabecera-bloque">
              <h2 class="titulo-fija">En Curso</h2>
              <p>Actividades y campañas en fase de ejecución técnica actualmente.</p>
            </div>
            <div class="contenedor-proyectos">
              <div v-for="p in enCurso" :key="p.id" class="mini-tarjeta">
                <div class="header-mini">
                  <span :class="['badge-tipo', clasePorTipo(p.categoria)]">{{ p.categoria }}</span>
                </div>
                <h3>{{ p.titulo }}</h3>
                <p class="desc-corta">{{ p.descripcion_corta }}</p>
                
                <button v-show="!descripcionesVisibles[p.id]" @click="toggleDesc(p.id)" class="btn-toggle">
                  ▼ Detall
                </button>
                <div v-show="descripcionesVisibles[p.id]" class="caja-detalle">
                  <div class="contenido-html" v-html="p.descripcion_ampliada"></div>
                  <button @click="toggleDesc(p.id)" class="btn-toggle-cerrar">▲ Amagar detall</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="columna-dreta" style="display: flex; flex-direction: column; gap: 30px;">
          
          <div class="seccion-bloque" v-if="aprovados.length > 0">
            <div class="cabecera-bloque">
              <h2 class="titulo-fija">Aprobados</h2>
              <p>Proyectos confirmados a la espera de inicio técnico.</p>
            </div>
            <div class="contenedor-proyectos">
              <div v-for="p in aprovados" :key="p.id" class="mini-tarjeta">
                <div class="header-mini">
                  <span :class="['badge-tipo', clasePorTipo(p.categoria)]">{{ p.categoria }}</span>
                </div>
                <h3>{{ p.titulo }}</h3>
                <p class="desc-corta">{{ p.descripcion_corta }}</p>
                
                <button v-show="!descripcionesVisibles[p.id]" @click="toggleDesc(p.id)" class="btn-toggle">▼ Detall</button>
                <div v-show="descripcionesVisibles[p.id]" class="caja-detalle">
                  <div class="contenido-html" v-html="p.descripcion_ampliada"></div>
                  <button @click="toggleDesc(p.id)" class="btn-toggle-cerrar">▲ Amagar detall</button>
                </div>
              </div>
            </div>
          </div>

          <div class="seccion-bloque" v-if="solicitados.length > 0">
            <div class="cabecera-bloque">
              <h2 class="titulo-fija">Solicitados</h2>
              <p>Propuestas en evaluación.</p>
            </div>
            <div class="contenedor-proyectos">
              <div v-for="p in solicitados" :key="p.id" class="mini-tarjeta">
                 <div class="header-mini"><span :class="['badge-tipo', clasePorTipo(p.categoria)]">{{ p.categoria }}</span></div>
                 <h3>{{ p.titulo }}</h3>
                 <p class="desc-corta">{{ p.descripcion_corta }}</p>
                 
                 <button v-show="!descripcionesVisibles[p.id]" @click="toggleDesc(p.id)" class="btn-toggle">▼ Detall</button>
                 <div v-show="descripcionesVisibles[p.id]" class="caja-detalle">
                   <div class="contenido-html" v-html="p.descripcion_ampliada"></div>
                   <button @click="toggleDesc(p.id)" class="btn-toggle-cerrar">▲ Amagar detall</button>
                 </div>
              </div>
            </div>
          </div>

          <div class="seccion-bloque" v-if="finalizados.length > 0">
            <div class="cabecera-bloque">
              <h2 class="titulo-fija">Finalizados</h2>
              <p>Histórico de campañas y proyectos concluidos.</p>
            </div>
            <div class="contenedor-proyectos">
              <div v-for="p in finalizados" :key="p.id" class="mini-tarjeta">
                 <div class="header-mini"><span :class="['badge-tipo', clasePorTipo(p.categoria)]">{{ p.categoria }}</span></div>
                 <h3>{{ p.titulo }}</h3>
                 <p class="desc-corta">{{ p.descripcion_corta }}</p>
                 
                 <button v-show="!descripcionesVisibles[p.id]" @click="toggleDesc(p.id)" class="btn-toggle">▼ Detall</button>
                 <div v-show="descripcionesVisibles[p.id]" class="caja-detalle">
                   <div class="contenido-html" v-html="p.descripcion_ampliada"></div>
                   <button @click="toggleDesc(p.id)" class="btn-toggle-cerrar">▲ Amagar detall</button>
                 </div>
              </div>
            </div>
          </div>

        </div>

      </div> 
    </div> 
  </div> 
</template>

<style scoped>
.proyectos-hub { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-proyectos { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-image: linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('/pecesaguasalada.jpg'); background-size: cover; background-position: center; background-repeat: no-repeat; z-index: 0; }
.contenido-hub { position: relative; z-index: 10; padding-top: 120px; }
.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 40px; max-width: 800px; }
.grid-horizontal { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
.seccion-bloque { background: white; border-radius: 12px; padding: 35px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15); display: flex; flex-direction: column; }
.titulo-fija { color: #012169; margin-top: 0; font-size: 1.6rem; margin-bottom: 10px; }
.cabecera-bloque p { color: #666; font-size: 0.95rem; line-height: 1.4; margin-bottom: 25px; }
.contenedor-proyectos { display: flex; flex-direction: column; gap: 15px; }

.mini-tarjeta { background: #fdfdfd; border-left: 4px solid #0086c0; padding: 15px; border-radius: 4px 8px 8px 4px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05); transition: transform 0.2s, box-shadow 0.2s; }
.mini-tarjeta:hover { transform: translateX(5px); background: white; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); }
.header-mini { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.mini-tarjeta h3 { margin: 5px 0 0 0; font-size: 1.2rem; color: #012169; }
.desc-corta { font-size: 0.9rem; color: #555; font-style: italic; margin-top: 5px; }

/* --- ETIQUETAS --- */
.badge-tipo { font-size: 0.75rem; font-weight: bold; padding: 4px 10px; border-radius: 20px; color: white; }
.badge-verde { background-color: #28a745; }
.badge-turquesa { background-color: #17a2b8; }
.badge-amarillo { background-color: #ffc107; color: #333; }
.badge-naranja { background-color: #fd7e14; }
.badge-morado { background-color: #6f42c1; }
.badge-gris { background-color: #6c757d; }

/* --- CAJA DE DETALLE Y BOTONES --- */
.btn-toggle { background: none; border: none; color: #0086c0; font-weight: bold; cursor: pointer; padding: 0; margin-top: 10px; font-size: 0.9rem; }
.btn-toggle:hover { text-decoration: underline; }
.caja-detalle { margin-top: 15px; background: #f4f7f9; padding: 20px; border-radius: 6px; border-left: 4px solid #0086c0; }
.btn-toggle-cerrar { margin-top: 15px; cursor: pointer; font-size: 0.85rem; font-weight: bold; background: #e0e6ed; color: #333; border: none; padding: 8px 15px; border-radius: 4px; transition: background 0.2s; }
.btn-toggle-cerrar:hover { background: #cbd3da; }

/* --- 📸 MAGIA PARA LAS IMÁGENES DEL EDITOR HTML --- */
.contenido-html {
  font-size: 0.95rem;
  color: #333;
  line-height: 1.6;
}

/* Forzamos a que cualquier foto subida no se salga de la tarjeta */
.contenido-html :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 15px 0;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  display: block;
}

/* Mejora para los párrafos y listas generados por el editor Quill */
.contenido-html :deep(p) { margin-bottom: 10px; }
.contenido-html :deep(ul), .contenido-html :deep(ol) { margin-left: 20px; margin-bottom: 10px; }

@media (max-width: 992px) {
  .grid-horizontal { grid-template-columns: 1fr; }
  .contenido-hub { padding-top: 150px; }
}
</style>