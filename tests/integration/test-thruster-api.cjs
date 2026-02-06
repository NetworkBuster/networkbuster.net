// Integration test for thruster API
const assert = require('assert');
const fetch = globalThis.fetch || require('node-fetch');
const app = require('../../thruster/server.cjs');

const server = app.listen(3801);

async function test() {
  console.log('Running thruster API integration test...');
  const opts = {
    initialMass: 1000,
    propellantAvailable: 300,
    isp: 300,
    maxThrust: 20000,
    maxG: 3,
    targetDeltaV: 200
  };

  const url = 'http://localhost:3801/plan';
  const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(opts) });
  const j = await res.json();
  assert.ok(j.ok === true, 'API should respond ok');
  assert.ok(j.multi && j.multi.segments && j.multi.segments.length > 0, 'multi plan present');

  console.log('Thruster API integration test passed.');
}

test().catch(err => { console.error(err); process.exit(1); }).finally(() => server.close());