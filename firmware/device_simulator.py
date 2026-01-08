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
import logging
import signal
from logging.handlers import RotatingFileHandler
from paho.mqtt import client as mqtt_client
# Prometheus
from prometheus_client import start_http_server, Gauge

class DeviceSim:
    def __init__(self, device_id='device-01', broker='test.mosquitto.org', port=1883, username=None, password=None, cafile=None, log_file=None, log_level='INFO', prom_port=None):
        self.id = device_id
        self.broker = broker
        self.port = port

        # Logging
        self.logger = logging.getLogger(f'device-{self.id}')
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        if log_file:
            handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
        else:
            handler = logging.StreamHandler()
        handler.setFormatter(fmt)
        self.logger.addHandler(handler)

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

        # state
        self.mode = 'normal'
        self.battery = 60
        self.harvest = 200
        self.queued = 0
        self.stats = {'sent':0}
        self._stop = False

        # Prometheus metrics
        self.prom_port = prom_port
        self.g_battery = Gauge('device_battery_percent', 'Battery percent', ['device'])
        self.g_harvest = Gauge('device_harvest_mw', 'Harvest mW', ['device'])
        self.g_sent = Gauge('device_sent_total', 'Telemetry messages sent', ['device'])
        if self.prom_port:
            start_http_server(self.prom_port)
            self.logger.info('Prometheus metrics available on port %s', self.prom_port)

        # setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def on_connect(self, client, userdata, flags, rc):
        topic = f'device/{self.id}/power/control'
        self.logger.info('Connected to MQTT broker, subscribing to %s', topic)
        client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
        except Exception:
            payload = {'raw': msg.payload.decode('utf-8')}
        entry = {'ts': int(time.time()), 'topic': msg.topic, 'payload': payload}
        with open('controls.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        self.logger.info('Received control: %s', payload)
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
        self.logger.debug('Published telemetry -> %s', telemetry)
        # update prometheus metrics
        try:
            self.g_battery.labels(device=self.id).set(self.battery)
            self.g_harvest.labels(device=self.id).set(self.harvest)
            self.g_sent.labels(device=self.id).set(self.stats['sent'])
        except Exception:
            pass

    def run(self, interval=5, duration=None, http_port=None):
        # Optionally start a simple HTTP health endpoint
        server = None
        if http_port:
            server = self._start_health_server(http_port)

        start = time.time()
        try:
            while not self._stop:
                self.publish_telemetry()
                if duration and (time.time() - start) > duration:
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info('Interrupted, stopping')
        finally:
            if server:
                server.shutdown()
            self.client.loop_stop()
            self.client.disconnect()
            self.logger.info('Simulator stopped')

    def _signal_handler(self, signum, frame):
        self.logger.info('Received signal %s, scheduling stop', signum)
        self._stop = True

    def _start_health_server(self, port):
        # Lightweight HTTP health endpoint that returns current state as JSON
        import threading
        from http.server import HTTPServer, BaseHTTPRequestHandler

        sim = self

        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path != '/health':
                    self.send_response(404)
                    self.end_headers()
                    return
                payload = {
                    'id': sim.id,
                    'mode': sim.mode,
                    'batteryPercent': sim.battery,
                    'harvest_mw': sim.harvest,
                    'stats': sim.stats
                }
                body = json.dumps(payload).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                return

        httpd = HTTPServer(('0.0.0.0', port), HealthHandler)
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        print(f'Health endpoint listening on http://0.0.0.0:{port}/health')
        return httpd

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