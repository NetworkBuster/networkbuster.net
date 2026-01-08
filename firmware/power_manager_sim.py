#!/usr/bin/env python3
"""Simple simulation of solar + thermal harvesting, battery, and scheduler."""
import time
import random

class Harvester:
    def __init__(self):
        self.irradiance = 0.5  # 0..1
        self.thermal = 0.2     # 0..1

    def sample(self):
        # fluctuate
        self.irradiance = max(0, min(1, self.irradiance + random.uniform(-0.05, 0.05)))
        self.thermal = max(0, min(1, self.thermal + random.uniform(-0.03, 0.03)))
        solar_mw = self.irradiance * 500  # up to 500 mW
        thermal_mw = self.thermal * 150  # up to 150 mW
        return solar_mw + thermal_mw

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

class PowerManager:
    def __init__(self):
        self.harvester = Harvester()
        self.batt = Battery()
        self.mode = 'normal'

    def step(self, dt_s=10):
        harvested = self.harvester.sample()
        # baseline device consumption
        baseline_mw = 80 if self.mode=='normal' else 20
        # if enough harvest, use it and charge battery
        net = harvested - baseline_mw
        if net >= 0:
            self.batt.charge(net, dt_s)
        else:
            self.batt.discharge(-net, dt_s)
        # simple policy: if battery <20% -> low_power
        if self.batt.percent() < 20:
            self.mode = 'low_power'
        elif self.batt.percent() > 40:
            self.mode = 'normal'

        return {
            'harvest_mw': int(harvested),
            'batteryPercent': self.batt.percent(),
            'mode': self.mode
        }

if __name__ == '__main__':
    pm = PowerManager()
    for i in range(200):
        s = pm.step(10)
        print(f"t={i*10:4}s harvest={s['harvest_mw']:4}mW batt={s['batteryPercent']:3}% mode={s['mode']}")
        time.sleep(0.05)
