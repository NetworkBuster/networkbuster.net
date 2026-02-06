// Unit tests for optimized allocation
const assert = require('assert');
const { planOptimizedMultiSegment, planMultiSegmentBurn, planBurn } = require('../../thruster/thrusterPhysics.cjs');

async function test() {
  console.log('Running optimizer tests...');
  const opts = {
    initialMass: 1000,
    propellantAvailable: 400,
    isp: 300,
    maxThrust: 20000,
    maxG: 3,
    targetDeltaV: 300,
    maxSegments: 4
  };

  const opt = planOptimizedMultiSegment(opts, { cost: 'min_peakG', steps: 8 });
  assert.ok(opt.possible, 'optimized allocation should be possible');
  // Ensure totals are consistent
  assert.ok(opt.totals.propellantUsed <= opts.propellantAvailable + 1e-6, 'should not exceed propellant');

  // Compare peakG of optimized vs single plan
  const single = planBurn(opts);
  assert.ok(single.possible, 'single plan possible');
  assert.ok(opt.totals.peakG <= single.peakG + 1e-6, 'optimized peakG should be <= single peakG');

  console.log('Optimizer tests passed.');
}

test().catch(err => { console.error(err); process.exit(1); });