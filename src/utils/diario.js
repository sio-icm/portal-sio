// Tipos de nota del diario de actividad. Los valores son los mismos que acepta
// el backend (TIPOS_NOTA en backend/app.py); si se añade uno, hay que hacerlo
// en los dos sitios.
export const TIPOS_NOTA = [
  { valor: 'campanya', etiqueta: 'Campanya de mar', color: '#0086c0' },
  { valor: 'desenvolupament', etiqueta: 'Desenvolupament', color: '#6f42c1' },
  { valor: 'manteniment', etiqueta: 'Manteniment', color: '#fd7e14' },
  { valor: 'calibratge', etiqueta: 'Calibratge', color: '#20a39e' },
  { valor: 'divulgacio', etiqueta: 'Divulgació', color: '#d63384' },
  { valor: 'formacio', etiqueta: 'Formació', color: '#198754' },
  { valor: 'gestio', etiqueta: 'Gestió', color: '#6c757d' },
  { valor: 'altres', etiqueta: 'Altres', color: '#495057' }
]

export const tipoNota = (valor) => TIPOS_NOTA.find(t => t.valor === valor) || TIPOS_NOTA[TIPOS_NOTA.length - 1]

// "2026-10-20" -> "20/10/2026"
export const fechaCorta = (iso) => {
  if (!iso) return ''
  const [a, m, d] = iso.split('-')
  return `${d}/${m}/${a}`
}

export const hoyIso = () => {
  const d = new Date()
  const dos = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`
}

// Petición a la API de la intranet; si la sesión ha caducado, avisa al panel
export const peticionIntranet = async (url, opciones = {}, alCaducar = () => {}) => {
  const respuesta = await fetch(url, opciones)
  if (respuesta.status === 401) alCaducar()
  return respuesta
}
