(async () => {
  try {
    const res = await fetch('http://localhost:3000/api/proxy/networkbuster/info?simulate=1');
    const json = await res.json();
    console.log('status', res.status);
    console.log('x-proxy-simulated', res.headers.get('x-proxy-simulated'));
    console.log('body', JSON.stringify(json));
    if (!json.simulated) { console.error('expected simulated response'); process.exit(2); }
    console.log('test-proxy-simulate: OK');
    process.exit(0);
  } catch (err) {
    console.error('err', err);
    process.exit(2);
  }
})();