import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/', // La web se sirve desde la raíz del servidor (10.100.201.12)
  plugins: [vue()],
  server: {
    // En desarrollo, /api va al backend Flask (en producción lo hace Nginx)
    proxy: {
      '/api': 'http://127.0.0.1:5000'
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
