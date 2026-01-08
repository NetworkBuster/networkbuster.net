Telemetry tooling

Files added:
- `power_manager_sim.py` : enhanced simulation (writes JSONL)
- `telemetry_ws_server.py` : broadcast JSONL over WebSocket
- `mqtt_bridge.py` : publish telemetry to MQTT (file or ws mode)

Examples:
1) Start simulation:
   python firmware/power_manager_sim.py --device device-01 --interval 2 --duration 3600 --out telemetry.jsonl

2) Start WS server:
   python firmware/telemetry_ws_server.py --file telemetry.jsonl --port 8765

3) Start MQTT bridge (file):
   python firmware/mqtt_bridge.py --file telemetry.jsonl --broker test.mosquitto.org

   or with TLS/auth:
   python firmware/mqtt_bridge.py --file telemetry.jsonl --broker mqtt.example.com --port 8883 --mqtt-user user --mqtt-pass secret --cafile ca.pem

4) Start MQTT bridge (ws):
   python firmware/mqtt_bridge.py --ws ws://localhost:8765 --broker test.mosquitto.org

Control flow:
- The React Power Panel sends control messages via WebSocket ({control:{...}}).
- When running `mqtt_bridge.py --ws ws://...`, control messages are forwarded to MQTT topic `device/{id}/power/control`.
- `mqtt_bridge.py` also subscribes to `device/+/power/control` and logs incoming control messages to `controls.jsonl`.

Notes:
- `mqtt_bridge.py` uses the public test Mosquitto broker by default; for production use your own broker and configure credentials.
- `react-power-panel` is a Vite app located in `dashboard/react-power-panel` (run `npm install` then `npm run dev`).
