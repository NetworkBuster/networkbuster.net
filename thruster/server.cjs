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
  const opts = req.body || req.query;
  try {
    const single = planBurn(opts);
    const multi = planMultiSegmentBurn(opts);
    res.json({ ok: true, single, multi });
  } catch (err) {
    res.status(400).json({ ok: false, error: err.message });
  }
});

app.get('/plan', (req, res) => {
  const opts = req.query;
  try {
    const single = planBurn(opts);
    const multi = planMultiSegmentBurn(opts);
    res.json({ ok: true, single, multi });
  } catch (err) {
    res.status(400).json({ ok: false, error: err.message });
  }
});

if (require.main === module) {
  const port = process.env.THRUSTER_PORT || 3800;
  app.listen(port, () => console.log(`Thruster planner API listening on ${port}`));
}

module.exports = app;}