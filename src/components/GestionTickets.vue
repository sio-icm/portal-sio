<template>
  <div class="panel-tickets-iframe">
    <div class="cabecera-panel">
      <h2>🎫 Panel de Tickets OTRS (CMIMA)</h2>
      <a href="https://sau.cmima.csic.es/otrs/index.pl?Action=AgentDashboard" target="_blank" class="btn-externo">
        Abrir en pestaña nueva ↗
      </a>
    </div>

    <div class="contenedor-iframe">
      <iframe 
        src="https://sau.cmima.csic.es/otrs/index.pl?Action=AgentDashboard" 
        frameborder="0" 
        class="otrs-iframe"
        title="OTRS CSIC"
      ></iframe>
    </div>
  </div>
</template>

<style scoped>
.panel-tickets-iframe {
  background: #ffffff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  margin-top: 20px;
  border-top: 4px solid #0086c0;
  
  /* Forzamos a que el contenedor ocupe casi todo el alto disponible */
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px); 
  box-sizing: border-box;
}

.cabecera-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
  flex-shrink: 0; /* Evita que la cabecera se encoja */
}

.cabecera-panel h2 {
  color: #012169;
  margin: 0;
  font-size: 1.4rem;
}

.btn-externo {
  background: #0086c0;
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: bold;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.btn-externo:hover {
  background: #012169;
}

.contenedor-iframe {
  flex-grow: 1; /* Ocupa todo el espacio restante */
  width: 100%;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #ddd;
  background: #ffffff;
}

.otrs-iframe {
  width: 100%;
  height: 100%;
  display: block;
}
</style>