#!/usr/bin/env python3
"""Telemetry -> MQTT bridge

Modes:
  --file <path>  : tail a JSONL file (telemetry.jsonl) and publish lines
  --ws <url>     : connect to a WebSocket telemetry source and publish messages

Publishes to topics:
  device/{id}/power/telemetry

Requires: pip install paho-mqtt websockets
"""
import argparse
import json
import asyncio
import os
import time
from paho.mqtt import client as mqtt_client

# helper: read last line(s) appended
async def tail_file(path, on_msg):
    while not os.path.exists(path):
        print(f"Waiting for file: {path}")
        await asyncio.sleep(1)
    with open(path, 'r', encoding='utf-8') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue
            try:
                payload = json.loads(line)
            except Exception:
                payload = {'raw': line}
            await on_msg(payload)

async def ws_client(url, on_msg):
    import websockets
    async with websockets.connect(url) as ws:
        print('Connected to WS', url)
        async for msg in ws:
            try:
                payload = json.loads(msg)
            except Exception:
                payload = {'raw': msg}
            # If payload includes a control from client UI, publish to MQTT control topic
            if 'control' in payload:
                dev = payload.get('device') or (payload.get('control',{}).get('id')) or 'device-unknown'
                bridge = on_msg.__self__ if hasattr(on_msg, '__self__') else None
                if bridge and hasattr(bridge, 'client'):
                    # publish control
                    print('WS -> MQTT: publishing control for', dev)
                    bridge.publish({'control': payload['control'], 'device': dev})
            await on_msg(payload)

class MqttBridge:
    def __init__(self, broker='test.mosquitto.org', port=1883, client_id='nb-bridge', username=None, password=None, cafile=None):
        self.broker = broker
        self.port = port
        self.client = mqtt_client.Client(client_id)
        if username:
            self.client.username_pw_set(username, password)
        if cafile:
            self.client.tls_set(ca_certs=cafile)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(broker, port)
        self.client.loop_start()
        self._control_log = 'controls.jsonl'

    def _on_connect(self, client, userdata, flags, rc):
        print('MQTT connected, subscribing to control topics')
        # subscribe to control topics so we can capture inbound controls
        client.subscribe('device/+/power/control')

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
        except Exception:
            payload = {'raw': msg.payload.decode('utf-8')}
        entry = {'ts': int(time.time()), 'topic': msg.topic, 'payload': payload}
        with open(self._control_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        print('RCV control', msg.topic)

    def publish(self, payload):
        # payload is expected to have 'device' and 'telemetry' or control
        dev = payload.get('device') or (payload.get('telemetry',{}).get('id')) or (payload.get('control',{}).get('id')) or 'device-unknown'
        if 'control' in payload:
            topic = f'device/{dev}/power/control'
            data = json.dumps(payload['control'])
            self.client.publish(topic, data, qos=1)
            print('PUB control', topic, data)
            return
        topic = f'device/{dev}/power/telemetry'
        data = json.dumps(payload)
        self.client.publish(topic, data, qos=0)
        print('PUB telemetry', topic, len(data))

async def run_bridge(args):
    bridge = MqttBridge(broker=args.broker, port=args.port)
    async def on_msg(payload):
        bridge.publish(payload)
    if args.file:
        await tail_file(args.file, on_msg)
    elif args.ws:
        await ws_client(args.ws, on_msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='Path to telemetry.jsonl')
    parser.add_argument('--ws', help='WebSocket URL to consume')
    parser.add_argument('--broker', default='test.mosquitto.org')
    parser.add_argument('--port', type=int, default=1883)
    args = parser.parse_args()
    asyncio.run(run_bridge(args))
