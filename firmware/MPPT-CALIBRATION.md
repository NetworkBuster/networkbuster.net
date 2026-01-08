# MPPT Calibration & Validation

## Purpose
Guidance and a small script to perform MPPT sweep calibration for a solar + TEG harvesting setup. This helps find operating voltage/current (Vmp/Imp) and verify MPPT behavior.

## Steps (bench)
1. Connect solar panel to MPPT module input and a programmable electronic load to the MPPT output.
2. Measure open-circuit voltage (Voc) and short-circuit current (Isc) of the panel at test conditions.
3. Using the `mppt_calibrate.py` script, sweep output load points and record power vs voltage.
4. Determine Vmp for best power point and program MPPT setpoint accordingly.

## Script: `mppt_calibrate.py`
- Simulates sweeps if hardware not connected (safe dry-run).
- When connected to real hardware, implement the `read_voltage()`, `set_load()` hooks for the specific MPPT/regulator.

## Acceptance criteria
- Vmp recorded to `mppt_results.json` including ambient conditions (temp, irradiance).
- MPPT efficiency > 90% at nominal irradiance.

## Safety
- Ensure correct panel orientation and no reverse connections
- Follow manufacturer's limits for MPPT current and device temperature
