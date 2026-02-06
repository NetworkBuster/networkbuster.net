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

// Visualize endpoint: returns SVG or PNG
app.post('/plan/visualize', async (req, res) => {
  const opts = parseNumericOptions(req.body || req.query);
  const format = (req.query.format || req.body.format || 'svg').toLowerCase();
  const title = req.body.title || req.query.title || 'Burn Profile';
  try {
    const outDir = 'build/thruster-artifacts';
    const svgPath = `${outDir}/burn-${Date.now()}.svg`;
    const pngPath = `${outDir}/burn-${Date.now()}.png`;
    await saveBurnProfileSVG(opts, svgPath, title);
    if (format === 'png') {
      const png = await renderBurnProfilePNG(opts, svgPath, pngPath, title);
      if (png) {
        const data = await fs.promises.readFile(png);
        res.set('Content-Type', 'image/png');
        return res.send(data);
      }
      // fallback to svg
    }
    const svg = await fs.promises.readFile(svgPath, 'utf8');
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