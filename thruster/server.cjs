// thruster/server.cjs
// Simple Express API to request thruster plans (simulation-only)

const express = require('express');
const bodyParser = require('body-parser');
const { planBurn, planMultiSegmentBurn } = require('./thrusterPhysics.cjs');

const app = express();
app.use(bodyParser.json());

app.get('/health', (req, res) => res.json({ ok: true }));

// Query parameters or JSON body supported
app.post('/plan', (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
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
app.post('/plan/visualize', async (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
  const format = (req.query.format || req.body.format || 'svg').toLowerCase();
  const title = req.body.title || req.query.title || 'Burn Profile';
  try {
    const svg = buildProfileSVGString(opts, title);
    if (format === 'png') {
      const buf = await require('./visualizeBurn.cjs').renderBurnProfilePNG(opts, null, null, title)
        .then(() => convertSvgStringToPngBuffer(svg, { width: opts.width, height: opts.height }))
        .catch(() => null);
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
app.post('/visualize/orbit', async (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
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

// Optimize variable-segment deltaV per cost. Accepts cost='min_propellant'|'min_time'|'min_peakG'
app.post('/plan/optimize', (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
  const cost = (req.body.cost || req.query.cost || 'min_peakG');
  try {
    const optimized = planOptimizedMultiSegment(opts, { cost });
    res.json({ ok: true, optimized });
  } catch (err) {
    res.status(400).json({ ok: false, error: err.message });
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