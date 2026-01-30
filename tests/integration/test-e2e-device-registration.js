import { spawn } from 'child_process';

const BASE = process.env.BASE || 'http://localhost:3001';

function wait(ms){return new Promise(r=>setTimeout(r,ms))}

async function waitForServer(timeout = 15000){
  const start = Date.now();
  while (Date.now() - start < timeout){
    try {
      const res = await fetch(`${BASE}/api/health`);
      if (res.ok) return true;
    } catch (e){}
    await wait(300);
  }
  throw new Error('Server did not become healthy in time');
}

async function run(){
  console.log('Starting server...');
  const server = spawn('node', ['server.js'], { cwd: process.cwd(), env: {...process.env, PORT: '3001'}, stdio: ['ignore','pipe','pipe'] });
  server.stdout.on('data', d => process.stdout.write(`[server] ${d}`));
  server.stderr.on('data', d => process.stderr.write(`[server.err] ${d}`));

  try {
    await waitForServer(15000);
    console.log('Server is healthy');

    console.log('Starting consumer...');
    const consumer = spawn('node', ['workers/deviceConsumer.js'], { cwd: process.cwd(), env: {...process.env, INGESTION_ENDPOINT: `${BASE}/api/ingestion/mock`}, stdio: ['ignore','pipe','pipe'] });
    consumer.stdout.on('data', d => process.stdout.write(`[consumer] ${d}`));
    consumer.stderr.on('data', d => process.stderr.write(`[consumer.err] ${d}`));

    const payload = {
      hardwareId: 'E2E-HW-0001',
      model: 'E2E-Model',
      firmwareVersion: 'e2e-0.1',
      location: 'test-lab',
      initialTelemetry: { battery: 100 }
    };

    const res = await fetch(`${BASE}/api/devices/register`, {
      method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)
    });

    if (res.status !== 202) {
      console.error('Expected 202 but got', res.status);
      console.error(await res.text());
      process.exit(2);
    }

    const body = await res.json();
    console.log('Enqueued:', body);
    const deviceId = body.deviceId;

    // Wait for consumer to process (poll status)
    let final = null;
    const pollStart = Date.now();
    while (Date.now() - pollStart < 30000){  // Increased timeout for async processing + retries
      const r = await fetch(`${BASE}/api/devices/${deviceId}`);
      if (r.status === 200){
        const j = await r.json();
        console.log('Status:', j.status);
        if (j.status === 'acknowledged') { final = j; break; }
        if (j.status === 'failed') {
          console.error('Device processing failed:', j);
          process.exit(5);
        }
      }
      await wait(500);
    }

    if (!final) {
      console.error('Device did not reach acknowledged state in time');
      process.exit(3);
    }

    console.log('✓ E2E flow succeeded:', final);
    process.exit(0);
  } catch (err) {
    console.error('Test failed:', err);
    process.exit(4);
  } finally {
    try { server.kill(); } catch(e){}
  }
}

run();
