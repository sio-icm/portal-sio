<script setup>
const emit = defineEmits(['cambiar-pagina'])
</script>

<template>
  <div class="idi-hub">
    <div class="fondo-idi"></div>

    <div class="contenedor-ancho contenido-hub">
      
      <h1 class="titulo-seccion">I+D+I</h1>
      <p class="subtitulo">Impulsando la innovación tecnológica marina y la transferencia de conocimiento del SIO.</p>

      <div class="contenido-oficina">
        <h2 class="titulo-oficina">Oficina I+D+I</h2>
        <p class="texto-oficina">Soporte integral a la investigación: desde la gestión de convocatorias hasta la protección de resultados y transferencia tecnológica.</p>

        <div class="lista-items">
          <div class="item-idi">
            <span class="punto-azul">●</span>
            <div>Gestión de proyectos y asesoramiento técnico especializado.</div>
          </div>
          <div class="item-idi">
            <span class="punto-azul">●</span>
            <div>Propiedad intelectual y valorización de la tecnología desarrollada.</div>
          </div>
          <div class="item-idi">
            <span class="punto-azul">●</span>
            <div>Fomento de la colaboración con empresas y centros del sector marino.</div>
          </div>
        </div>
        
        <!-- 👇 FORMULARIO TRANSPARENTE 👇 -->
        <div class="seccion-idi-innovacion" style="margin-top: 30px; padding: 15px; background-color: transparent; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px; text-align: left; max-width: 700px; backdrop-filter: blur(3px);">          <p style="font-size: 1.05rem; color: #e0e6ed; line-height: 1.6; margin-bottom: 30px;">
            En el SIO creemos en la co-creación. Si tienes una necesidad técnica para tus campañas, una idea para un nuevo sensor, o buscas adaptar robótica a un entorno extremo, <strong>queremos escucharte</strong>.
          </p>

          <form action="#" method="POST">
            
            <div style="margin-bottom: 10px;">
              <label for="nombre" style="display: block; font-weight: bold; color: white; margin-bottom: 5px;">Nombre y Apellidos</label>
              <input type="text" id="nombre" name="nombre" placeholder="Ej: Dra. Elena Martínez" style="width: 100%; padding: 10px; border: none; border-radius: 4px; box-sizing: border-box; background-color: rgba(255, 255, 255, 0.9);" required>
            </div>

            <div style="margin-bottom: 20px;">
              <label for="departamento" style="display: block; font-weight: bold; color: white; margin-bottom: 5px;">Institución / Departamento</label>
              <input type="text" id="departamento" name="departamento" placeholder="Ej: Dept. Oceanografía Física" style="width: 100%; padding: 10px; border: none; border-radius: 4px; box-sizing: border-box; background-color: rgba(255, 255, 255, 0.9);" required>
            </div>

            <div style="margin-bottom: 20px;">
              <label for="reto" style="display: block; font-weight: bold; color: white; margin-bottom: 5px;">¿Cuál es el reto oceanográfico o la idea?</label>
              <textarea id="reto" name="reto" rows="4" placeholder="Describe brevemente qué necesitas medir, qué problema técnico tienes o qué tecnología te gustaría explorar." style="width: 100%; padding: 10px; border: none; border-radius: 4px; box-sizing: border-box; resize: vertical; background-color: rgba(255, 255, 255, 0.9);" required></textarea>
            </div>

            <div style="margin-bottom: 25px;">
              <label for="entorno" style="display: block; font-weight: bold; color: white; margin-bottom: 5px;">Entorno de aplicación previsto</label>
              <select id="entorno" name="entorno" style="width: 100%; padding: 10px; border: none; border-radius: 4px; box-sizing: border-box; background-color: rgba(255, 255, 255, 0.9);">
                <option value="costa">Zona Costera / Aguas Someras</option>
                <option value="pelagico">Alta Mar / Plataforma Continental</option>
                <option value="profundo">Aguas Profundas / Bentos</option>
                <option value="laboratorio">Pruebas de Laboratorio / Tanque</option>
                <option value="otro">Otro</option>
              </select>
            </div>

            <div style="text-align: center;">
              <button type="submit" style="background-color: #8cc63f; color: #003366; border: none; padding: 12px 30px; font-size: 1.1rem; border-radius: 4px; cursor: pointer; font-weight: bold; transition: background 0.3s; width: 100%; max-width: 300px;">
                🚀 Enviar Propuesta
              </button>
            </div>
            
          </form>
        </div>
        <!-- ☝️ FIN DEL FORMULARIO ☝️ -->

      </div> 
    </div>
  </div>
</template>

<style scoped>
.idi-hub { 
  position: relative; 
  min-height: 100vh; 
  padding-bottom: 80px; 
  background-color: #f4f7f9; 
}

.fondo-idi { 
  position: absolute; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 100%; 
  background-image: linear-gradient(rgba(1, 33, 105, 0.65), rgba(1, 33, 105, 0.85)), 
                    url('/tortuga.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 0; 
}

.contenido-hub { 
  position: relative; 
  z-index: 10; 
  padding-top: 120px; 
}

.titulo-seccion { 
  color: white; 
  font-size: 2.2rem; 
  margin-bottom: 15px; 
  font-weight: bold; 
  position: relative;
  display: inline-block;
  padding-bottom: 8px;
}

.titulo-seccion::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: #8cc63f; 
}

.subtitulo { 
  color: #e0e6ed; 
  font-size: 1.1rem; 
  margin-bottom: 40px; 
  max-width: 800px; 
}

.contenido-oficina {
  margin-top: 30px;
  max-width: 850px;
  padding-bottom: 40px;
}

.titulo-oficina { 
  color: white; 
  margin-top: 0; 
  font-size: 1.6rem; 
  margin-bottom: 10px; 
}

.texto-oficina { 
  color: #e0e6ed; 
  font-size: 1.05rem; 
  line-height: 1.5; 
  margin-bottom: 20px; 
}

.lista-items { 
  margin-top: 15px; 
  display: flex; 
  flex-direction: column; 
  gap: 8px; 
}

.item-idi { 
  display: flex; 
  gap: 10px; 
  margin-bottom: 0px !important; 
  font-size: 1rem; 
  color: #e0e6ed;
  line-height: 1.3; 
}

.punto-azul { color: #00a4eb; }

@media (max-width: 992px) {
  .contenido-hub { padding-top: 150px; }
}
</style>