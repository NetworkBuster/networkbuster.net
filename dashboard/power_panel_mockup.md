# Dashboard Power Panel Mockup

## Purpose
Wireframe and sample integration notes for a per-device Power Panel.

## Features
- Real-time chart (harvest mW, battery %)
- Status badges: `mode`, `lastSignalRcv`
- Controls: Set `mode` (normal/low_power), set tx power, emergency sleep

## Sample MQTT integration (JS)

- Subscribe to `device/{id}/power/telemetry` and update UI
- Publish to `device/{id}/power/control` for control actions

Sample telemetry handler (pseudocode):
```
client.on('message', (topic, payload) => {
  if(topic == `device/${id}/power/telemetry`) {
    updateChart(payload.harvest_mw, payload.batteryPercent)
    updateStatus(payload.mode)
  }
})
```

## HTML mockup (concept)
- Top: device name + power sources icons
- Left: real-time line chart
- Right: battery % donut + controls
- Bottom: event log and alerts

---

I can convert this into an actual React component / static HTML + JS sample if you prefer. Reply "React" or "HTML".