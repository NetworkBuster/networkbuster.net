import fetch from 'node-fetch';

const BASE = process.env.BASE || 'http://localhost:3001';

async function run() {
  console.log('Testing POST /api/devices/register against', BASE);
  const payload = {
    hardwareId: 'TEST-HW-1234',
    model: 'NB-Test-Model-1',
    firmwareVersion: '0.0.1-test',
    location: 'lab-1',
    initialTelemetry: { battery: 98 }
  };

  const res = await fetch(`${BASE}/api/devices/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const json = await res.json();
  console.log('Status', res.status);
  console.log(JSON.stringify(json, null, 2));

  if (res.status !== 202) {
    process.exit(1);
  }

  console.log('✓ Registration accepted and queued.');
}

run().catch(e => { console.error(e); process.exit(2); });
