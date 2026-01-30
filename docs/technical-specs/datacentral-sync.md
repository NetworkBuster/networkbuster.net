# DataCentral Synchronization Module (DCSM)

## Overview
The **DataCentral Synchronization Module (DCSM)** is a core component of the NetworkBuster project, designed specifically to handle the challenges of lunar-to-Earth data telemetry. It ensures that the Lunar Recycling System stays in sync with the central command hub (DataCentral) despite significant communication latencies and periodic connection blackouts.

## Key Features
- **High Latency Optimization**: Uses delta-compression to minimize the size of each telemetry packet.
- **Resilient Caching**: Automatically caches data locally when the uplink is unavailable, with support for up to 14 days of retention.
- **End-to-End Encryption**: All data transmitted to DataCentral is AES-256 encrypted at the source.
- **Delta Sync**: Only transmits changes set since the last successful sync to conserve bandwidth.

## Technical Specifications
- **Sync Interval**: Default 300 seconds (configurable).
- **Communication Protocol**: Simulated MQTT over Satellite Uplink.
- **Data Format**: Optimized JSON (Protocol Buffers support planned for v1.2).
- **Local Cache Path**: `./data/sync-cache.json`.

## Implementation
The module is implemented as a Node.js class that can be easily integrated into any NetworkBuster server component.

```javascript
const DataCentralSync = require('./datacentral-sync-module');
const sync = new DataCentralSync();
sync.start();
```

---
*Created by Antigravity AI for the NetworkBuster Research Division.*
