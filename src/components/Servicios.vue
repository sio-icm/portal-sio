<script setup>
const emit = defineEmits(['cambiar-pagina'])
</script>

<template>
  <div class="servicios-hub">
    <div class="fondo-servicios"></div>
    <div class="contenedor-ancho contenido-hub">
      <h1 class="titulo-seccion">Nuestros Servicios</h1>
      <p class="subtitulo">Infraestructuras y soluciones tecnológicas para la comunidad científica marina.</p>

      <div class="grid-servicios">
        
        <div class="seccion-bloque" @click="$emit('cambiar-pagina', 'pelagia')">
          <div class="cabecera-bloque">
            <h2 class="titulo-fija">Embarcación Pelagia</h2>
            <p>Plataforma polivalente para trabajos de oceanografía costera, equipada para el despliegue de instrumentación y muestreo.</p>
          </div>
          <div class="lista-items">
            <div class="item-servicio"><span class="punto-azul">●</span><div>Operaciones de despliegue y recuperación de equipos.</div></div>
            <div class="item-servicio"><span class="punto-azul">●</span><div>Campañas de muestreo biológico, geológico y físico-químico.</div></div>
            <div class="item-servicio"><span class="punto-azul">●</span><div>Gestión logística y tripulación especializada.</div></div>
          </div>
        </div>

        <div class="seccion-bloque" @click="$emit('cambiar-pagina', 'instrumentacion')">
          <div class="cabecera-bloque">
            <h2 class="titulo-fija">Instrumentación</h2>
            <p>Acceso a una amplia gama de instrumentación oceanográfica y soporte técnico para su configuración.</p>
          </div>
          <div class="lista-items">
            <div class="item-servicio"><span class="punto-verde">●</span><div>Desarrollo y personalización de equipos a medida.</div></div>
            <div class="item-servicio"><span class="punto-verde">●</span><div>Sistemas de comunicaciones y telemetría submarina.</div></div>
            <div class="item-servicio"><span class="punto-verde">●</span><div>Mantenimiento preventivo y correctivo de sensores.</div></div>
          </div>
        </div>

        <div class="seccion-bloque" @click="$emit('cambiar-pagina', 'tanques')">
          <div class="cabecera-bloque">
            <h2 class="titulo-fija">Tanques de Pruebas</h2>
            <p>Alquiler de áreas experimentales para la validación y calibración de instrumentación en entornos controlados.</p>
          </div>
          <div class="lista-items">
            <div class="item-servicio"><span class="punto-azul">●</span><div>Ensayos de estanqueidad y flotabilidad para robótica.</div></div>
            <div class="item-servicio"><span class="punto-azul">●</span><div>Calibración de sensores acústicos y ópticos.</div></div>
            <div class="item-servicio"><span class="punto-azul">●</span><div>Soporte de ingeniería especializado durante los ensayos.</div></div>
          </div>
        </div>

        <div class="seccion-bloque" @click="$emit('cambiar-pagina', 'salinidad')">
          <div class="cabecera-bloque">
            <h2 class="titulo-fija">Análisis de Salinidad</h2>
            <p>Servicio de determinación precisa de salinidad en muestras de agua de mar y calibración mediante salinómetro.</p>
          </div>
          <div class="lista-items">
            <div class="item-servicio"><span class="punto-verde">●</span><div>Lectura de precisión con Standard Seawater.</div></div>
            <div class="item-servicio"><span class="punto-verde">●</span><div>Protocolo estricto de aclimatación de muestras.</div></div>
            <div class="item-servicio"><span class="punto-verde">●</span><div>Validación de datos de conductividad CTD.</div></div>
          </div>
        </div>
        
        <div class="seccion-bloque" @click="$emit('cambiar-pagina', 'fondeos')">
          <div class="cabecera-bloque">
            <h2 class="titulo-fija">Diseño e Instalación de Fondeos</h2>
            <p>Planificación técnica, integración de sensores y despliegue en el mar de fondeos fijos y trípodes oceanográficos.</p>
          </div>
          <div class="lista-items">
            <div class="item-servicio"><span class="punto-azul">●</span><div>Diseño y configuración de anclajes a medida.</div></div>
            <div class="item-servicio"><span class="punto-azul">●</span><div>Integración y calibración de instrumentos.</div></div>
            <div class="item-servicio"><span class="punto-azul">●</span><div>Operaciones de despliegue y seguimiento continuo.</div></div>
          </div>
        </div>

        <div class="seccion-bloque" @click="$emit('cambiar-pagina', 'prototipado')">
          <div class="cabecera-bloque">
            <h2 class="titulo-fija">Prototipado Rápido y Fabricación</h2>
            <p>Diseño CAD avanzado y producción de componentes mecánicos complejos empleando impresión 3D técnica en materiales de alta resistencia.</p>
          </div>
          <div class="lista-items">
            <div class="item-servicio"><span class="punto-verde">●</span><div>Modelado 3D y diseño paramétrico.</div></div>
            <div class="item-servicio"><span class="punto-verde">●</span><div>Impresión técnica FDM y resina.</div></div>
            <div class="item-servicio"><span class="punto-verde">●</span><div>Desarrollo de carcasas submarinas y adaptadores.</div></div>
          </div>
        </div>

      </div> 
    </div>
  </div>
</template>

<style scoped>
.servicios-hub { position: relative; min-height: 100vh; padding-bottom: 80px; background-color: #f4f7f9; }
.fondo-servicios { position: absolute; top: 0; left: 0; width: 100%; height: 550px; background-image: linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), url('/instrumentacion.jpg'); background-size: cover; background-position: center; z-index: 0; }
.contenido-hub { position: relative; z-index: 10; padding-top: 120px; }
.titulo-seccion { color: white; font-size: 2.2rem; margin-bottom: 15px; font-weight: bold; position: relative; display: inline-block; padding-bottom: 8px; }
.titulo-seccion::after { content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background-color: #8cc63f; }
.subtitulo { color: #e0e6ed; font-size: 1.1rem; margin-bottom: 40px; max-width: 800px; }

/* CUADRICULA 2x2 */
.grid-servicios { display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; }

.seccion-bloque { background: white; border-radius: 12px; padding: 35px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); display: flex; flex-direction: column; cursor: pointer; transition: transform 0.3s; }
.seccion-bloque:hover { transform: translateY(-5px); }
.titulo-fija { color: #012169; margin-top: 0; font-size: 1.6rem; margin-bottom: 10px; }
.cabecera-bloque p { color: #666; font-size: 0.95rem; line-height: 1.3; margin-bottom: 15px; }
.lista-items { margin-top: 15px; display: flex; flex-direction: column; gap: 8px; }
.item-servicio { display: flex; gap: 10px; font-size: 0.9rem; color: #333; }
.punto-azul { color: #007bff; }
.punto-verde { color: #28a745; }

@media (max-width: 900px) { .grid-servicios { grid-template-columns: 1fr; } }
</style>