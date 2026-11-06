import { createI18n } from 'vue-i18n'
import es from './es.js'
import ca from './ca.js'
import en from './en.js'
import intranet from './intranet.js'

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

// intranet.js tiene cada frase con sus tres idiomas juntos: aquí se separan.
// Los errores del servidor (claves con puntos) no pasan por vue-i18n: ver traducirError.
const separar = (nodo, idioma) => Object.fromEntries(Object.entries(nodo)
  .filter(([clave]) => clave !== 'errores' && clave !== 'valores')
  .map(([clave, valor]) => [clave, typeof valor.ca === 'string' ? valor[idioma] : separar(valor, idioma)]))
for (const [idioma, mensajes] of [['ca', ca], ['es', es], ['en', en]]) mensajes.intranet = separar(intranet, idioma)

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

// Mensaje de error del servidor (en castellano) en el idioma de la web; si no se conoce, tal cual
export const traducirError = (mensaje) => {
  if (!mensaje) return mensaje
  const idioma = i18n.global.locale.value
  const conocido = intranet.errores[mensaje]
  if (conocido) return conocido[idioma]
  const fotos = mensaje.match(/^Máximo (\d+) fotos por nota$/)
  if (fotos) return intranet.errores._fotosMax[idioma].replace('{n}', fotos[1])
  const notas = mensaje.match(/^Tiene (\d+) notas en el diario/)
  if (notas) return intranet.errores._tieneNotas[idioma].replace('{n}', notas[1])
  return mensaje
}

// Valor guardado de un proyecto o instrumento («En Curs», «Contrato»...) tal como se ve en cada idioma
export const traducirValor = (valor) => intranet.panel.valores[valor]?.[i18n.global.locale.value] || valor

export default i18n
