// Unit tests for multi-segment burn planner
const assert = require('assert');
const { planMultiSegmentBurn, planBurn } = require('../../thruster/thrusterPhysics.cjs');

async function test() {
  console.log('Running multi-segment planner tests...');
  const opts = {
    initialMass: 1000,
    propellantAvailable: 300,
    isp: 300,
    maxThrust: 20000,
    maxG: 3,
    targetDeltaV: 200,
    preferredThrust: 15000,
    maxSegments: 4
  };

  const single = planBurn(opts);
  const multi = planMultiSegmentBurn(opts);

  assert.ok(single.possible === true, 'single segment should be possible');
  assert.ok(multi.possible === true, 'multi segment should be possible');
  // Multi-segment should not exceed maxG and should have lower or equal peakG
  assert.ok(multi.totals.peakG <= opts.maxG + 1e-6, 'multi peakG should be within limit');
  assert.ok(multi.totals.peakG <= single.peakG + 1e-6, 'multi peakG should be <= single peakG');

  console.log('Multi-segment planner tests passed.');
}

test().catch(err => { console.error(err); process.exit(1); });