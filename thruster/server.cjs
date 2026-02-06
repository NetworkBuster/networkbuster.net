// thruster/server.cjs
// Simple Express API to request thruster plans (simulation-only)

const express = require('express');
const bodyParser = require('body-parser');
const rateLimit = require('express-rate-limit');
const { planBurn, planMultiSegmentBurn, planOptimizedMultiSegment, planOptimizedMultiSegmentHeuristic, planOptimizedMultiSegmentContinuous } = require('./thrusterPhysics.cjs');
const { buildProfileSVGString } = require('./visualizeBurn.cjs');
const { convertSvgStringToPngBuffer } = require('./publishGraph.cjs');

const app = express();
app.use(bodyParser.json());

// basic rate limiting for safety: 30 requests per minute per IP
const limiter = rateLimit({ windowMs: 60 * 1000, max: 30 });
app.use(limiter);

app.get('/health', (req, res) => res.json({ ok: true }));

// Query parameters or JSON body supported
// Optional API key enforcement: set THRUSTER_API_KEY env var to enable
function requireApiKey(req, res, next) {
  const key = process.env.THRUSTER_API_KEY;
  if (!key) return next();
  const got = req.headers['x-api-key'] || req.query['api_key'] || req.body && req.body.api_key;
  if (!got || String(got) !== String(key)) return res.status(401).json({ ok: false, error: 'invalid_api_key' });
  return next();
}

function validatePlanOptions(opts) {
  const required = ['initialMass', 'propellantAvailable', 'isp', 'maxG', 'targetDeltaV'];
  for (const r of required) {
    if (opts[r] === undefined || opts[r] === null || Number.isNaN(Number(opts[r]))) return { valid: false, error: `missing_or_invalid_${r}` };
  }
  if (Number(opts.initialMass) <= 0) return { valid: false, error: 'initialMass_must_be_positive' };
  if (Number(opts.propellantAvailable) < 0) return { valid: false, error: 'propellantAvailable_must_be_nonnegative' };
  if (Number(opts.isp) <= 0) return { valid: false, error: 'isp_must_be_positive' };
  if (Number(opts.maxG) <= 0) return { valid: false, error: 'maxG_must_be_positive' };
  return { valid: true };
}

app.post('/plan', requireApiKey, (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
  const v = validatePlanOptions(opts);
  if (!v.valid) return res.status(400).json({ ok: false, error: v.error });
  try {
    const single = planBurn(opts);
    const multi = planMultiSegmentBurn(opts);
    res.json({ ok: true, single, multi });
  } catch (err) {
    res.status(400).json({ ok: false, error: err.message });
  }
});

app.get('/plan', (req, res) => {
  const opts = parseNumericOptions(req.query);
  try {
    const single = planBurn(opts);
    const multi = planMultiSegmentBurn(opts);
    res.json({ ok: true, single, multi });
  } catch (err) {
    res.status(400).json({ ok: false, error: err.message });
  }
});

// Visualize endpoint: returns SVG or PNG (in-memory, no temp files)
app.post('/plan/visualize', requireApiKey, async (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
  const v = validatePlanOptions(opts);
  if (!v.valid) return res.status(400).json({ ok: false, error: v.error });
  const format = (req.query.format || req.body.format || 'svg').toLowerCase();
  const title = req.body.title || req.query.title || 'Burn Profile';
  try {
    const svg = buildProfileSVGString(opts, title);
    if (format === 'png') {
      const buf = await convertSvgStringToPngBuffer(svg, { width: opts.width, height: opts.height }).catch(() => null);
      if (buf) {
        res.set('Content-Type', 'image/png');
        return res.send(buf);
      }
      // fallback to svg
    }
    res.set('Content-Type', 'image/svg+xml');
    res.send(svg);
  } catch (err) {
    res.status(400).json({ ok: false, error: err.message });
  }
});

// Orbit visualization endpoint
app.post('/visualize/orbit', requireApiKey, async (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
  // lightweight validation for orbit params
  if (!opts.radius || !opts.period) {
    return res.status(400).json({ ok: false, error: 'missing_or_invalid_radius_or_period' });
  }
  const format = (req.query.format || req.body.format || 'svg').toLowerCase();
  try {
    const { generateOrbitSVG, svgToPngBuffer } = require('./visualizeOrbit.cjs');
    const svg = generateOrbitSVG(opts);
    if (format === 'png') {
      const buf = await svgToPngBuffer(opts).catch(() => null);
      if (buf) {
        res.set('Content-Type', 'image/png');
        return res.send(buf);
      }
    }
    res.set('Content-Type', 'image/svg+xml');
    res.send(svg);
  } catch (err) {
    res.status(400).json({ ok: false, error: err.message });
  }
});

