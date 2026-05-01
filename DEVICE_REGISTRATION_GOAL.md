# Device Registration → Neural Network

**Overview**
This document specifies the new project goal for builders: when a new device registers with NetworkBuster, its registration and initial telemetry must be validated, persisted, and forwarded into the neural network ingestion pipeline for training or inference. This capability enables device-aware models and closed-loop improvements.

## Goal (one-liner)
Pass every new device registration into the neural network ingestion pipeline reliably, securely, and with full observability.

## Priority
- **Priority:** High (project-level goal)
- **Owner:** platform / ingestion team (assign on project board)

## Acceptance Criteria
1. POST /api/devices/register returns canonical device ID and registration status.
2. Registration payload is validated and stored in device registry (persistent DB). Schema is versioned.
3. A registration event is enqueued to an ingestion topic (e.g., Azure Service Bus, Kafka, or Azure Event Grid).
4. Neural network ingestion service consumes the event, returns acknowledgement, and registration status is updated in the registry (queued → processed → acknowledged or failed).
5. Automated E2E test that simulates a device registration and verifies processed status.
6. Metrics/alerts: registration rate, ingestion queue lag, processing success/failure, and SLA violation alerts.

## Data model (minimum)
DeviceRegistration {
  deviceId (string) // provided by device or generated
  hardwareId (string) // device serial/MAC/fingerprint
  model (string) // device model
  firmwareVersion (string)
  location (string | geo-coords)
  ts (ISO8601) // registration timestamp
  initialTelemetry: { battery, temp, sensors: {...} } // optional
}

## API Spec (example)
- POST /api/devices/register
  - input: DeviceRegistration payload (JSON)
  - responses:
    - 201 Created { deviceId, status: 'registered' }
    - 202 Accepted { deviceId, status: 'queued' }
    - 400 Bad Request

Authentication: API key or OAuth. Rate limit per IP/credential.

## Ingestion contract
- Message schema must match DeviceRegistration with metadata: {source, version, traceId}
- Messages delivered to topic: `device-registrations.v1` with at-least-once delivery
- Consumer (ingestion microservice) must return processing result to `device-registration-results` topic or call back API to update status

## Security & Privacy
- Validate and sanitize all fields
- Store sensitive identifiers hashed or encrypted at rest
- Enforce ACLs and authenticated endpoints
- Log access and changes for audits

## Reliability
- Use a durable queue (retry/backoff policy)
- Implement idempotency keys (deviceId + ts) to avoid duplicate processing
- Provide op metrics and health endpoints

## Observability
- Traces: Attach a traceId from API -> queue -> ingestion consumer -> model
- Metrics: registration_count, registration_errors, ingestion_lag_seconds, ingestion_success_rate
- Logs: structured logs with correlation IDs

## Tests
- Unit tests: validation, schema, DB write
- Integration tests: API -> DB -> queue (mock) -> ingestion (mock)
- E2E test: bring up a test ingestion consumer and verify registration processed

## Implementation suggestions for builders
1. Add `POST /api/devices/register` with JSON schema validation using existing API framework (e.g., express + Joi or equivalent).
2. Persist registrations in a `devices` collection/table with status and audit fields.
3. Use `az acr build` container or existing unix-friendly workers to host ingestion consumer.
4. Publish a message to Azure Service Bus / Kafka topic with schema and trace context.
5. Create a small ingestion worker that reads topic and calls model ingestion REST or gRPC endpoint.
6. Add monitoring dashboards and alerts in observability platform (Log Analytics / Prometheus).

## Suggested Milestones (for PRs)
- M1 API + DB schema + unit tests
- M2 Queue publish + consumer (test harness)
- M3 Ingestion acknowledgement + status transitions + E2E test
- M4 Security review + production runbook

## Notes
- Keep the message schema versioned and backward-compatible.
- Document the exact contract in `api/schema/device-registration.json` when ready.

---

Add this file as the canonical specification for builders and link from `PROJECT-SUMMARY.md` and any relevant docs.
