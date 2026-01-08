#!/usr/bin/env python3
"""Simulated device agent for testing control/telemetry loop via MQTT.

Behavior:
- Publishes telemetry periodically to `device/{id}/power/telemetry`.
- Subscribes to `device/{id}/power/control` and applies actions (e.g., set_mode).
- Logs inbound controls to `controls.jsonl`.

Usage:
  python firmware/device_simulator.py --id device-01 --broker test.mosquitto.org --interval 2 --duration 60

Requires: pip install paho-mqtt
"""
import argparse
import json
import time
import random
from paho.mqtt import client as mqtt_client

class DeviceSim:
    def __init__(self, device_id='device-01', broker='test.mosquitto.org', port=1883, username=None, password=None, cafile=None):
        self.id = device_id
        self.broker = broker
        self.port = port
        # Use explicit protocol to avoid callback API mismatch in some paho versions
        self.client = mqtt_client.Client(client_id=f"sim-{device_id}", protocol=mqtt_client.MQTTv311)
        if username:
            self.client.username_pw_set(username, password)
        if cafile:
            self.client.tls_set(ca_certs=cafile)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        self.client.loop_start()

        self.mode = 'normal'
        self.battery = 60
        self.harvest = 200
        self.queued = 0
        self.stats = {'sent':0}

    def on_connect(self, client, userdata, flags, rc):
        topic = f'device/{self.id}/power/control'
        print('Connected to MQTT broker, subscribing to', topic)
        client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
        except Exception:
            payload = {'raw': msg.payload.decode('utf-8')}
        entry = {'ts': int(time.time()), 'topic': msg.topic, 'payload': payload}
        with open('controls.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        print('Received control:', payload)
        # apply control
        if isinstance(payload, dict):
            if 'set_mode' in payload:
                self.mode = payload['set_mode']
            if 'set_tx_power_db' in payload:
                # not modeled; log
                print('Set tx power to', payload['set_tx_power_db'])
            if 'battery' in payload:
                try:
                    self.battery = int(payload['battery'])
                except Exception:
                    pass

    def publish_telemetry(self):
        # simple model: harvest fluctuates, battery changes slowly
        self.harvest = max(0, int(self.harvest + random.uniform(-30, 30)))
        if self.mode == 'normal':
            cons = 80
        elif self.mode == 'low_power':
            cons = 20
        else:
            cons = 40
        net = self.harvest - cons
        if net >= 0:
            self.battery = min(100, self.battery + int(net/100.0))
        else:
            self.battery = max(0, self.battery + int(net/100.0))

        telemetry = {
            'id': self.id,
            'ts': int(time.time()),
            'harvest_mw': self.harvest,
            'batteryPercent': self.battery,
            'mode': self.mode,
            'queued': self.queued,
            'uptime_s': 0,
            'stats': self.stats
        }
        topic = f'device/{self.id}/power/telemetry'
        self.client.publish(topic, json.dumps({'telemetry':telemetry}))
        self.stats['sent'] += 1
        print('Published telemetry ->', telemetry)

    def run(self, interval=5, duration=None):
        start = time.time()
        while True:
            self.publish_telemetry()
            if duration and (time.time() - start) > duration:
                break
            time.sleep(interval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', default='device-01')
    parser.add_argument('--broker', default='test.mosquitto.org')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument('--interval', type=int, default=5)
    parser.add_argument('--duration', type=int, default=30)
    parser.add_argument('--mqtt-user')
    parser.add_argument('--mqtt-pass')
    parser.add_argument('--cafile')
    args = parser.parse_args()

    sim = DeviceSim(device_id=args.id, broker=args.broker, port=args.port, username=args.mqtt_user, password=args.mqtt_pass, cafile=args.cafile)
    sim.run(interval=args.interval, duration=args.duration)
    print('Simulator finished')