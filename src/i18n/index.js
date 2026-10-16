import { createI18n } from 'vue-i18n'
import es from './es.js'
import ca from './ca.js'
import en from './en.js'

// Textos de la web en castellano, catalán e inglés (src/i18n/*.js).
// Ojo al escribir textos: { } @ $ | tienen significado especial en vue-i18n.
// Para escribir una @ (correos) hay que poner {'@'}.
export const IDIOMAS = ['ca', 'es', 'en']
const CLAVE_GUARDADA = 'sio_idioma'

const idiomaInicial = () => {
  try {
    const guardado = localStorage.getItem(CLAVE_GUARDADA)
    if (IDIOMAS.includes(guardado)) return guardado
  } catch { /* navegador sin almacenamiento */ }
  const navegador = (navigator.language || 'es').slice(0, 2).toLowerCase()
  return IDIOMAS.includes(navegador) ? navegador : 'es'
}

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: idiomaInicial(),
  fallbackLocale: 'es',
  messages: { es, ca, en }
})

document.documentElement.lang = i18n.global.locale.value

export const cambiarIdioma = (idioma) => {
  if (!IDIOMAS.includes(idioma)) return
  i18n.global.locale.value = idioma
  document.documentElement.lang = idioma
  try { localStorage.setItem(CLAVE_GUARDADA, idioma) } catch { /* sin almacenamiento */ }
}

export default i18n
