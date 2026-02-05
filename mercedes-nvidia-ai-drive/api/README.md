# API Reference
## Mercedes-NVIDIA AI Drive Platform

---

## Overview

This document provides the complete API reference for the Mercedes-NVIDIA AI Drive platform, covering vehicle APIs, cloud services, and integration endpoints.

---

## Vehicle APIs

### 1. Perception API

#### Get Current Perception State

```http
GET /api/v1/perception/state
```

**Response:**
```json
{
  "timestamp": "2026-02-05T12:34:56.789Z",
  "objects": [
    {
      "id": "obj_12345",
      "type": "vehicle",
      "position": {"x": 10.5, "y": -2.3, "z": 0.0},
      "velocity": {"x": 15.2, "y": 0.1, "z": 0.0},
      "confidence": 0.98
    }
  ],
  "lanes": [...],
  "traffic_lights": [...]
}
```

#### Get Sensor Data

```http
GET /api/v1/sensors/{sensor_type}/data
```

Parameters:
- `sensor_type`: camera, radar, lidar, ultrasonic

---

### 2. Planning API

#### Get Current Plan

```http
GET /api/v1/planning/trajectory
```

**Response:**
```json
{
  "trajectory": {
    "points": [
      {"x": 0, "y": 0, "t": 0, "v": 15.5},
      {"x": 1.5, "y": 0.1, "t": 0.1, "v": 15.6}
    ],
    "duration": 5.0,
    "confidence": 0.95
  }
}
```

#### Set Destination

```http
POST /api/v1/planning/destination
Content-Type: application/json

{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "preferences": {
    "route_type": "fastest",
    "avoid_highways": false
  }
}
```

---

### 3. Control API

#### Get Vehicle State

```http
GET /api/v1/control/state
```

**Response:**
```json
{
  "speed": 65.5,
  "acceleration": 0.2,
  "steering_angle": 2.5,
  "gear": "D",
  "autonomy_level": 3,
  "driver_attention": 0.95
}
```

---

## Cloud APIs

### 1. HD Map Service

#### Query Map Data

```http
POST /api/v1/maps/query
Authorization: Bearer {token}
Content-Type: application/json

{
  "center": {"lat": 37.7749, "lon": -122.4194},
  "radius": 1000,
  "layers": ["lanes", "traffic_signs", "traffic_lights"]
}
```

**Response:**
```json
{
  "map_version": "2026.02.05.001",
  "lanes": [...],
  "traffic_signs": [...],
  "dynamic_objects": [...]
}
```

#### Report Map Issue

```http
POST /api/v1/maps/report-issue
Authorization: Bearer {token}
Content-Type: application/json

{
  "position": {"lat": 37.7749, "lon": -122.4194},
  "issue_type": "missing_sign",
  "description": "Stop sign not in map",
  "severity": "high"
}
```

---

### 2. Fleet Management API

#### Upload Telemetry

```http
POST /api/v1/fleet/telemetry
Authorization: Bearer {token}
Content-Type: application/json

{
  "vin": "WDD1234567890",
  "timestamp": "2026-02-05T12:34:56.789Z",
  "metrics": {
    "miles_driven": 125.5,
    "autonomy_engaged": 98.2,
    "disengagements": 0,
    "alerts": []
  }
}
```

#### Request OTA Update

```http
POST /api/v1/fleet/ota/check-update
Authorization: Bearer {token}
Content-Type: application/json

{
  "vin": "WDD1234567890",
  "current_version": "2.0.1"
}
```

**Response:**
```json
{
  "update_available": true,
  "version": "2.1.0",
  "size_mb": 450,
  "release_notes": "Improved rainy weather performance",
  "estimated_install_time": 30
}
```

---

### 3. Analytics API

#### Query Vehicle Analytics

```http
GET /api/v1/analytics/vehicle/{vin}
Authorization: Bearer {token}

?start_date=2026-01-01&end_date=2026-02-01
```

**Response:**
```json
{
  "total_miles": 1250.5,
  "autonomous_miles": 1180.2,
  "disengagement_rate": 0.015,
  "safety_score": 98.5,
  "efficiency_score": 92.3
}
```

---

## WebSocket APIs

### Real-time Vehicle State

```javascript
const ws = new WebSocket('wss://api.networkbuster.net/v1/vehicle/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Vehicle state:', data);
};
```

**Message Format:**
```json
{
  "type": "state_update",
  "timestamp": "2026-02-05T12:34:56.789Z",
  "data": {
    "speed": 65.5,
    "position": {"lat": 37.7749, "lon": -122.4194},
    "autonomy_active": true
  }
}
```

---

## Authentication

### OAuth 2.0 Flow

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id={client_id}
&client_secret={client_secret}
&scope=vehicle.read vehicle.control
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "vehicle.read vehicle.control"
}
```

---

## Rate Limits

| Endpoint Category | Limit | Window |
|------------------|-------|--------|
| Vehicle APIs | 1000 req/min | Per vehicle |
| Cloud APIs | 10000 req/min | Per account |
| WebSocket | 100 msg/sec | Per connection |

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## SDK Support

### Python SDK

```python
from mercedes_nvidia import VehicleClient

client = VehicleClient(api_key="your_key")
state = client.perception.get_state()
print(f"Detected {len(state.objects)} objects")
```

### JavaScript SDK

```javascript
import { MercedesNVIDIA } from '@networkbuster/mercedes-nvidia-sdk';

const client = new MercedesNVIDIA({ apiKey: 'your_key' });
const trajectory = await client.planning.getTrajectory();
```

---

**API Version**: v1  
**Last Updated**: February 5, 2026  
**Support**: api-support@networkbuster.net
