#!/usr/bin/env python3
"""Simple integration test for control flow.

- Starts a device simulator process (short duration)
- Publishes control message to the device control topic
- Waits and asserts that `controls.jsonl` contains the control

This is intended as a quick CI smoke test (non-exhaustive).
"""
import subprocess
import time
import json
import os
import sys
from paho.mqtt import client as mqtt_client

SIM = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'firmware', 'device_simulator.py'))
CONTROLS_LOG = os.path.abspath('controls.jsonl')

def run_simulator(device_id='itest-01', duration=15):
    proc = subprocess.Popen([sys.executable, SIM, '--id', device_id, '--interval', '1', '--duration', str(duration)])
    return proc

def publish_control(device_id, payload):
    c = mqtt_client.Client()
    c.connect('test.mosquitto.org', 1883)
    c.loop_start()
    topic = f'device/{device_id}/power/control'
    c.publish(topic, json.dumps(payload))
    time.sleep(1)
    c.loop_stop()
    c.disconnect()

def wait_for_control_entry(device_id, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(CONTROLS_LOG):
            with open(CONTROLS_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        e = json.loads(line)
                        if e.get('topic', '').startswith(f'device/{device_id}/power/control'):
                            return e
                    except Exception:
                        continue
        time.sleep(0.5)
    return None

if __name__ == '__main__':
    device = 'itest-01'
    # remove old control file
    try:
        if os.path.exists(CONTROLS_LOG): os.remove(CONTROLS_LOG)
    except Exception:
        pass

    p = run_simulator(device_id=device, duration=20)
    time.sleep(2)  # let simulator connect
    print('Publishing control...')
    publish_control(device, {'set_mode':'low_power'})

    entry = wait_for_control_entry(device, timeout=12)
    p.wait()
    if not entry:
        print('FAIL: control entry not found in controls.jsonl')
        sys.exit(2)
    print('PASS: control entry found:', entry)
    sys.exit(0)
