import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

// Envío de solicitudes de servicios (Pelagia, tanque, instrumentos...) a través
// del servidor, que las manda a sio@icm.csic.es. Ya no se abre el programa de
// correo del usuario. El nombre y el correo se recuerdan en este navegador.
const CLAVE_GUARDADO = 'sio-solicitante'

function leerGuardado() {
  try {
    const datos = JSON.parse(localStorage.getItem(CLAVE_GUARDADO) || '{}')
    return { nombre: String(datos.nombre || ''), email: String(datos.email || '') }
  } catch {
    return { nombre: '', email: '' }
  }
}

export function useSolicitud(tipo) {
  const { t } = useI18n()
  const guardado = leerGuardado()

  const nombre = ref(guardado.nombre)
  const email = ref(guardado.email)
  const web = ref('') // campo trampa para bots
  const estado = ref('') // '', 'enviando', 'enviado', 'error'
  const error = ref('')

  // Si el usuario vuelve a tocar el formulario, se borra el aviso anterior
  watch([nombre, email], () => { if (estado.value !== 'enviando') estado.value = '' })

  const enviar = async ({ asunto, cuerpo, adjunto = null }) => {
    if (estado.value === 'enviando') return false
    estado.value = 'enviando'
    error.value = ''

    const formulario = new FormData()
    formulario.append('tipo', tipo)
    formulario.append('nombre', nombre.value.trim())
    formulario.append('email', email.value.trim())
    formulario.append('web', web.value)
    formulario.append('asunto', asunto)
    formulario.append('cuerpo', cuerpo)
    if (adjunto) formulario.append('adjunto', adjunto)

    try {
      const respuesta = await fetch('/api/solicitud', { method: 'POST', body: formulario })
      if (respuesta.ok) {
        estado.value = 'enviado'
        try {
          localStorage.setItem(CLAVE_GUARDADO, JSON.stringify({ nombre: nombre.value.trim(), email: email.value.trim() }))
        } catch { /* navegador sin almacenamiento: no pasa nada */ }
        return true
      }
      if (respuesta.status === 400) error.value = t('solicitud.errorDatos')
      else if (respuesta.status === 413 || respuesta.status === 415) error.value = t('solicitud.errorAdjunto')
      else if (respuesta.status === 429) error.value = t('solicitud.errorLimite')
      else error.value = t('solicitud.errorEnvio')
    } catch (e) {
      console.error('Error enviando la solicitud:', e)
      error.value = t('solicitud.errorConexion')
    }
    estado.value = 'error'
    return false
  }

  return { nombre, email, web, estado, error, enviar }
}
