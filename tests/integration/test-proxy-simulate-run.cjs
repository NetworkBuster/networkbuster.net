const child = require('child_process');
const fetch = require('node-fetch');

(async () => {
  const server = child.spawn(process.execPath, [require.resolve('../../server.js')], { env: Object.assign({}, process.env, { PORT: '3030' }), stdio: ['ignore', 'pipe', 'pipe'] });

  server.stdout.on('data', d => process.stdout.write('[server] ' + d.toString()));
  server.stderr.on('data', d => process.stderr.write('[server] ' + d.toString()));

  function wait(ms) { return new Promise(r => setTimeout(r, ms)); }
  await wait(800);

  try {
    const res = await fetch('http://localhost:3030/api/proxy/networkbuster/info?simulate=1');
    const body = await res.json();
    console.log('status', res.status);
    console.log('x-proxy-simulated', res.headers.get('x-proxy-simulated'));
    console.log('body', JSON.stringify(body));
    if (!body.simulated) { console.error('expected simulated response'); process.exit(2); }
    console.log('test-proxy-simulate-run: OK');
    server.kill();
    process.exit(0);
  } catch (err) {
    console.error('err', err);
    server.kill();
    process.exit(2);
  }
})();