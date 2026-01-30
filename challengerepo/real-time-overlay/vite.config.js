import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
<<<<<<< HEAD
    base: '/overlay/',
    resolve: {
        alias: {
            'hls.js': 'hls.js/dist/hls.js'
        }
    },
    build: {
        outDir: 'dist',
        assetsDir: 'assets',
        sourcemap: false,
        minify: 'terser'
=======
    server: {
        port: 5173,
        host: true,
        cors: true
    },
    build: {
        outDir: 'dist',
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
>>>>>>> ea2e95d829f48271cc22401b9ead352fbc794d1d
    }
})
