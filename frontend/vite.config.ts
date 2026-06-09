import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Todas as chamadas /api/* encaminham para a FastAPI do helmsman
      '/api': {
        target: 'http://localhost:8800',
        changeOrigin: true,
        // sem rewrite — /api/metrics no front bate em /api/metrics na FastAPI
      },
    },
  },
})
