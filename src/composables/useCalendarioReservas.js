import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

// Calendario de reservas compartido (Pelagia, Tanques de Pruebas):
// varios meses a partir del actual, selección de días y fechas escritas
// en el idioma de la web.
export function useCalendarioReservas(numeroMeses = 7) {
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

  // Días ocupados: todavía no hay un calendario real de reservas.
  // Cuando lo haya, se consultará aquí; mientras tanto no se marca ninguno.
  const esOcupado = () => false

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
