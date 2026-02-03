import fs from 'fs';
import { promises as fsPromises } from 'fs';
import path from 'path';
import crypto from 'crypto';

const dataDir = path.join(process.cwd(), 'data', 'devices');

async function ensureDir() {
  try {
    await fsPromises.access(dataDir);
  } catch {
    await fsPromises.mkdir(dataDir, { recursive: true });
  }
}

export async function saveRegistration(reg) {
  await ensureDir();
  const id = reg.deviceId || (Date.now().toString() + '-' + crypto.randomBytes(4).toString('hex'));
  const record = Object.assign({
    deviceId: id,
    status: 'registered',
    createdAt: new Date().toISOString()
  }, reg);

  const fn = path.join(dataDir, `${id}.json`);
  await fsPromises.writeFile(fn, JSON.stringify(record, null, 2), 'utf8');
  return record;
}

export async function getRegistration(deviceId) {
  const fn = path.join(dataDir, `${deviceId}.json`);
  try {
    const data = await fsPromises.readFile(fn, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

export async function updateStatus(deviceId, status, extra = {}) {
  const rec = await getRegistration(deviceId);
  if (!rec) return null;
  rec.status = status;
  rec.updatedAt = new Date().toISOString();
  Object.assign(rec, extra);
  const fn = path.join(dataDir, `${deviceId}.json`);
  await fsPromises.writeFile(fn, JSON.stringify(rec, null, 2), 'utf8');
  return rec;
}

export async function listRegistrations() {
  await ensureDir();
  const files = await fsPromises.readdir(dataDir);
  const jsonFiles = files.filter(f => f.endsWith('.json'));
  
  // Read all files in parallel for better performance
  const results = await Promise.all(
    jsonFiles.map(async (f) => {
      try {
        const data = await fsPromises.readFile(path.join(dataDir, f), 'utf8');
        return JSON.parse(data);
      } catch (err) {
        console.error(`Error reading ${f}:`, err.message);
        return null;
      }
    })
  );
  
  return results.filter(r => r !== null);
}

// Status transition validation
const VALID_TRANSITIONS = {
  'registered': ['queued'],
  'queued': ['processing', 'failed'],
  'processing': ['acknowledged', 'failed'],
  'acknowledged': [],
  'failed': ['queued'] // allow retry
};

export async function transitionStatus(deviceId, newStatus, extra = {}) {
  const rec = await getRegistration(deviceId);
  if (!rec) return null;
  
  const currentStatus = rec.status;
  if (!VALID_TRANSITIONS[currentStatus]?.includes(newStatus)) {
    throw new Error(`Invalid status transition from ${currentStatus} to ${newStatus}`);
  }
  
  return await updateStatus(deviceId, newStatus, extra);
}
