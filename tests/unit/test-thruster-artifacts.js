// Unit test for thruster artifact generation
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { run } = require('../../thruster/generateArtifacts');

async function test() {
    console.log('Running thruster artifacts generator test...');
    const res = await run();
    assert.ok(res.outDir && fs.existsSync(res.outDir), 'outDir should exist');
    assert.ok(res.zipPath && fs.existsSync(res.zipPath), 'zip should exist');
    if (res.manifestPath) {
        assert.ok(fs.existsSync(res.manifestPath), 'manifest should exist');
        const m = JSON.parse(fs.readFileSync(res.manifestPath, 'utf8'));
        assert.ok(m.files && Array.isArray(m.files), 'manifest.files should be an array');
    }
    if (res.telemetryPath) {
        assert.ok(fs.existsSync(res.telemetryPath), 'telemetry CSV should exist');
        const txt = fs.readFileSync(res.telemetryPath, 'utf8');
        assert.ok(txt.includes('timestamp'), 'telemetry CSV should contain header');
    }
    console.log('Thruster artifact tests passed.');
}

test().catch(err => { console.error(err); process.exit(1); });