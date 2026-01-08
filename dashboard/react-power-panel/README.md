React Power Panel (Vite)

Quickstart:
1. cd dashboard/react-power-panel
2. npm install
3. npm run dev

By default the app connects to `ws://localhost:8765`. Set `WS_URL` env var to change.

Notes:
- The component expects telemetry messages shaped like { telemetry: { batteryPercent, harvest_mw, mode, queued, uptime_s, stats } }
- Control buttons send JSON controls via the same WebSocket (for demo only); in production use authenticated MQTT or control channels.
