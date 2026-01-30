import express from 'express';
import crypto from 'crypto';
import { saveRegistration, updateStatus, getRegistration, transitionStatus } from '../lib/deviceStore.js';
import { enqueue } from '../lib/messageQueue.js';
import cryptoHash from 'crypto';

const router = express.Router();

// Simple validation middleware
function validateRegistration(req, res, next) {
  const body = req.body || {};
  if (!body.hardwareId || !body.model) {
    return res.status(400).json({ error: 'hardwareId and model are required' });
  }
  next();
}

// POST /api/devices/register
router.post('/register', validateRegistration, (req, res) => {
  const body = req.body;

  // canonical deviceId (if not provided generate one)
  const deviceId = body.deviceId || (Date.now().toString() + '-' + crypto.randomBytes(4).toString('hex'));

  // sanitize & hash sensitive identifiers
  const hashedHardwareId = cryptoHash.createHash('sha256').update(String(body.hardwareId)).digest('hex');

  const record = {
    deviceId,
    hardwareIdHash: hashedHardwareId,
    model: body.model,
    firmwareVersion: body.firmwareVersion || null,
    location: body.location || null,
    ts: body.ts || new Date().toISOString(),
    initialTelemetry: body.initialTelemetry || null,
    source: body.source || 'api'
  };

  // persist (prototype: local file)
  const saved = saveRegistration(record);

  // enqueue message for ingestion
  const msg = enqueue('device-registrations.v1', {
    deviceId: saved.deviceId,
    hardwareIdHash: saved.hardwareIdHash,
    model: saved.model,
    firmwareVersion: saved.firmwareVersion,
    location: saved.location,
    ts: saved.ts,
    initialTelemetry: saved.initialTelemetry,
    source: saved.source,
    traceId: crypto.randomUUID ? crypto.randomUUID() : (crypto.randomBytes(8).toString('hex'))
  });

  // mark status queued
  transitionStatus(saved.deviceId, 'queued', { queuedAt: new Date().toISOString(), queueMessageId: msg.id });

  res.status(202).json({ deviceId: saved.deviceId, status: 'queued', queueMessageId: msg.id });
});

// GET device status
router.get('/:deviceId', (req, res) => {
  const rec = getRegistration(req.params.deviceId);
  if (!rec) return res.status(404).json({ error: 'Device not found' });
  res.json(rec);
});

export default router;
