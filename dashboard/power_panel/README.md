Power Panel mock (static HTML + WebSocket)

Usage:
1. Start the simulation (writes telemetry.jsonl):
   python firmware/power_manager_sim.py --device device-001 --interval 3 --duration 3600 --out telemetry.jsonl

2. Start WebSocket telemetry server (requires `pip install websockets`):
   python firmware/telemetry_ws_server.py --file telemetry.jsonl --port 8765

3. Open `dashboard/power_panel/index.html` in your browser (served via simple HTTP server or open the file if using `ws://localhost:8765`).

Notes:
- This is a mock; control buttons only simulate UI actions. In production integrate via secure MQTT or authenticated WebSocket control channels.
