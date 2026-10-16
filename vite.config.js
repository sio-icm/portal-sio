import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/', // La web se sirve desde la raíz del servidor (10.100.201.12)
  plugins: [vue()],
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
