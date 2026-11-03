// Calendari d'equip. Els valors són els mateixos que accepta el backend
// (TIPOS_CALENDARIO, FUERA_DEL_CENTRO i RECURSOS a backend/app.py): si se
// n'afegeix un, cal fer-ho als dos llocs.
export const TIPOS_CALENDARIO = [
  { valor: 'teletreball', etiqueta: 'Teletreball', icono: '🏠', color: '#6f42c1', fuera: true },
  { valor: 'campanya', etiqueta: 'Campanya / fora', icono: '🚢', color: '#0086c0', fuera: true },
  { valor: 'vacances', etiqueta: 'Vacances', icono: '🌴', color: '#20a39e', fuera: true },
  { valor: 'baixa', etiqueta: 'Baixa / permís', icono: '🩺', color: '#b02a37', fuera: true },
  { valor: 'formacio', etiqueta: 'Formació / congrés', icono: '🎓', color: '#198754', fuera: true },
  { valor: 'reunio', etiqueta: 'Reunió', icono: '💬', color: '#fd7e14', fuera: false },
  { valor: 'altres', etiqueta: 'Altres', icono: '📌', color: '#495057', fuera: false }
]
export const tipoCalendario = (valor) => TIPOS_CALENDARIO.find(t => t.valor === valor) || TIPOS_CALENDARIO[TIPOS_CALENDARIO.length - 1]

export const RECURSOS = [
  { valor: 'pelagia', etiqueta: 'Pelagia', icono: '⛵' },
  { valor: 'tanc', etiqueta: 'Tanc de proves', icono: '💧' },
  { valor: 'instrument', etiqueta: 'Instrument (préstec)', icono: '🔧' }
]
export const recurso = (valor) => RECURSOS.find(r => r.valor === valor) || RECURSOS[2]
export const nombreReserva = (r) => r.recurso === 'instrument' ? (r.instrumento || 'Instrument') : recurso(r.recurso).etiqueta

export const ICONOS_AVISO = { personal: '👥', conflicte: '⚠️', patro: '⛵' }

// Dates en format AAAA-MM-DD, sempre en hora local
export const aIso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
export const deIso = (iso) => { const [a, m, d] = iso.split('-').map(Number); return new Date(a, m - 1, d) }
export const sumarDias = (iso, n) => { const d = deIso(iso); d.setDate(d.getDate() + n); return aIso(d) }
export const lunesDe = (iso) => { const d = deIso(iso); return sumarDias(iso, -((d.getDay() + 6) % 7)) }
export const esFinDeSemana = (iso) => [0, 6].includes(deIso(iso).getDay())

export const fechaLarga = (iso, conAnio = true) => new Intl.DateTimeFormat('ca', {
  weekday: 'long', day: 'numeric', month: 'long', ...(conAnio ? { year: 'numeric' } : {})
}).format(deIso(iso))
export const fechaBreve = (iso) => new Intl.DateTimeFormat('ca', { weekday: 'short', day: 'numeric', month: 'short' }).format(deIso(iso))
export const rangoTexto = (inicio, fin) => inicio === fin ? fechaBreve(inicio) : `${fechaBreve(inicio)} – ${fechaBreve(fin)}`

const cubre = (x, dia) => x.inicio <= dia && dia <= x.fin

// Com es presenta un dia a partir de la resposta de /api/calendario
export const resumenDia = (datos, dia) => {
  const festiu = datos.festius.find(f => f.fecha === dia)
  const entradas = datos.entradas.filter(e => cubre(e, dia))
  const reservas = datos.reservas.filter(r => cubre(r, dia))
  const plantilla = datos.equipo.filter(u => u.plantilla)
  const fuera = new Set(entradas.filter(e => e.usuario_id !== null && tipoCalendario(e.tipo).fuera).map(e => e.usuario_id))
  const presentes = plantilla.filter(u => !fuera.has(u.id))
  return {
    dia,
    festiu: festiu ? festiu.nombre : null,
    laborable: !festiu && !esFinDeSemana(dia),
    entradas,
    reservas,
    presentes,
    plantilla,
    avisos: datos.avisos.filter(a => a.fecha <= dia && dia <= (a.fin || a.fecha))
  }
}

// Nom curt per a les cel·les: el primer nom, i la inicial del cognom si dues
// persones de l'equip es diuen igual («Raül B.», «Raül F.»)
export const nombreCorto = (nombre, equipo) => {
  if (!nombre) return ''
  const [primero, segundo] = nombre.split(' ')
  const repetido = equipo.filter(u => u.nombre.split(' ')[0] === primero).length > 1
  return repetido && segundo ? `${primero} ${segundo[0]}.` : primero
}
