// thruster/thrusterPhysics.cjs
// Simple, safe thruster planning utilities (simulation-only). Not an instruction
// for building hardware. Designed to compute safe burn plans respecting human
// g-force limits and available propellant.

const g0 = 9.80665; // m/s^2

/**
 * Compute delta-v achievable with Tsiolkovsky rocket equation
 * @param {number} isp - Specific impulse in seconds
 * @param {number} m0 - initial total mass (kg)
 * @param {number} mf - final total mass (kg)
 * @returns {number} deltaV in m/s
 */
function computeDeltaV(isp, m0, mf) {
  if (m0 <= mf) return 0;
  return isp * g0 * Math.log(m0 / mf);
}

/**
 * Compute final mass after applying deltaV (invert Tsiolkovsky)
 * @param {number} isp - s
 * @param {number} m0 - initial mass kg
 * @param {number} deltaV - desired m/s
 * @returns {number} mf (kg) final mass
 */
function computeFinalMassForDeltaV(isp, m0, deltaV) {
  if (deltaV <= 0) return m0;
  const mf = m0 / Math.exp(deltaV / (isp * g0));
  return mf;
}

/**
 * Compute propellant required for a desired deltaV
 * @param {number} isp - seconds
 * @param {number} m0 - initial mass kg
 * @param {number} deltaV - m/s
 * @returns {number} propellant kg required (m0 - mf)
 */
function propellantForDeltaV(isp, m0, deltaV) {
  const mf = computeFinalMassForDeltaV(isp, m0, deltaV);
  return Math.max(0, m0 - mf);
}

/**
 * Plan a burn that achieves targetDeltaV while respecting maxG and available fuel.
 * - Chooses thrust <= maxThrust and not exceeding maxG at initial mass
 * - Computes mass flow mdot = thrust / (Isp * g0)
 * - Computes propellant needed by Tsiolkovsky and burn time = propellant / mdot
 *
 * @param {object} opts
 * @param {number} opts.initialMass - total initial mass (kg)
 * @param {number} opts.propellantAvailable - available propellant mass (kg)
 * @param {number} opts.isp - specific impulse in seconds
 * @param {number} opts.maxThrust - maximum thrust engine can supply (N)
 * @param {number} opts.maxG - maximum allowed g-force (in Gs) for crew safety (e.g., 3)
 * @param {number} opts.targetDeltaV - desired delta-v in m/s
 * @param {number} [opts.preferredThrust] - optional preferred thrust (N)
 * @returns {object} plan {possible, thrust, burnTime, propellantUsed, peakG}
 */
function planBurn(opts) {
  const { initialMass, propellantAvailable, isp, maxThrust, maxG, targetDeltaV, preferredThrust } = opts;
  if (targetDeltaV <= 0) return { possible: true, thrust: 0, burnTime: 0, propellantUsed: 0, peakG: 0 };

  // compute propellant required ignoring thrust/time
  const requiredProp = propellantForDeltaV(isp, initialMass, targetDeltaV);
  if (requiredProp > propellantAvailable + 1e-9) {
    return { possible: false, reason: 'insufficient_propellant', requiredProp, propellantAvailable };
  }

  // determine thrust limited by engine and maxG at start
  // max thrust allowed by g limit: T_max_g = maxG * initialMass * g0
  const maxThrustByG = maxG * initialMass * g0;
  let thrust = Math.min(maxThrust || Infinity, maxThrustByG);
  if (preferredThrust) thrust = Math.min(thrust, preferredThrust);
  if (thrust <= 0) return { possible: false, reason: 'zero_thrust' };

  // compute mdot and burnTime
  const mdot = thrust / (isp * g0); // kg/s
  const burnTime = requiredProp / mdot; // seconds

  // peak g is thrust / (initialMass * g0)
  const peakG = thrust / (initialMass * g0);

  return {
    possible: true,
    thrust,
    burnTimeSeconds: burnTime,
    propellantUsed: requiredProp,
    peakG
  };
}

/**
 * Plan a multi-segment burn to meet targetDeltaV while minimizing peak G.
 * Strategy: try 1..maxSegments segments, splitting deltaV evenly per segment.
 * For each segment simulate mass change and ensure propellant availability and
 * peak G limits. Prefer lower peak G.
 *
 * @param {object} opts - same as planBurn plus:
 *   maxSegments: number (default 3)
 *   allowUnequal: boolean (default false) - can implement later
 * @returns {object} {possible, segments: [{deltaV, thrust, burnTimeSeconds, propellantUsed, startMass, endMass, peakG}], totals: {propellantUsed, burnTimeSeconds, peakG}}
 */
