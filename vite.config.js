import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/', // La web se sirve desde la raíz del servidor (10.100.201.12)
  plugins: [vue()],
  define: {
    // vue-i18n: solo la Composition API, sin la API antigua
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false
  },
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
