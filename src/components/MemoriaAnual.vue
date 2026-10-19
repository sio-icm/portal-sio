<script setup>
import { computed } from 'vue'
const fondoInstrumentacion = '/instrumentacion.webp'

// Ruta del PDF de la memoria (dentro de public/). Mientras esté vacía no se
// muestra el recuadro de descarga. Ejemplo: '/memorias/Memoria_SIO_2025.pdf'
const pdfMemoria = ''

// Año de la memoria y cifras (pendientes de verificar)
const anioMemoria = 2025
const metricas = [
  { valor: '24', clave: 'campanas' },
  { valor: '150+', clave: 'sensores' },
  { valor: '12', clave: 'fondeos' },
  { valor: '8', clave: 'proyectos' }
]

const backgroundStyle = computed(() => {
  return `linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('${fondoInstrumentacion}')`
})
</script>

<template>
  <div class="memoria-page">
    <div class="fondo-cabecera" :style="{ backgroundImage: backgroundStyle }"></div>
    
    <div class="contenedor-ancho contenido-pagina">
      <h1 class="titulo-seccion">{{ $t('memoria.titulo') }}</h1>
      <p class="subtitulo">{{ $t('memoria.subtitulo') }}</p>

      <div class="bloque-blanco">
        <h2>{{ $t('memoria.resumen', { anio: anioMemoria }) }}</h2>
        <p class="intro-memoria">{{ $t('memoria.intro') }}</p>
        
        <div class="grid-metricas">
          <div v-for="m in metricas" :key="m.clave" class="tarjeta-metrica">
            <span class="numero">{{ m.valor }}</span>
            <span class="etiqueta">{{ $t(`memoria.metricas.${m.clave}`) }}</span>
          </div>
        </div>

        <div v-if="pdfMemoria" class="caja-descarga">
          <div class="icono-doc">📄</div>
          <div>
            <h3>{{ $t('memoria.completa', { anio: anioMemoria }) }}</h3>
            <p>{{ $t('memoria.completaTexto') }}</p>
          </div>
          <a :href="pdfMemoria" class="btn-descarga" download>{{ $t('memoria.descargar') }}</a>
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
.bloque-blanco h2 { color: #012169; margin-top: 0; font-size: 1.8rem; border-bottom: 2px solid #eee; padding-bottom: 10px; }
.intro-memoria { color: #555; font-size: 1.05rem; line-height: 1.6; margin-bottom: 30px; }

.grid-metricas { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
.tarjeta-metrica { background: #f8f9fa; padding: 25px; border-radius: 8px; text-align: center; border: 1px solid #e9ecef; }
.numero { display: block; font-size: 2.5rem; font-weight: bold; color: #dc3545; margin-bottom: 5px; }
.etiqueta { font-size: 0.95rem; color: #666; font-weight: bold; text-transform: uppercase; }

.caja-descarga { display: flex; align-items: center; gap: 20px; background: #eaf2f8; padding: 25px; border-radius: 8px; border-left: 4px solid #0086c0; }
.icono-doc { font-size: 3rem; }
.caja-descarga h3 { margin: 0 0 5px 0; color: #012169; }
.caja-descarga p { margin: 0; color: #555; font-size: 0.95rem; }
.btn-descarga { margin-left: auto; background-color: #0086c0; color: white; padding: 12px 25px; border-radius: 6px; text-decoration: none; font-weight: bold; transition: background 0.3s; white-space: nowrap; }
.btn-descarga:hover { background-color: #012169; }

@media (max-width: 768px) { 
  .contenido-pagina { padding-top: 150px; } 
  .caja-descarga { flex-direction: column; text-align: center; } 
  .btn-descarga { margin-left: 0; margin-top: 15px; width: 100%; text-align: center; } 
}
</style>