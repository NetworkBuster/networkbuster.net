#!/usr/bin/env python3
"""Bulk device simulator: spawn many simulated devices in-process for load testing.

Usage:
  python firmware/bulk_simulator.py --count 10 --interval 5 --duration 60

This creates `count` simulated devices each publishing telemetry to the broker.
"""
import argparse
import threading
from device_simulator import DeviceSim

def run_device(i, broker, port, interval, duration):
    dev_id = f'device-{i:03d}'
    sim = DeviceSim(device_id=dev_id, broker=broker, port=port)
    sim.run(interval=interval, duration=duration)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--broker', default='test.mosquitto.org')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument('--interval', type=int, default=5)
    parser.add_argument('--duration', type=int, default=60)
    args = parser.parse_args()

    threads = []
    for i in range(1, args.count+1):
        t = threading.Thread(target=run_device, args=(i, args.broker, args.port, args.interval, args.duration), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print('Bulk simulation finished')