const fetch = (typeof global.fetch === 'function') ? global.fetch : require('node-fetch');
const { planMultiSegmentBurn } = require('./thrusterPhysics.cjs');

/**
 * Simulate separation after a drift period.
 * opts: same plan options (initialMass, propellantAvailable, isp, maxG, maxThrust, targetDeltaV, maxSegments)
 * options: { driftSeconds, onlyIfEven=true, separationDeltaV=0, detachedMass (kg), notifyWebhook }
 * Returns { separated, reason?, summary, timeSeries, notifyResult? }
 */
function separateAfterDrift(opts, options = {}) {
  const driftSeconds = Number(options.driftSeconds || 0);
  if (driftSeconds <= 0) return { separated: false, reason: 'invalid_drift_seconds' };
  const onlyIfEven = options.onlyIfEven === undefined ? true : Boolean(options.onlyIfEven);
  const separationDeltaV = Number(options.separationDeltaV || 0);
  const detachedMass = (options.detachedMass === undefined) ? (opts.initialMass * 0.1) : Number(options.detachedMass);

  // basic validation
  if (!opts || Number(opts.initialMass) <= 0 || Number(opts.targetDeltaV) <= 0) return { separated: false, reason: 'invalid_plan_opts' };

  const plan = planMultiSegmentBurn(opts);
  if (!plan || !plan.possible) return { separated: false, reason: 'no_feasible_plan', plan };

  if (onlyIfEven && (plan.segmentsCount % 2 !== 0)) {
    return { separated: false, reason: 'segments_not_even', segmentsCount: plan.segmentsCount };
  }

  // Simplified kinematics: final velocity (stack) = targetDeltaV (m/s). Start v=0.
  const finalVelocity = Number(opts.targetDeltaV);
  const driftDistance = finalVelocity * driftSeconds; // meters

  // Separated stage receives optional small separation delta-v
  const separatedStageVelocity = finalVelocity + separationDeltaV;

  const summary = {
    driftSeconds,
    driftDistance,
    finalVelocity,
    separatedStage: {
      mass: detachedMass,
      velocity: separatedStageVelocity,
      position: driftDistance
    },
    remainingStage: {
      mass: opts.initialMass - detachedMass,
      velocity: finalVelocity,
      position: driftDistance
    }
  };

  const timeSeries = [
    { t: 0, stackVelocity: 0, stackPosition: 0 },
    { t: driftSeconds, stackVelocity: finalVelocity, stackPosition: driftDistance, separatedStageVelocity, separatedStagePosition: driftDistance }
  ];

  const result = { separated: true, planSummary: plan.totals || null, summary, timeSeries };

  // optional notification (captain job) - POST JSON to notifyWebhook
  if (options.notifyWebhook) {
    // validate URL
    try {
      const u = new URL(options.notifyWebhook);
      if (!/^https?:$/.test(u.protocol)) {
        result.notifyResult = { ok: false, error: 'unsupported_protocol' };
        return result;
      }
    } catch (e) {
      result.notifyResult = { ok: false, error: 'invalid_url' };
      return result;
    }

    // fire-and-forget, but return result (attempt)
    return fetch(options.notifyWebhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'separation', summary })
    }).then(resp => resp.text().then(body => ({ ok: resp.ok, status: resp.status, body }))).then(nres => Object.assign(result, { notifyResult: nres })).catch(err => Object.assign(result, { notifyResult: { ok: false, error: String(err) } }));
  }

  return Promise.resolve(result);
}

module.exports = { separateAfterDrift };
