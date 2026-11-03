import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

// Calendario de reservas compartido (Pelagia, Tanques de Pruebas):
// varios meses a partir del actual, selección de días y fechas escritas
// en el idioma de la web. Los días ocupados salen de las reservas del
// calendario de equipo de la intranet ('pelagia' o 'tanc').
export function useCalendarioReservas(recurso, numeroMeses = 7) {
  const { locale } = useI18n()

  const hoy = new Date()
  const meses = Array.from({ length: numeroMeses }, (_, i) => new Date(hoy.getFullYear(), hoy.getMonth() + i, 1))

  const mesActualIndex = ref(0)
  const mesVisible = computed(() => meses[mesActualIndex.value])
  const diasMesVisible = computed(() => new Date(mesVisible.value.getFullYear(), mesVisible.value.getMonth() + 1, 0).getDate())
  const hayMesAnterior = computed(() => mesActualIndex.value > 0)
  const hayMesSiguiente = computed(() => mesActualIndex.value < meses.length - 1)

  const nombreMes = computed(() => {
    const texto = new Intl.DateTimeFormat(locale.value, { month: 'long', year: 'numeric' }).format(mesVisible.value)
    return texto.charAt(0).toUpperCase() + texto.slice(1)
  })

  const mesAnterior = () => { if (hayMesAnterior.value) mesActualIndex.value-- }
  const mesSiguiente = () => { if (hayMesSiguiente.value) mesActualIndex.value++ }

  // Días elegidos como 'AAAA-M-D', para poder ordenarlos y escribirlos en cualquier idioma
  const diasSeleccionados = ref([])
  const claveDia = (dia) => `${mesVisible.value.getFullYear()}-${mesVisible.value.getMonth()}-${dia}`

  // Días ocupados ('AAAA-MM-DD'), sin nombres ni motivos
  const ocupados = ref(new Set())
  const iso = (fecha) => `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`
  onMounted(async () => {
    const desde = iso(meses[0])
    const hasta = iso(new Date(hoy.getFullYear(), hoy.getMonth() + numeroMeses, 0))
    try {
      const r = await fetch(`/api/ocupacion?recurso=${recurso}&desde=${desde}&hasta=${hasta}`)
      if (r.ok) ocupados.value = new Set(await r.json())
    } catch { /* sin conexión con el servidor: se muestran todos libres */ }
  })
  const esOcupado = (dia) => ocupados.value.has(iso(new Date(mesVisible.value.getFullYear(), mesVisible.value.getMonth(), dia)))

  const toggleDia = (dia) => {
    if (esOcupado(dia)) return
    const clave = claveDia(dia)
    const index = diasSeleccionados.value.indexOf(clave)
    if (index === -1) diasSeleccionados.value.push(clave)
    else diasSeleccionados.value.splice(index, 1)
  }

  const estaSeleccionado = (dia) => diasSeleccionados.value.includes(claveDia(dia))

  // Fechas elegidas, ordenadas y escritas en el idioma activo ("3 de noviembre de 2026")
  const fechasSeleccionadas = computed(() => {
    const formato = new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' })
    return diasSeleccionados.value
      .map((clave) => { const [a, m, d] = clave.split('-').map(Number); return new Date(a, m, d) })
      .sort((x, y) => x - y)
      .map((fecha) => formato.format(fecha))
  })

  return {
    nombreMes, diasMesVisible, hayMesAnterior, hayMesSiguiente, mesAnterior, mesSiguiente,
    diasSeleccionados, esOcupado, toggleDia, estaSeleccionado, fechasSeleccionadas
  }
}
