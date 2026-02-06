// Unit tests for thrusterPhysics
const assert = require("assert");
const {
  computeDeltaV,
  propellantForDeltaV,
  planBurn,
  g0,
} = require("../../thruster/thrusterPhysics.cjs");

async function test() {
  console.log("Running thruster physics tests...");

  const isp = 300; // s (typical small engine sim)
  const initialMass = 1000; // kg
  const targetDV = 100; // m/s

  const prop = propellantForDeltaV(isp, initialMass, targetDV);
  assert.ok(prop > 0, "propellant should be positive for non-zero deltaV");

  const plan = planBurn({
    initialMass,
    propellantAvailable: prop + 10,
    isp,
    maxThrust: 20000, // N
    maxG: 3, // 3 g
    targetDeltaV: targetDV,
  });

  assert.ok(
    plan.possible === true,
    "plan should be possible with available propellant",
  );
  assert.ok(plan.peakG <= 3 + 1e-6, "peak g should be within limit");
  assert.ok(
    plan.propellantUsed <= prop + 1e-6,
    "used propellant should match required",
  );
  assert.ok(plan.burnTimeSeconds > 0, "burn time should be positive");

  // Also verify deltaV computation inverse
  const m0 = 1000;
  const mf = 900;
  const dv = computeDeltaV(isp, m0, mf);
  assert.ok(dv > 0, "deltaV should be positive for m0 > mf");

  console.log("Thruster physics tests passed.");
}

test().catch((err) => {
  console.error(err);
  process.exit(1);
});
