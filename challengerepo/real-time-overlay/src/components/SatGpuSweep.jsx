import { useEffect, useMemo, useState } from 'react'

const ISS_API_URL = 'https://api.wheretheiss.at/v1/satellites/25544'

function formatNumber(value, digits = 2) {
    if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A'
    return value.toFixed(digits)
}

export default function SatGpuSweep() {
    const [satellite, setSatellite] = useState({
        loading: true,
        error: false,
        latitude: null,
        longitude: null,
        altitude: null,
        velocity: null,
        visibility: null,
        updatedAt: null
    })
    const [gpu, setGpu] = useState({
        renderer: 'Unknown',
        vendor: 'Unknown',
        glVersion: 'Unavailable',
        maxTextureSize: null,
        maxRenderbufferSize: null
    })
    const [fps, setFps] = useState(0)

    useEffect(() => {
        let cancelled = false

        const fetchSatellite = async () => {
            try {
                const res = await fetch(ISS_API_URL)
                if (!res.ok) throw new Error(`HTTP ${res.status}`)
                const data = await res.json()
                if (cancelled) return
                setSatellite({
                    loading: false,
                    error: false,
                    latitude: data.latitude,
                    longitude: data.longitude,
                    altitude: data.altitude,
                    velocity: data.velocity,
                    visibility: data.visibility,
                    updatedAt: data.timestamp ? new Date(data.timestamp * 1000) : new Date()
                })
            } catch {
                if (cancelled) return
                setSatellite(prev => ({ ...prev, loading: false, error: true }))
            }
        }

        fetchSatellite()
        const interval = setInterval(fetchSatellite, 15000)

        return () => {
            cancelled = true
            clearInterval(interval)
        }
    }, [])

    useEffect(() => {
        const canvas = document.createElement('canvas')
        const gl = canvas.getContext('webgl2') || canvas.getContext('webgl')
        if (!gl) return

        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
        const renderer = debugInfo
            ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
            : gl.getParameter(gl.RENDERER)
        const vendor = debugInfo
            ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL)
            : gl.getParameter(gl.VENDOR)

        setGpu({
            renderer: renderer || 'Unknown',
            vendor: vendor || 'Unknown',
            glVersion: gl.getParameter(gl.VERSION) || 'Unknown',
            maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
            maxRenderbufferSize: gl.getParameter(gl.MAX_RENDERBUFFER_SIZE)
        })
    }, [])

    useEffect(() => {
        let mounted = true
        let frameCount = 0
        let start = performance.now()

        const tick = now => {
            frameCount += 1
            const elapsed = now - start
            if (elapsed >= 1000) {
                if (mounted) {
                    setFps(Math.round((frameCount * 1000) / elapsed))
                }
                frameCount = 0
                start = now
            }
            if (mounted) requestAnimationFrame(tick)
        }

        requestAnimationFrame(tick)
        return () => {
            mounted = false
        }
    }, [])

    const satStatus = useMemo(() => {
        if (satellite.loading) return 'SYNCING'
        if (satellite.error) return 'DEGRADED'
        return 'ONLINE'
    }, [satellite.error, satellite.loading])

    return (
        <div className="mt-2 p-2 bg-white/5 rounded text-[10px] border border-white/10">
            <div className="flex items-center justify-between mb-2">
                <span className="text-[#00f0ff] font-bold tracking-wider">SAT+GPU SWEEP</span>
                <span className={satellite.error ? 'text-[#ff003c]' : 'text-[#00ff00]'}>{satStatus}</span>
            </div>

            <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-gray-300">
                <span>SAT LAT</span>
                <span className="text-white text-right">{formatNumber(satellite.latitude, 3)}</span>

                <span>SAT LNG</span>
                <span className="text-white text-right">{formatNumber(satellite.longitude, 3)}</span>

                <span>ALT (KM)</span>
                <span className="text-white text-right">{formatNumber(satellite.altitude, 1)}</span>

                <span>VEL (KM/H)</span>
                <span className="text-white text-right">{formatNumber(satellite.velocity, 0)}</span>

                <span>VISIBILITY</span>
                <span className="text-white text-right uppercase">{satellite.visibility || 'N/A'}</span>

                <span>FPS</span>
                <span className="text-white text-right">{fps || 0}</span>

                <span>GPU</span>
                <span className="text-white text-right truncate" title={gpu.renderer}>{gpu.renderer}</span>

                <span>VENDOR</span>
                <span className="text-white text-right truncate" title={gpu.vendor}>{gpu.vendor}</span>

                <span>WEBGL</span>
                <span className="text-white text-right">{gpu.glVersion}</span>

                <span>MAX TEX</span>
                <span className="text-white text-right">{gpu.maxTextureSize ?? 'N/A'}</span>

                <span>MAX RBUF</span>
                <span className="text-white text-right">{gpu.maxRenderbufferSize ?? 'N/A'}</span>
            </div>

            <div className="text-gray-500 mt-2 text-right">
                UPDATED: {satellite.updatedAt ? satellite.updatedAt.toLocaleTimeString() : 'N/A'}
            </div>
        </div>
    )
}