function planMultiSegmentBurn(opts) {
  const maxSegments = opts.maxSegments || 3;
  const perfs = [];

  // try from 1 to maxSegments and pick the one with lowest peakG (while keeping reasonable total burn time)
  let best = null;

  for (let segments = 1; segments <= maxSegments; segments++) {
    const segDelta = opts.targetDeltaV / segments;
    let mass = opts.initialMass;
    let remainingProp = opts.propellantAvailable;
    const segs = [];
    let feasible = true;
    let peakGOverall = 0;
    let totalBurn = 0;
    let totalProp = 0;

    for (let i = 0; i < segments; i++) {
      const dV = segDelta;
      // compute propellant needed for this deltaV starting at current mass
      const mf = computeFinalMassForDeltaV(opts.isp, mass, dV);
      const propNeeded = Math.max(0, mass - mf);
      if (propNeeded - remainingProp > 1e-9) { feasible = false; break; }

      // thrust limited by engine and maxG
      const maxThrustByG = opts.maxG * mass * g0;
      let thrust = Math.min(opts.maxThrust || Infinity, maxThrustByG);
      if (opts.preferredThrust) thrust = Math.min(thrust, opts.preferredThrust);
      if (thrust <= 0) { feasible = false; break; }

      const mdot = thrust / (opts.isp * g0);
      const burnTime = mdot > 0 ? propNeeded / mdot : Infinity;
      const peakG = thrust / (mass * g0);

      segs.push({ deltaV: dV, thrust, burnTimeSeconds: burnTime, propellantUsed: propNeeded, startMass: mass, endMass: mf, peakG });

      mass = mf;
      remainingProp -= propNeeded;
      peakGOverall = Math.max(peakGOverall, peakG);
      totalBurn += burnTime;
      totalProp += propNeeded;
    }

    if (feasible) {
      const candidate = { segments: segs, totals: { propellantUsed: totalProp, burnTimeSeconds: totalBurn, peakG: peakGOverall }, segmentsCount: segments };
      // prefer lower peakG; if tie prefer fewer segments (quicker)
      if (!best || candidate.totals.peakG < best.totals.peakG - 1e-9 || (Math.abs(candidate.totals.peakG - best.totals.peakG) < 1e-9 && candidate.totals.burnTimeSeconds < best.totals.burnTimeSeconds)) {
        best = candidate;
      }
    }
  }

  if (!best) return { possible: false, reason: 'insufficient_propellant_or_constraints' };
  return { possible: true, ...best };
}

/**
 * Plan optimized multi-segment deltaV allocation using a small discrete search.
 * Supports cost functions: 'min_peakG', 'min_propellant', 'min_time'.
 * This is a conservative, small-grid search for prototyping (not for flight use).
 */
function planOptimizedMultiSegment(opts, options = {}) {
  const cost = options.cost || 'min_peakG';
  const maxSegments = opts.maxSegments || 3;
  const steps = options.steps || 6; // discretize target deltaV into `steps` quanta per allocation
  const target = opts.targetDeltaV;

  function genAlloc(nSegments, steps) {
    const out = [];
    function helper(k, remaining, acc) {
      if (k === 1) return out.push([...acc, remaining]);
      for (let i = 0; i <= remaining; i++) helper(k - 1, remaining - i, [...acc, i]);
    }
    helper(nSegments, steps, []);
    return out.map(parts => parts.map(p => (p / steps) * target));
  }

  function evaluateAllocation(alloc) {
    let mass = opts.initialMass;
    let remProp = opts.propellantAvailable;
    let totalProp = 0;
    let totalTime = 0;
    let peakG = 0;
    const segs = [];

    for (const dV of alloc) {
      if (dV <= 0) { segs.push(null); continue; }
      const mf = computeFinalMassForDeltaV(opts.isp, mass, dV);
      const propNeeded = Math.max(0, mass - mf);
      if (propNeeded - remProp > 1e-9) return null;
      const maxThrustByG = opts.maxG * mass * g0;
      let thrust = Math.min(opts.maxThrust || Infinity, maxThrustByG);
      if (opts.preferredThrust) thrust = Math.min(thrust, opts.preferredThrust);
      if (thrust <= 0) return null;
      const mdot = thrust / (opts.isp * g0);
      const burnTime = mdot > 0 ? propNeeded / mdot : Infinity;
      const segPeakG = thrust / (mass * g0);
      segs.push({ deltaV: dV, startMass: mass, endMass: mf, propellantUsed: propNeeded, burnTimeSeconds: burnTime, thrust, peakG: segPeakG });
      mass = mf;
      remProp -= propNeeded;
      totalProp += propNeeded;
      totalTime += burnTime;
      peakG = Math.max(peakG, segPeakG);
    }

    let score;
    if (cost === 'min_propellant') score = totalProp;
    else if (cost === 'min_time') score = totalTime;
    else score = peakG;

    return { segs, totals: { propellantUsed: totalProp, burnTimeSeconds: totalTime, peakG }, score };
  }

  let best = null;
  for (let s = 1; s <= maxSegments; s++) {
    const allocs = genAlloc(s, steps);
    for (const alloc of allocs) {
      if (!alloc.some(v => v > 1e-12)) continue;
      const evaled = evaluateAllocation(alloc);
      if (!evaled) continue;
      if (!best || evaled.score < best.score - 1e-9 || (Math.abs(evaled.score - best.score) < 1e-9 && evaled.totals.burnTimeSeconds < best.totals.burnTimeSeconds)) {
        best = { segments: evaled.segs, totals: evaled.totals, score: evaled.score, segmentsCount: s, allocation: alloc };
      }
    }
  }

  if (!best) return { possible: false, reason: 'no_feasible_allocation' };
  return { possible: true, ...best };
}

