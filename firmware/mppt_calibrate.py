#!/usr/bin/env python3
"""Simple MPPT calibration script (simulation mode by default).

Usage:
  python mppt_calibrate.py --simulate --out mppt_results.json

When hardware hooks are added (read_voltage, set_load), the script will operate real hardware.
"""
import argparse
import json
import time
import random

# --- Hardware hooks (override when hardware available) ---
def read_voltage():
    # placeholder; in real system read ADC
    return 12.0 + random.uniform(-0.5, 0.5)

def set_load(value):
    # placeholder; set electronic load or PWM duty
    pass

# --------------------------------------------------------

def run_sweep(steps=20, simulate=True):
    results = []
    for i in range(steps):
        load = (i+1)/steps
        set_load(load)
        time.sleep(0.1)
        v = read_voltage()
        i_m = max(0.01, (1.0 - load) * (5.0 + random.uniform(-0.2,0.2)))
        p = v * i_m
        results.append({'load': load, 'v': v, 'i': round(i_m,3), 'p': round(p,3)})
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulate', action='store_true')
    parser.add_argument('--out', default='mppt_results.json')
    args = parser.parse_args()
    res = run_sweep(steps=40, simulate=args.simulate)
    summary = sorted(res, key=lambda r: r['p'], reverse=True)[0]
    output = {'results': res, 'best': summary, 'ts': int(time.time())}
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print('Wrote', args.out)