// Optimize variable-segment deltaV per cost. Accepts cost='min_propellant'|'min_time'|'min_peakG' and method='grid'|'heuristic'|'continuous'
app.post('/plan/optimize', requireApiKey, (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
  const v = validatePlanOptions(opts);
  if (!v.valid) return res.status(400).json({ ok: false, error: v.error });
  const cost = (req.body.cost || req.query.cost || 'min_peakG');
  const method = (req.body.method || req.query.method || 'grid');
  try {
    let optimized = null;
    if (method === 'heuristic') {
      optimized = planOptimizedMultiSegmentHeuristic(opts, { cost, steps: Number(req.body.steps || req.query.steps || 12), iterations: Number(req.body.iterations || req.query.iterations || 2000) });
    } else if (method === 'continuous') {
      optimized = planOptimizedMultiSegmentContinuous(opts, { cost, maxIter: Number(req.body.maxIter || req.query.maxIter || 400) });
    } else {
      optimized = planOptimizedMultiSegment(opts, { cost, steps: Number(req.body.steps || req.query.steps || 6) });
    }
    res.json({ ok: true, optimized, method });
  } catch (err) {
    res.status(400).json({ ok: false, error: err.message });
  }
});

// Separation endpoint: simulate separation after drift and optionally notify an operations specialist (webhook)
const { separateAfterDrift } = require('./separation.cjs');
const admin = require('./admin.cjs');

app.post('/plan/separate', requireApiKey, async (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
  const body = Object.assign({}, req.body || {}, req.query || {});
  // driftSeconds required
  const driftSeconds = Number(body.driftSeconds || body.drift_seconds || body.drift || 0);
  if (!driftSeconds || driftSeconds <= 0) return res.status(400).json({ ok: false, error: 'missing_or_invalid_driftSeconds' });
  const onlyIfEven = (body.onlyIfEven === undefined) ? true : (String(body.onlyIfEven) === 'true');
  const separationDeltaV = Number(body.separationDeltaV || body.separation_delta_v || 0);
  const detachedMass = body.detachedMass !== undefined ? Number(body.detachedMass) : undefined;
  const notifyWebhook = body.notifyWebhook || body.notify_webhook || body.notify || null;

  const v = validatePlanOptions(opts);
  if (!v.valid) return res.status(400).json({ ok: false, error: v.error });

  try {
    const result = await separateAfterDrift(opts, { driftSeconds, onlyIfEven, separationDeltaV, detachedMass, notifyWebhook });
    res.json(Object.assign({ ok: true }, result));
  } catch (err) {
    res.status(500).json({ ok: false, error: String(err) });
  }
});

// Admin access request endpoints
function requireAdminKey(req, res, next) {
  const key = process.env.THRUSTER_ADMIN_KEY;
  if (!key) return res.status(403).json({ ok: false, error: 'admin_key_not_configured' });
  const got = req.headers['x-admin-key'] || req.query['admin_key'] || req.body && req.body.admin_key;
  if (!got || String(got) !== String(key)) return res.status(401).json({ ok: false, error: 'invalid_admin_key' });
  return next();
}

// Request access (anyone can request)
app.post('/admin/request-access', (req, res) => {
  try {
    const body = Object.assign({}, req.body || {}, req.query || {});
    if (!body.githubUser || !body.publicKey) return res.status(400).json({ ok: false, error: 'githubUser_and_publicKey_required' });
    const r = admin.requestAccess({ githubUser: String(body.githubUser), publicKey: String(body.publicKey), reason: body.reason, contact: body.contact });
    res.json({ ok: true, request: r });
  } catch (err) {
    res.status(400).json({ ok: false, error: String(err) });
  }
});

// Approve access (admin only): generates safe script to run on server as root and marks request approved
app.post('/admin/approve', requireAdminKey, (req, res) => {
  try {
    const body = Object.assign({}, req.body || {}, req.query || {});
    if (!body.id) return res.status(400).json({ ok: false, error: 'id_required' });
    const r = admin.approveRequest(String(body.id), req.headers['x-admin-user'] || 'web-admin');
    if (!r.ok) return res.status(400).json({ ok: false, error: r.error });
    res.json({ ok: true, scriptPath: r.scriptPath });
  } catch (err) {
    res.status(500).json({ ok: false, error: String(err) });
  }
});

// List requests (admin only)
app.get('/admin/requests', requireAdminKey, (req, res) => {
  try {
    res.json({ ok: true, requests: admin.listRequests() });
  } catch (err) {
    res.status(500).json({ ok: false, error: String(err) });
  }
});

// Helper: parse numeric options from query/body
function parseNumericOptions(obj) {
  const n = {};
  for (const k in obj) {
    if (!Object.prototype.hasOwnProperty.call(obj, k)) continue;
    const v = obj[k];
    if (v === undefined || v === null) continue;
    const num = Number(v);
    n[k] = ('' + v).trim() !== '' && !Number.isNaN(num) ? num : v;
  }
  return n;
}

if (require.main === module) {
  const port = process.env.THRUSTER_PORT || 3800;
  app.listen(port, () => console.log(`Thruster planner API listening on ${port}`));
}

module.exports = app;}