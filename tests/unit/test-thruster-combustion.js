// Simple unit test for thruster/combustion.js
const assert = require('assert');
const { isGitAvailable, combustionStatus } = require('../../thruster/combustion');

async function runTests() {
    console.log('Running thruster combustion tests...');
    // isGitAvailable should return a boolean
    const gitAvail = isGitAvailable();
    assert.strictEqual(typeof gitAvail, 'boolean', 'isGitAvailable should be boolean');

    // combustionStatus should resolve to a string
    const status = await combustionStatus();
    assert.ok(typeof status === 'string', 'combustionStatus should return a string');

    console.log('All thruster tests passed');
}

runTests().catch(err => { console.error('Test failed:', err); process.exit(1); });