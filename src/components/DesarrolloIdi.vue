<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Propuesta de colaboración: abre el correo del usuario con los datos preparados
const ENTORNOS = ['costa', 'pelagico', 'profundo', 'laboratorio', 'otro']
const propuesta = ref({ nombre: '', departamento: '', reto: '', entorno: 'costa' })

const enviarPropuesta = () => {
  const { nombre, departamento, reto, entorno } = propuesta.value
  const asunto = encodeURIComponent(t('idi.correo.asunto', { nombre }))
  const cuerpo = encodeURIComponent(
    `${t('idi.correo.saludo')}\n\n` +
    `${t('idi.correo.nombre')}: ${nombre}\n` +
    `${t('idi.correo.departamento')}: ${departamento}\n` +
    `${t('idi.correo.entorno')}: ${t(`idi.entornos.${entorno}`)}\n\n` +
    `${reto}\n\n` +
    `${t('idi.correo.despedida')}`
  )
  window.location.href = `mailto:sio@icm.csic.es?subject=${asunto}&body=${cuerpo}`
}
</script>

<template>
  <div class="idi-hub">
    <div class="fondo-idi"></div>

    <div class="contenedor-ancho contenido-hub">
      
      <h1 class="titulo-seccion">{{ $t('idi.titulo') }}</h1>
      <p class="subtitulo">{{ $t('idi.subtitulo') }}</p>

      <div class="contenido-oficina">
        <h2 class="titulo-oficina">{{ $t('idi.oficina') }}</h2>
        <p class="texto-oficina">{{ $t('idi.oficinaTexto') }}</p>

        <div class="lista-items">
          <div v-for="(item, i) in $tm('idi.items')" :key="i" class="item-idi">
            <span class="punto-azul" aria-hidden="true">●</span>
            <div>{{ $rt(item) }}</div>
          </div>
        </div>
        
        <!-- 👇 FORMULARIO TRANSPARENTE 👇 -->
        <div class="seccion-idi-innovacion" style="margin-top: 30px; padding: 15px; background-color: transparent; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px; text-align: left; max-width: 700px; backdrop-filter: blur(3px);">          <p style="font-size: 1.05rem; color: #e0e6ed; line-height: 1.6; margin-bottom: 30px;">
            {{ $t('idi.invitacion') }} <strong>{{ $t('idi.invitacionDestacado') }}</strong>.
          </p>

          <form @submit.prevent="enviarPropuesta">
            
            <div style="margin-bottom: 10px;">
              <label for="nombre" style="display: block; font-weight: bold; color: white; margin-bottom: 5px;">{{ $t('idi.nombre') }}</label>
              <input type="text" id="nombre" name="nombre" v-model="propuesta.nombre" :placeholder="$t('idi.nombrePh')" style="width: 100%; padding: 10px; border: none; border-radius: 4px; box-sizing: border-box; background-color: rgba(255, 255, 255, 0.9);" required>
            </div>

            <div style="margin-bottom: 20px;">
              <label for="departamento" style="display: block; font-weight: bold; color: white; margin-bottom: 5px;">{{ $t('idi.departamento') }}</label>
              <input type="text" id="departamento" name="departamento" v-model="propuesta.departamento" :placeholder="$t('idi.departamentoPh')" style="width: 100%; padding: 10px; border: none; border-radius: 4px; box-sizing: border-box; background-color: rgba(255, 255, 255, 0.9);" required>
            </div>

            <div style="margin-bottom: 20px;">
              <label for="reto" style="display: block; font-weight: bold; color: white; margin-bottom: 5px;">{{ $t('idi.reto') }}</label>
              <textarea id="reto" name="reto" v-model="propuesta.reto" rows="4" :placeholder="$t('idi.retoPh')" style="width: 100%; padding: 10px; border: none; border-radius: 4px; box-sizing: border-box; resize: vertical; background-color: rgba(255, 255, 255, 0.9);" required></textarea>
            </div>

            <div style="margin-bottom: 25px;">
              <label for="entorno" style="display: block; font-weight: bold; color: white; margin-bottom: 5px;">{{ $t('idi.entorno') }}</label>
              <select id="entorno" name="entorno" v-model="propuesta.entorno" style="width: 100%; padding: 10px; border: none; border-radius: 4px; box-sizing: border-box; background-color: rgba(255, 255, 255, 0.9);">
                <option v-for="entorno in ENTORNOS" :key="entorno" :value="entorno">{{ $t(`idi.entornos.${entorno}`) }}</option>
              </select>
            </div>

            <p style="font-size: 0.85rem; color: #e0e6ed; margin: 0 0 15px;">{{ $t('idi.avisoCorreo') }} <a href="mailto:sio@icm.csic.es" style="color: white;">sio@icm.csic.es</a>.</p>

            <div style="text-align: center;">
              <button type="submit" style="background-color: #8cc63f; color: #003366; border: none; padding: 12px 30px; font-size: 1.1rem; border-radius: 4px; cursor: pointer; font-weight: bold; transition: background 0.3s; width: 100%; max-width: 300px;">
                🚀 {{ $t('idi.enviar') }}
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