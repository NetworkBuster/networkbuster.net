// thruster/visualizeBurn.cjs
// Generate a simple SVG burn profile (thrust, acceleration, mass vs time)

const fs = require("fs");
const path = require("path");
const { convertSvgToPng } = require("./publishGraph.cjs");
const { planBurn } = require("./thrusterPhysics.cjs");
const g0 = 9.80665;

function buildProfileData(opts) {
  // opts: initialMass, isp, maxThrust, maxG, targetDeltaV, propellantAvailable, preferredThrust
  const plan = planBurn(opts);
  if (!plan.possible)
    throw new Error(`Plan not possible: ${plan.reason || "unknown"}`);

  const mdot = plan.thrust / (opts.isp * g0);
  const duration = plan.burnTimeSeconds;
  const steps = Math.max(10, Math.ceil(duration / 0.5)); // step ~0.5s or less
  const dt = duration / steps;

  const times = [];
  const thrust = [];
  const mass = [];
  const accel = [];

  for (let i = 0; i <= steps; i++) {
    const t = Math.min(i * dt, duration);
    const m = Math.max(0, opts.initialMass - mdot * t);
    const a = plan.thrust / (m * g0); // in Gs
    times.push(t);
    thrust.push(plan.thrust);
    mass.push(m);
    accel.push(a);
  }

  return { plan, times, thrust, mass, accel, duration };
}

function _scale(arr, min, max) {
  const aMin = Math.min(...arr);
  const aMax = Math.max(...arr);
  if (aMax - aMin < 1e-12) return arr.map(() => (min + max) / 2);
  return arr.map((v) => min + ((v - aMin) / (aMax - aMin)) * (max - min));
}

function generateSVG(profile, title = "Burn Profile", opts = {}) {
  const width = opts.width || 800;
  const height = opts.height || 420;
  const margin = { top: 40, right: 80, bottom: 40, left: 60 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;

  const times = profile.times;
  const xs = times.map((t) => margin.left + (t / profile.duration) * plotW);

  // scale thrust and accel separately to same plot height
  const thrustScaled = _scale(profile.thrust, margin.top + plotH, margin.top);
  const accelScaled = _scale(profile.accel, margin.top + plotH, margin.top);
  const massScaled = _scale(profile.mass, margin.top + plotH, margin.top);

  function polylineFrom(xs, ys) {
    return xs.map((x, i) => `${x.toFixed(2)},${ys[i].toFixed(2)}`).join(" ");
  }

  const thrustPoints = polylineFrom(xs, thrustScaled);
  const accelPoints = polylineFrom(xs, accelScaled);
  const massPoints = polylineFrom(xs, massScaled);

  // Build axes labels
  const maxT = profile.duration.toFixed(1);

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${title}">
  <style>
    .axis { stroke: #333; stroke-width: 1; }
    .grid { stroke: #ddd; stroke-width: 1; }
    .thrust { fill:none; stroke: #d9534f; stroke-width: 2; }
    .accel { fill:none; stroke: #5bc0de; stroke-width: 2; stroke-dasharray: 4 2; }
    .mass { fill:none; stroke: #5cb85c; stroke-width: 2; stroke-dasharray: 2 2; }
    .legend { font-family: sans-serif; font-size: 12px; }
    .title { font-family: sans-serif; font-size: 14px; font-weight: bold; }
    .label { font-family: sans-serif; font-size: 11px; fill: #333 }
  </style>
  <rect x="0" y="0" width="${width}" height="${height}" fill="#fff" />
  <text x="${margin.left}" y="${margin.top - 12}" class="title">${title}</text>
  <!-- grid lines -->
  ${[0, 0.25, 0.5, 0.75, 1]
    .map((f) => {
      const y = margin.top + f * plotH;
      return `<line class="grid" x1="${margin.left}" y1="${y}" x2="${margin.left + plotW}" y2="${y}"/>`;
    })
    .join("\n  ")}

  <!-- axes -->
  <line class="axis" x1="${margin.left}" y1="${margin.top + plotH}" x2="${margin.left + plotW}" y2="${margin.top + plotH}"/>
  <line class="axis" x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${margin.top + plotH}"/>

  <!-- plots -->
  <polyline class="thrust" points="${thrustPoints}" />
  <polyline class="accel" points="${accelPoints}" />
  <polyline class="mass" points="${massPoints}" />

  <!-- legend -->
  <g transform="translate(${margin.left + plotW + 10}, ${margin.top})" class="legend">
    <g><rect width="12" height="8" fill="#d9534f"></rect><text x="18" y="8">Thrust (N)</text></g>
    <g transform="translate(0,18)"><rect width="12" height="8" fill="#5bc0de"></rect><text x="18" y="8">Acceleration (g)</text></g>
    <g transform="translate(0,36)"><rect width="12" height="8" fill="#5cb85c"></rect><text x="18" y="8">Mass (kg)</text></g>
  </g>

  <!-- x-axis labels -->
  <text x="${margin.left}" y="${margin.top + plotH + 22}" class="label">0s</text>
  <text x="${margin.left + plotW}" y="${margin.top + plotH + 22}" class="label" text-anchor="end">${maxT}s</text>

</svg>`;

  return svg;
}

async function saveBurnProfileSVG(opts, outSvgPath, title) {
  const profile = buildProfileData(opts);
  const svg = generateSVG(profile, title, opts);
  await fs.promises.mkdir(path.dirname(outSvgPath), { recursive: true });
  await fs.promises.writeFile(outSvgPath, svg, "utf8");
  return outSvgPath;
}

async function renderBurnProfilePNG(opts, outSvgPath, outPngPath, title) {
  const svgPath = await saveBurnProfileSVG(opts, outSvgPath, title);
  // convert to PNG
  try {
    const out = await convertSvgToPng(svgPath, outPngPath, {
      width: opts.width || 800,
      height: opts.height || 420,
    });
    return out;
  } catch (e) {
    // conversion failed
    return null;
  }
}

// Exported helper to build profile and return inline SVG string (no disk writes)
function buildProfileSVGString(opts, title = "Burn Profile", svgOpts = {}) {
  const profile = buildProfileData(opts);
  return generateSVG(profile, title, svgOpts);
}

module.exports = {
  buildProfileData,
  generateSVG,
  saveBurnProfileSVG,
  renderBurnProfilePNG,
  buildProfileSVGString,
};

// CLI
if (require.main === module) {
  (async () => {
    try {
      const argv = process.argv.slice(2);
      // Usage: node visualizeBurn.cjs <outSvg> [outPng]
      const outSvg = argv[0] || "build/thruster-artifacts/burn-profile.svg";
      const outPng = argv[1] || "build/thruster-artifacts/burn-profile.png";

      // Example plan options
      const opts = {
        initialMass: 1000,
        propellantAvailable: 200,
        isp: 300,
        maxThrust: 20000,
        maxG: 3,
        targetDeltaV: 100,
      };

      await saveBurnProfileSVG(opts, outSvg, "Example Burn Profile");
      console.log("Saved SVG to", outSvg);
      try {
        await renderBurnProfilePNG(opts, outSvg, outPng);
        console.log("Saved PNG to", outPng);
      } catch (e) {
        console.warn("PNG conversion failed:", e.message);
      }
    } catch (err) {
      console.error(err);
      process.exit(1);
    }
  })();
}

module.exports = {
  buildProfileData,
  generateSVG,
  saveBurnProfileSVG,
  renderBurnProfilePNG,
  buildProfileSVGString,
};
