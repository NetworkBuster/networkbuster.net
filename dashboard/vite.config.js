import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
      // Static proxy (configurable via STATIC_PROXY_TARGET env var)
      '/static': {
        target: process.env.STATIC_PROXY_TARGET || 'http://localhost:3002',
        changeOrigin: true,
      }
    }
  }
})
