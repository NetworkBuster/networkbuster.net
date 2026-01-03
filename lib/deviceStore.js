import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const dataDir = path.join(process.cwd(), 'data', 'devices');

function ensureDir() {
  if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });
}

export function saveRegistration(reg) {
  ensureDir();
  const id = reg.deviceId || (Date.now().toString() + '-' + crypto.randomBytes(4).toString('hex'));
  const record = Object.assign({
    deviceId: id,
    status: 'registered',
    createdAt: new Date().toISOString()
  }, reg);

  const fn = path.join(dataDir, `${id}.json`);
  fs.writeFileSync(fn, JSON.stringify(record, null, 2), 'utf8');
  return record;
}

export function getRegistration(deviceId) {
  const fn = path.join(dataDir, `${deviceId}.json`);
  if (!fs.existsSync(fn)) return null;
  return JSON.parse(fs.readFileSync(fn, 'utf8'));
}

export function updateStatus(deviceId, status, extra = {}) {
  const rec = getRegistration(deviceId);
  if (!rec) return null;
  rec.status = status;
  rec.updatedAt = new Date().toISOString();
  Object.assign(rec, extra);
  const fn = path.join(dataDir, `${deviceId}.json`);
  fs.writeFileSync(fn, JSON.stringify(rec, null, 2), 'utf8');
  return rec;
}

export function listRegistrations() {
  ensureDir();
  return fs.readdirSync(dataDir).filter(f => f.endsWith('.json')).map(f => JSON.parse(fs.readFileSync(path.join(dataDir, f), 'utf8')));
}

// Status transition validation
const VALID_TRANSITIONS = {
  'registered': ['queued'],
  'queued': ['processing', 'failed'],
  'processing': ['acknowledged', 'failed'],
  'acknowledged': [],
  'failed': ['queued'] // allow retry
};

export function transitionStatus(deviceId, newStatus, extra = {}) {
  const rec = getRegistration(deviceId);
  if (!rec) return null;
  
  const currentStatus = rec.status;
  if (!VALID_TRANSITIONS[currentStatus]?.includes(newStatus)) {
    throw new Error(`Invalid status transition from ${currentStatus} to ${newStatus}`);
  }
  
  return updateStatus(deviceId, newStatus, extra);
}