/**
 * Heuristic optimizer using random perturbations + hill-climb with temperature (simulated annealing style).
 * Returns a feasible allocation optimized for the given cost function.
 */
function planOptimizedMultiSegmentHeuristic(opts, options = {}) {
  const cost = options.cost || 'min_peakG';
  const maxSegments = opts.maxSegments || 3;
  const steps = options.steps || 12; // resolution for initial seed
  const target = opts.targetDeltaV;
  const iterations = options.iterations || 2000;
  const tempStart = options.tempStart || 1.0;
  const tempEnd = options.tempEnd || 0.001;

  function evalAlloc(alloc) {
    let mass = opts.initialMass;
    let remProp = opts.propellantAvailable;
    let totalProp = 0;
    let totalTime = 0;
    let peakG = 0;
    const segs = [];
    for (const dV of alloc) {
      if (dV <= 0) { segs.push(null); continue; }
      const mf = computeFinalMassForDeltaV(opts.isp, mass, dV);
      const propNeeded = Math.max(0, mass - mf);
      if (propNeeded - remProp > 1e-9) return null;
      const maxThrustByG = opts.maxG * mass * g0;
      let thrust = Math.min(opts.maxThrust || Infinity, maxThrustByG);
      if (opts.preferredThrust) thrust = Math.min(thrust, opts.preferredThrust);
      if (thrust <= 0) return null;
      const mdot = thrust / (opts.isp * g0);
      const burnTime = mdot > 0 ? propNeeded / mdot : Infinity;
      const segPeakG = thrust / (mass * g0);
      segs.push({ deltaV: dV, startMass: mass, endMass: mf, propellantUsed: propNeeded, burnTimeSeconds: burnTime, thrust, peakG: segPeakG });
      mass = mf;
      remProp -= propNeeded;
      totalProp += propNeeded;
      totalTime += burnTime;
      peakG = Math.max(peakG, segPeakG);
    }
    let score = (cost === 'min_propellant') ? totalProp : (cost === 'min_time' ? totalTime : peakG);
    return { segs, totals: { propellantUsed: totalProp, burnTimeSeconds: totalTime, peakG }, score };
  }

  // seed: equal split allocations and keep best
  function seedAlloc(s) {
    const base = target / s;
    return Array.from({ length: s }, () => base);
  }

  function mutateAlloc(alloc) {
    // random small transfer between two segments (keeps sum constant)
    const s = alloc.length;
    const i = Math.floor(Math.random() * s);
    let j = Math.floor(Math.random() * s);
    while (j === i && s > 1) j = Math.floor(Math.random() * s);
    const delta = (Math.random() - 0.5) * (target / (s * 8));
    const next = alloc.slice();
    next[i] = Math.max(0, next[i] + delta);
    next[j] = Math.max(0, next[j] - delta);
    return next;
  }

  let best = null;
  // initialize with seeds for different segment counts
  for (let s = 1; s <= maxSegments; s++) {
    const alloc = seedAlloc(s);
    const evaled = evalAlloc(alloc);
    if (!evaled) continue;
    const candidate = { alloc, evaled };
    if (!best || evaled.score < best.evaled.score) best = candidate;

    // run annealing starting from this seed
    let current = candidate;
    let temp = tempStart;
    for (let it = 0; it < iterations; it++) {
      const tFrac = it / iterations;
      temp = tempStart * Math.pow(tempEnd / tempStart, tFrac);
      const trialAlloc = mutateAlloc(current.alloc);
      const trialEval = evalAlloc(trialAlloc);
      if (!trialEval) continue;
      const d = trialEval.score - current.evaled.score;
      if (d < 0 || Math.exp(-d / (temp + 1e-12)) > Math.random()) {
        current = { alloc: trialAlloc, evaled: trialEval };
      }
      if (current.evaled.score < best.evaled.score - 1e-12) best = current;
    }
  }

  if (!best) return { possible: false, reason: 'no_feasible_allocation' };
  return { possible: true, segments: best.evaled.segs, totals: best.evaled.totals, allocation: best.alloc, score: best.evaled.score };
}

module.exports = {
  computeDeltaV,
  computeFinalMassForDeltaV,
  propellantForDeltaV,
  planBurn,
  planMultiSegmentBurn,
  planOptimizedMultiSegment,
  planOptimizedMultiSegmentHeuristic,
  g0
};
