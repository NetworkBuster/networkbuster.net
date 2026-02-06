const assert = require("assert");
const { separateAfterDrift } = require("../../thruster/separation.cjs");

(async () => {
  // valid separation without requiring 'even' constraint
  const opts = {
    initialMass: 1000,
    propellantAvailable: 600,
    isp: 300,
    maxThrust: 20000,
    maxG: 5,
    targetDeltaV: 100,
    maxSegments: 3,
  };

  const res = await separateAfterDrift(opts, {
    driftSeconds: 10,
    onlyIfEven: false,
  });
  assert(
    res.separated,
    "separation should be performed when onlyIfEven=false and plan feasible",
  );
  assert(res.summary && typeof res.summary.driftDistance === "number");

  // invalid drift
  const bad = await separateAfterDrift(opts, { driftSeconds: 0 });
  assert(!bad.separated && bad.reason === "invalid_drift_seconds");
  console.log("test-separation: OK");
})();
