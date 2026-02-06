const assert = require("assert");
const {
  planOptimizedMultiSegment,
  planOptimizedMultiSegmentContinuous,
} = require("../../thruster/thrusterPhysics.cjs");

// basic smoke test: continuous optimizer should produce a score no worse than grid search
function approxLE(a, b) {
  return a <= b + 1e-6;
}

const opts = {
  initialMass: 1000,
  propellantAvailable: 500,
  isp: 300,
  maxThrust: 15000,
  maxG: 3,
  targetDeltaV: 200,
  maxSegments: 3,
};

const grid = planOptimizedMultiSegment(opts, { steps: 8, cost: "min_peakG" });
const cont = planOptimizedMultiSegmentContinuous(opts, {
  cost: "min_peakG",
  maxIter: 200,
});

assert(grid.possible, "grid found a feasible allocation");
assert(cont.possible, "continuous found a feasible allocation");
console.log("grid.score", grid.score, "continuous.score", cont.score);
assert(
  approxLE(cont.score, grid.score),
  "continuous should be as-good-or-better than grid in score",
);
console.log("test-thruster-continuous: OK");
