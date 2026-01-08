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
  - Optionally enable HTTP health: `--http-port 8080` and open `http://localhost:8080/health`
- Start `telemetry_ws_server.py` (tails telemetry.jsonl) or run `mqtt_bridge.py` depending on your preferred path
- Use the React panel to send a control; it will be forwarded to MQTT (when `mqtt_bridge.py --ws` is running), and the simulator will receive and apply it.

Bulk simulation:
- Use `bulk_simulator.py` to start many simulated devices in-process: `python firmware/bulk_simulator.py --count 20 --interval 5 --duration 300`

Automated CI test:
- A simple integration test is provided at `ci/integration_test.py`. Run it in CI to verify control flow:
  `python ci/integration_test.py` (uses public test.mosquitto.org broker by default)

Systemd unit:
- A template systemd unit is available at `packaging/device_simulator.service` for production deployments; adjust paths and user as needed.
