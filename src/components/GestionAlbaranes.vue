<script setup>
import { ref, computed } from 'vue'

// Los albaranes NO pueden ir escritos en el código: este archivo se descarga
// sin iniciar sesión, así que cualquiera vería nombres, proyectos e importes.
// Cuando se gestionen de verdad, deben venir del backend con login.
const albaranes = ref([])

const totalCobrado = computed(() => {
  return albaranes.value
    .filter(a => a.estado === 'Cobrado')
    .reduce((sum, a) => sum + a.importe, 0)
    .toFixed(2)
})

const totalEnProceso = computed(() => {
  return albaranes.value
    .filter(a => a.estado === 'En proceso')
    .reduce((sum, a) => sum + a.importe, 0)
    .toFixed(2)
})

const getClassEstado = (estado) => {
  if (estado === 'Cobrado') return 'badge-verde'
  if (estado === 'En proceso') return 'badge-naranja'
  return 'badge-gris'
}
</script>

<template>
  <div class="panel-albaranes">
    <div class="cabecera-panel">
      <h2>📦 Gestió d'Albarans i Facturació</h2>
      <button class="btn-nou-albaran" disabled title="Secció en preparació">+ Nou Albarà</button>
    </div>

    <div class="grid-kpis">
      <div class="kpi-card">
        <span class="kpi-numero">{{ albaranes.length }}</span>
        <span class="kpi-texto">Total Registres</span>
      </div>
      <div class="kpi-card" style="border-bottom: 4px solid #ffc107;">
        <span class="kpi-numero" style="color: #d39e00;">{{ totalEnProceso }} €</span>
        <span class="kpi-texto">Pendent / En Procés</span>
      </div>
      <div class="kpi-card" style="border-bottom: 4px solid #28a745;">
        <span class="kpi-numero" style="color: #28a745;">{{ totalCobrado }} €</span>
        <span class="kpi-texto">Total Cobrat</span>
      </div>
    </div>

    <div class="contenedor-tabla">
      <table class="tabla-sio">
        <thead>
          <tr>
            <th>Data</th>
            <th>Número</th>
            <th>Projecte / Servei</th>
            <th>Investigador/a Principal</th>
            <th>Import (€)</th>
            <th>Estat</th>
            <th>Document</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="albaranes.length === 0">
            <td colspan="7" class="aviso-vacio">Secció en preparació: els albarans es gestionaran des de la base de dades del SIO.</td>
          </tr>
          <tr v-for="albaran in albaranes" :key="albaran.id">
            <td class="td-fecha">{{ albaran.fecha }}</td>
            <td><strong>{{ albaran.numero }}</strong></td>
            <td class="td-proyecto">{{ albaran.proyecto }}</td>
            <td>{{ albaran.ip }}</td>
            <td class="td-importe">{{ albaran.importe.toFixed(2) }} €</td>
            <td>
              <span class="badge" :class="getClassEstado(albaran.estado)">
                {{ albaran.estado }}
              </span>
            </td>
            <td>
              <a href="#" class="btn-pdf">📄 PDF</a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.aviso-vacio { text-align: center; color: #666; font-style: italic; padding: 25px; }
.btn-nou-albaran:disabled { opacity: 0.5; cursor: not-allowed; }
.panel-albaranes {
  background: #ffffff;
  border-radius: 10px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  margin-top: 20px;
  border-top: 4px solid #8cc63f;
}

.cabecera-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  border-bottom: 2px solid #eee;
  padding-bottom: 15px;
}

.cabecera-panel h2 {
  color: #012169;
  margin: 0;
  font-size: 1.6rem;
}

.btn-nou-albaran {
  background: #012169;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-nou-albaran:hover {
  background: #0086c0;
}

/* KPIs */
.grid-kpis {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.kpi-card {
  background: #fdfdfd;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.kpi-numero {
  display: block;
  font-size: 2.2rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.kpi-texto {
  font-size: 0.9rem;
  color: #666;
  text-transform: uppercase;
  font-weight: bold;
}

/* TABLA */
.contenedor-tabla {
  overflow-x: auto;
}

.tabla-sio {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.tabla-sio th, .tabla-sio td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.tabla-sio th {
  background-color: #f8f9fa;
  color: #012169;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.85rem;
}

.tabla-sio tr:hover {
  background-color: #f8fcfd;
}

.td-fecha {
  color: #666;
}

.td-proyecto {
  color: #0086c0;
  font-weight: 500;
  max-width: 250px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.td-importe {
  font-family: monospace;
  font-size: 1.05rem;
  text-align: right;
  font-weight: bold;
}

/* BADGES DE ESTADO */
.badge {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}
.badge-verde { background-color: #eaf7ed; color: #257a3c; border: 1px solid #c3e6cb; }
.badge-naranja { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
.badge-gris { background-color: #f8f9fa; color: #6c757d; border: 1px solid #dee2e6; }

.btn-pdf {
  background: #f4f7f9;
  color: #0086c0;
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 0.85rem;
  border: 1px solid #b3d7ff;
  transition: all 0.2s;
}

.btn-pdf:hover {
  background: #0086c0;
  color: white;
}
</style>