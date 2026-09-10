import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    base: '/overlay/',
    resolve: {
        alias: {
            'hls.js': 'hls.js/dist/hls.js'
        }
    },
    server: {
        port: 5173,
        host: true,
        cors: true
    },
    build: {
        outDir: 'dist',
        assetsDir: 'assets',
        sourcemap: true,
        rollupOptions: {
            output: {
                manualChunks: {
                    'three': ['three', '@react-three/fiber', '@react-three/drei'],
                    'leaflet': ['leaflet', 'react-leaflet']
                }
            }
        }
    },
    define: {
        'process.env': process.env
    }
})
