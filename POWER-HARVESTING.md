# POWER HARVESTING DESIGN

## Purpose
Design an energy-harvesting subsystem (solar + thermal) to keep devices "signal-based always-on" via intelligent power management, with telemetry exposed to the dashboard.

---

## Block diagram (logical)

Device peripherals: Sensors, Radio (low-power listen + WiFi7), MCU

[Solar Panel] -- MPPT --+--> Charger -- Battery / Supercap -- Power Path -- Device
[TEG] -- Booster -------+

MCU monitors: voltage, current, temperature, irradiance, state-of-charge (fuel gauge)
MCU provides telemetry and remote control via MQTT / HTTPS

---

## BOM (example)
- Solar panel (tie to device size): 2W - 20W modules (mono) per device
- TEG module (e.g., 1-5W) + heat sink
- MPPT controller (off-the-shelf small MPPT module)
- TEG power booster / DC-DC converter
- Battery: LiFePO4 2-4 Ah (or Li-ion with proper BMS), or supercapacitor for short bursts
- BMS / fuel gauge (e.g., TI bq series or equivalent)
- MCU: low-power MCU (e.g., ARM Cortex-M0/M4 or ESP32-S3 with low-power options)
- Voltage/current sensors (INA219 or similar)
- Temp sensors (DS18B20, or thermistors)
- Radiance sensor (photodiode / TSL2591)
- RF module: primary WiFi7 module + low-power wake radio (BLE/LoRa) or wake-on-radio front-end

---

## Firmware API (telemetry + control)
Protocol: MQTT topic hierarchy (example)

Topics:
- `device/{id}/power/status` (retain 1)
- `device/{id}/power/telemetry` (periodic JSON)
- `device/{id}/power/control` (commands)

Telemetry JSON example:
```
{
  "id":"device-012",
  "powerSources":["solar","thermal"],
  "batteryPercent":82,
  "current_mW":140,
  "harvest_mW":220,
  "mode":"normal",
  "lastSignalRcv":16712345
}
```

Control examples (payload JSON):
- `{"mode":"low_power"}`
- `{"set_tx_power_db":8}`

Security: TLS for MQTT or secured MQTT over WebSockets, client certs or token-based auth.

---

## Scheduler / Behavior
- Low-level radio: always listen in ultra-low-power mode; MCU wakes on priority signal (wake-on-radio) or scheduled polling
- Adaptive duty cycling: adjust transmit frequency and power based on battery/farm state
- Graceful fallback: When energy critical, reduce sampling frequency, reduce tx power, and queue non-urgent data

---

## Dashboard Integration
- Display: harvested power (mW), battery %, temp, irradiance, estimated autonomy
- Controls: Set power mode, emergency sleep, enable/disable harvesters
- Alerts: low battery, over-temp, harvester fault

---

## Safety & Regulatory
- Proper battery charge profile and temperature cutoffs
- Overcurrent, reverse polarity and short-circuit protections
- IP ratings and environmental sealing for outdoor solar panels

---

## Next steps
- Prototype with off-the-shelf MPPT + TEG + MCU
- Implement the telemetry endpoints and a simple dashboard panel
- Validate adaptive scheduling in real-world conditions
