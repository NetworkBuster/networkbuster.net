// Unit test for heuristic optimizer
const assert = require("assert");
const {
  planOptimizedMultiSegmentHeuristic,
  planBurn,
} = require("../../thruster/thrusterPhysics.cjs");

async function test() {
  console.log("Running heuristic optimizer tests...");
  const opts = {
    initialMass: 1000,
    propellantAvailable: 400,
    isp: 300,
    maxThrust: 20000,
    maxG: 3,
    targetDeltaV: 300,
    maxSegments: 4,
  };

  const single = planBurn(opts);
  const h = planOptimizedMultiSegmentHeuristic(opts, {
    cost: "min_peakG",
    iterations: 800,
  });
  assert.ok(h.possible, "heuristic should produce a feasible allocation");
  assert.ok(
    h.totals.propellantUsed <= opts.propellantAvailable + 1e-6,
    "should not exceed propellant",
  );
  assert.ok(
    h.totals.peakG <= single.peakG + 1e-6,
    "heuristic should reduce or equal peakG vs single",
  );

  console.log("Heuristic optimizer tests passed.");
}

test().catch((err) => {
  console.error(err);
  process.exit(1);
});
