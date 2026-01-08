Device Simulator

`firmware/device_simulator.py` simulates a device that:
- Publishes telemetry to `device/{id}/power/telemetry` on an MQTT broker
- Subscribes to `device/{id}/power/control` and applies control actions (set_mode, set_tx_power_db, etc.)
- Logs inbound controls to `controls.jsonl`

Quickstart:
1. Start an MQTT broker (or use `test.mosquitto.org` for quick tests)
2. Run the simulator:
   python firmware/device_simulator.py --id device-01 --interval 2 --duration 60
3. Send a control message (example):
   python -c "import paho.mqtt.client as mqtt, json; c=mqtt.Client(); c.connect('test.mosquitto.org',1883); c.publish('device/device-01/power/control', json.dumps({'set_mode':'low_power'})); c.disconnect()"

End-to-end tests:
- Start `device_simulator.py` (publishes telemetry)
- Start `telemetry_ws_server.py` (tails telemetry.jsonl) or run `mqtt_bridge.py` depending on your preferred path
- Use the React panel to send a control; it will be forwarded to MQTT (when `mqtt_bridge.py --ws` is running), and the simulator will receive and apply it.
