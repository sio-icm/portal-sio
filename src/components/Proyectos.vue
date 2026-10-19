<script setup>
import { ref, computed, onMounted } from 'vue'

const proyectos = ref([])
const cargando = ref(true)
const errorCarga = ref(false)
const descripcionesVisibles = ref({})

// Estado guardado en la base de datos -> grupo de la página
const GRUPO_POR_ESTADO = {
  'En Curs': 'enCurso',
  'Aprovat': 'aprobados',
  'Sol·licitat': 'solicitados',
  'Finalitzat': 'finalizados'
}
const proyectosDe = (grupo) => proyectos.value.filter(p => GRUPO_POR_ESTADO[p.estado] === grupo)

const enCurso = computed(() => proyectosDe('enCurso'))
// Columna derecha: solo los grupos que tienen algún proyecto
const gruposDerecha = computed(() =>
  ['aprobados', 'solicitados', 'finalizados']
    .map(grupo => ({ grupo, lista: proyectosDe(grupo) }))
    .filter(g => g.lista.length > 0)
)

// Carga los proyectos reales de la base de datos
const cargarProyectos = async () => {
  try {
    const res = await fetch('/api/proyectos')
    if (!res.ok) throw new Error(res.status)
    proyectos.value = await res.json()
  } catch (error) {
    console.error("Error cargando proyectos:", error)
    errorCarga.value = true
  } finally {
    cargando.value = false
  }
}

onMounted(cargarProyectos)

const toggleDesc = (id) => {
  descripcionesVisibles.value[id] = !descripcionesVisibles.value[id]
}

// Categoría guardada en la base de datos -> clave de traducción y color
const CATEGORIAS = {
  'Infraestructura': { clave: 'infraestructura', clase: 'badge-verde' },
  'Contrato': { clave: 'contrato', clase: 'badge-turquesa' },
  'Plan Nacional': { clave: 'planNacional', clase: 'badge-amarillo' },
  'I+D+I': { clave: 'idi', clase: 'badge-gris' },
  'Divulgació científica': { clave: 'divulgacion', clase: 'badge-morado' },
  'Divulgación científica': { clave: 'divulgacion', clase: 'badge-morado' },
  'Otro': { clave: 'otro', clase: 'badge-naranja' }
}
const clasePorTipo = (categoria) => CATEGORIAS[categoria]?.clase || 'badge-gris'
</script>

<template>
  <div class="proyectos-hub">
    <div class="fondo-proyectos"></div>

    <div class="contenedor-ancho contenido-hub">
      <h1 class="titulo-seccion">{{ $t('proyectos.titulo') }}</h1>
      <p class="subtitulo">{{ $t('proyectos.subtitulo') }}</p>

      <div class="grid-horizontal">

        <div class="columna-esquerra">
          <div class="seccion-bloque">
            <div class="cabecera-bloque">
              <h2 class="titulo-fija">{{ $t('proyectos.grupos.enCurso.titulo') }}</h2>
              <p>{{ $t('proyectos.grupos.enCurso.texto') }}</p>
            </div>
            <p v-if="cargando" class="aviso-lista">{{ $t('proyectos.cargando') }}</p>
            <p v-else-if="errorCarga" class="aviso-lista">{{ $t('proyectos.errorCarga') }}</p>
            <p v-else-if="enCurso.length === 0" class="aviso-lista">{{ $t('proyectos.vacio') }}</p>
            <div class="contenedor-proyectos">
              <div v-for="p in enCurso" :key="p.id" class="mini-tarjeta">
                <div class="header-mini">
                  <span :class="['badge-tipo', clasePorTipo(p.categoria)]">{{ CATEGORIAS[p.categoria] ? $t(`proyectos.categorias.${CATEGORIAS[p.categoria].clave}`) : p.categoria }}</span>
                </div>
                <h3>{{ p.titulo }}</h3>
                <p class="desc-corta">{{ p.descripcion_corta }}</p>

                <button v-show="!descripcionesVisibles[p.id]" @click="toggleDesc(p.id)" class="btn-toggle">▼ {{ $t('proyectos.detalle') }}</button>
                <div v-show="descripcionesVisibles[p.id]" class="caja-detalle">
                  <div class="contenido-html" v-html="p.descripcion_ampliada"></div>
                  <button @click="toggleDesc(p.id)" class="btn-toggle-cerrar">▲ {{ $t('proyectos.ocultarDetalle') }}</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="columna-dreta" style="display: flex; flex-direction: column; gap: 30px;">
          <div v-for="{ grupo, lista } in gruposDerecha" :key="grupo" class="seccion-bloque">
            <div class="cabecera-bloque">
              <h2 class="titulo-fija">{{ $t(`proyectos.grupos.${grupo}.titulo`) }}</h2>
              <p>{{ $t(`proyectos.grupos.${grupo}.texto`) }}</p>
            </div>
            <div class="contenedor-proyectos">
              <div v-for="p in lista" :key="p.id" class="mini-tarjeta">
                <div class="header-mini">
                  <span :class="['badge-tipo', clasePorTipo(p.categoria)]">{{ CATEGORIAS[p.categoria] ? $t(`proyectos.categorias.${CATEGORIAS[p.categoria].clave}`) : p.categoria }}</span>
                </div>
                <h3>{{ p.titulo }}</h3>
                <p class="desc-corta">{{ p.descripcion_corta }}</p>

                <button v-show="!descripcionesVisibles[p.id]" @click="toggleDesc(p.id)" class="btn-toggle">▼ {{ $t('proyectos.detalle') }}</button>
                <div v-show="descripcionesVisibles[p.id]" class="caja-detalle">
                  <div class="contenido-html" v-html="p.descripcion_ampliada"></div>
                  <button @click="toggleDesc(p.id)" class="btn-toggle-cerrar">▲ {{ $t('proyectos.ocultarDetalle') }}</button>
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
.aviso-lista { color: #666; font-style: italic; margin: 10px 0; }
.proyectos-hub { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-proyectos { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-image: linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('/pecesaguasalada.webp'); background-size: cover; background-position: center; background-repeat: no-repeat; z-index: 0; }
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