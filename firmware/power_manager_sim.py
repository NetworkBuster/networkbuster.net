#!/usr/bin/env python3
"""Enhanced simulation of solar + thermal harvesting, battery, scheduler, and telemetry queueing.

Outputs JSON-lines to stdout and to `telemetry.jsonl` for downstream consumers.
"""
import time
import random
import json
import argparse
import threading
from datetime import datetime

class Harvester:
    def __init__(self):
        self.irradiance = 0.5  # 0..1
        self.thermal = 0.2     # 0..1

    def sample(self):
        # emulate fluctuations and occasional dips/spikes
        change = random.uniform(-0.07, 0.07)
        self.irradiance = max(0, min(1, self.irradiance + change))
        self.thermal = max(0, min(1, self.thermal + random.uniform(-0.04, 0.04)))
        solar_mw = self.irradiance * 500  # up to 500 mW
        thermal_mw = self.thermal * 150  # up to 150 mW
        # occasional transient drop
        if random.random() < 0.01:
            solar_mw *= random.uniform(0.1, 0.5)
        return int(solar_mw + thermal_mw)

class Battery:
    def __init__(self, capacity_mwh=2000):
        self.capacity = capacity_mwh
        self.energy = capacity_mwh * 0.5

    def charge(self, mW, dt_s):
        self.energy += mW * (dt_s/3600.0)
        if self.energy > self.capacity: self.energy = self.capacity

    def discharge(self, mW, dt_s):
        self.energy -= mW * (dt_s/3600.0)
        if self.energy < 0: self.energy = 0

    def percent(self):
        return int(self.energy / self.capacity * 100)

class MessageQueue:
    def __init__(self):
        self.queue = []

    def push(self, msg, urgent=False):
        self.queue.append({'ts': time.time(), 'urgent': urgent, 'msg': msg})

    def pop(self, count=1):
        # prioritize urgent messages
        urgent = [m for m in self.queue if m['urgent']]
        normal = [m for m in self.queue if not m['urgent']]
        out = urgent[:count]
        remaining = count - len(out)
        if remaining > 0:
            out += normal[:remaining]
        # remove popped
        for m in out:
            self.queue.remove(m)
        return out

    def size(self):
        return len(self.queue)

class PowerManager:
    def __init__(self, device_id='device-001'):
        self.device_id = device_id
        self.harvester = Harvester()
        self.batt = Battery()
        self.mode = 'normal'
        self.tx_queue = MessageQueue()
        self.uptime = 0
        self.last_signal = None
        self.stats = {'sent':0, 'queued':0}

    def generate_event(self):
        # random events that create telemetry or logs
        ev = None
        r = random.random()
        if r < 0.02:
            ev = {'type':'alert','level':'warning','text':'High temperature'}
        elif r < 0.05:
            ev = {'type':'info','text':'Scheduled maintenance window'}
        elif r < 0.1:
            ev = {'type':'signal','priority':'urgent','text':'Incoming control signal'}
        return ev

    def step(self, dt_s=10):
        self.uptime += dt_s
        harvested = self.harvester.sample()
        baseline_mw = 80 if self.mode=='normal' else 20
        net = harvested - baseline_mw
        if net >= 0:
            self.batt.charge(net, dt_s)
        else:
            self.batt.discharge(-net, dt_s)

        # policy
        if self.batt.percent() < 15:
            self.mode = 'critical'
        elif self.batt.percent() < 30:
            self.mode = 'low_power'
        elif self.batt.percent() > 45:
            self.mode = 'normal'

        # produce telemetry
        telemetry = {
            'id': self.device_id,
            'ts': int(time.time()),
            'harvest_mw': harvested,
            'batteryPercent': self.batt.percent(),
            'mode': self.mode,
            'queued': self.tx_queue.size(),
            'uptime_s': self.uptime
        }

        # generate events and enqueue messages
        ev = self.generate_event()
        if ev:
            urgent = (ev.get('priority')=='urgent')
            self.tx_queue.push({'event':ev, 'telemetry':telemetry}, urgent=urgent)
            self.stats['queued'] += 1
            if urgent:
                self.last_signal = telemetry['ts']

        # try to send up to N messages depending on energy and mode
        send_capacity = 3 if self.mode=='normal' else (1 if self.mode=='low_power' else 0)
        sent = []
        if send_capacity>0:
            items = self.tx_queue.pop(send_capacity)
            for item in items:
                # Simulate transmit energy cost
                tx_cost_mw = 200 if item['urgent'] else 100
                # if battery can't afford, requeue
                if self.batt.percent() <= 5 and tx_cost_mw>0:
                    self.tx_queue.push(item['msg'], urgent=item['urgent'])
                    break
                # discharge battery for transmit
                self.batt.discharge(tx_cost_mw, dt_s)
                sent.append(item['msg'])
                self.stats['sent'] += 1

        telemetry['sent_count'] = len(sent)
        telemetry['stats'] = self.stats.copy()
        return telemetry, sent

    def to_json(self, payload, sent):
        return json.dumps({'telemetry': payload, 'sent': sent})

# Simple writer that appends JSON lines to file
class TelemetryWriter:
    def __init__(self, path='telemetry.jsonl'):
        self.path = path
        self.lock = threading.Lock()

    def write(self, obj):
        line = json.dumps(obj)
        with self.lock:
            with open(self.path, 'a', encoding='utf-8') as f:
                f.write(line + '\n')


def run_sim(device_id='device-001', interval=5, duration=None, out_file='telemetry.jsonl'):
    pm = PowerManager(device_id=device_id)
    writer = TelemetryWriter(out_file)
    start = time.time()
    i = 0
    while True:
        telemetry, sent = pm.step(interval)
        payload = {'ts':int(time.time()), 'device': device_id, 'telemetry': telemetry}
        print(json.dumps(payload))
        writer.write(payload)
        i += 1
        if duration and (time.time() - start) > duration:
            break
        time.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='device-001')
    parser.add_argument('--interval', type=int, default=5)
    parser.add_argument('--duration', type=int, default=60)
    parser.add_argument('--out', default='telemetry.jsonl')
    args = parser.parse_args()
    run_sim(device_id=args.device, interval=args.interval, duration=args.duration, out_file=args.out)
