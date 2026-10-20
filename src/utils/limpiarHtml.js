import DOMPurify from 'dompurify'

// Los textos con formato que se escriben en la intranet (descripciones de
// instrumentos y proyectos) se guardan como HTML y se muestran con v-html.
// Antes de mostrarlos se limpian: se mantiene el formato (negritas, listas,
// enlaces, imágenes...) y se quita todo lo que podría ejecutar código en el
// navegador de quien visita la web (scripts, onclick, javascript:, iframes...).

// Los enlaces se abren en otra pestaña y sin dar acceso a esta página
DOMPurify.addHook('afterSanitizeAttributes', (nodo) => {
  if (nodo.tagName === 'A' && nodo.getAttribute('href')) {
    nodo.setAttribute('target', '_blank')
    nodo.setAttribute('rel', 'noopener noreferrer')
  }
})

export const limpiarHtml = (html) => DOMPurify.sanitize(html || '', { ADD_ATTR: ['target'] })
