const fetch = require('node-fetch');
const child = require('child_process');
const fs = require('fs');
const path = require('path');

const server = child.spawn(process.execPath, [require.resolve('../../thruster/server.cjs')], { stdio: 'inherit', detached: true, env: Object.assign({}, process.env, { THRUSTER_ADMIN_KEY: 'adminkey123' }) });

function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  try {
    await wait(1200);
    const base = 'http://localhost:3800';
    // request access
    const reqBody = { githubUser: 'test-admin', publicKey: 'ssh-rsa AAAAB3TestKey', reason: 'integration test' };
    let res = await fetch(`${base}/admin/request-access`, { method: 'POST', body: JSON.stringify(reqBody), headers: { 'Content-Type': 'application/json' } });
    const j = await res.json();
    if (!j.ok) { console.error('request failed', j); process.exit(2); }
    const id = j.request && j.request.id;

    // list requests (admin)
    res = await fetch(`${base}/admin/requests`, { method: 'GET', headers: { 'x-admin-key': 'adminkey123' } });
    const list = await res.json();
    if (!list.ok) { console.error('list failed', list); process.exit(2); }

    // approve
    res = await fetch(`${base}/admin/approve`, { method: 'POST', headers: { 'x-admin-key': 'adminkey123', 'Content-Type': 'application/json' }, body: JSON.stringify({ id }) });
    const apr = await res.json();
    if (!apr.ok) { console.error('approve failed', apr); process.exit(2); }
    const scriptPath = apr.scriptPath;
    if (!fs.existsSync(scriptPath)) { console.error('script missing', scriptPath); process.exit(2); }

    console.log('test-admin-endpoints: OK');
    process.kill(-server.pid);
    process.exit(0);
  } catch (err) {
    console.error(err);
    process.kill(-server.pid);
    process.exit(2);
  }
})();