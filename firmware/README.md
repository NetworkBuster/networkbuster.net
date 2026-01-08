# Firmware Prototype: Power Manager

## Goal
Simulate and prototype power harvesting behavior (solar + thermal) and power-aware scheduler. Provide hooks for telemetry and control.

## Components
- `power_manager_sim.py` : Python simulation of harvester, battery, and scheduler
- `power_manager.c` : (skeleton) MCU logic for reading sensors and publishing MQTT telemetry

## Run (simulation)
`python firmware/power_manager_sim.py`

## Deliverables
- Simulation that models: solar irradiance, thermal gradient, MPPT output, battery state, and policy that decides when to wake high-power modules.
- Telemetry outputs consistent with `POWER-HARVESTING.md` API.

---

Notes: The simulation is intentionally simple and configurable for quick testing of scheduling policies.
