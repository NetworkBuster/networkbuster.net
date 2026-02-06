// thruster/visualizeOrbit.cjs
// Generate an SVG of a biosphere (planet) and an orbital trail with release marker.

const fs = require("fs");
const path = require("path");
const { convertSvgStringToPngBuffer } = require("./publishGraph.cjs");

function generateOrbitSVG(opts = {}) {
  // options: radius (planet radius px), width, height, trailAngle (deg), releaseAngle, color palette
  const width = opts.width || 800;
  const height = opts.height || 600;
  const cx = width / 2;
  const cy = height / 2 + 40;
  const planetR = opts.radius || Math.min(width, height) * 0.18; // biosphere radius
  const orbitR = Math.min(width, height) / 2 - 40;
  const trailAngle = (opts.trailAngle || -40) * (Math.PI / 180);
  const releaseAngle = (opts.releaseAngle || -10) * (Math.PI / 180);

  // compute points on orbit
  const orbitX = (x) => cx + orbitR * Math.cos(x);
  const orbitY = (x) => cy + orbitR * Math.sin(x);

  // create a smooth trail path from release point outward
  const releaseX = orbitX(releaseAngle);
  const releaseY = orbitY(releaseAngle);
  const trailLen = opts.trailLen || 220;
  const trailEndX =
    releaseX + trailLen * Math.cos(releaseAngle - Math.PI / 2) * 0.2;
  const trailEndY =
    releaseY + trailLen * Math.sin(releaseAngle - Math.PI / 2) * 0.2 - 120;

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="Biosphere Orbit Visualization">
  <defs>
    <radialGradient id="atmo" cx="50%" cy="40%">
      <stop offset="0%" stop-color="#9be7ff" stop-opacity="0.9" />
      <stop offset="70%" stop-color="#7fd3ff" stop-opacity="0.4" />
      <stop offset="100%" stop-color="#2f9fff" stop-opacity="0.05" />
    </radialGradient>
    <filter id="grain"><feTurbulence baseFrequency="0.8" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>
  </defs>

  <!-- background -->
  <rect x="0" y="0" width="${width}" height="${height}" fill="#000011" />

  <!-- stars -->
  ${Array.from({ length: 60 })
    .map((_, i) => {
      const sx = Math.random() * width;
      const sy = Math.random() * height * 0.6;
      const r = Math.random() * 1.6;
      return `<circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="${r.toFixed(2)}" fill="#ffffff" opacity="${(0.2 + Math.random() * 0.8).toFixed(2)}"/>`;
    })
    .join("\n  ")}

  <!-- orbit -->
  <circle cx="${cx}" cy="${cy}" r="${orbitR}" fill="none" stroke="#88c0ff" stroke-opacity="0.25" stroke-width="2" stroke-dasharray="6 6" />

  <!-- biosphere / planet -->
  <circle cx="${cx}" cy="${cy}" r="${planetR}" fill="url(#atmo)" stroke="#5fb1ff" stroke-width="2" />
  <g transform="translate(${cx - planetR * 0.6}, ${cy - planetR * 0.4}) scale(${planetR / 200})">
    <!-- simple land/sea shapes (decorative) -->
    <path d="M20,100 C40,40 140,40 160,100 C180,160 100,160 80,100 C60,40 20,60 20,100 Z" fill="#2a8e4c" opacity="0.9"/>
    <path d="M100,20 C140,40 180,60 160,120 C140,180 100,140 100,100 C100,80 80,40 100,20 Z" fill="#2a8e4c" opacity="0.6"/>
  </g>

  <!-- release marker on orbit -->
  <g transform="translate(${releaseX}, ${releaseY})">
    <circle r="6" fill="#ffcc00" stroke="#fff" stroke-width="1"/>
    <text x="12" y="4" font-size="12" fill="#fff">Release</text>
  </g>

  <!-- trail path -->
  <path d="M ${releaseX.toFixed(2)} ${releaseY.toFixed(2)} C ${((releaseX + trailEndX) / 2).toFixed(2)} ${((releaseY + trailEndY) / 2 - 60).toFixed(2)}, ${trailEndX.toFixed(2)} ${trailEndY.toFixed(2)}, ${trailEndX.toFixed(2)} ${trailEndY.toFixed(2)}" fill="none" stroke="#ff8a00" stroke-width="3" stroke-linecap="round" stroke-opacity="0.95"/>

  <!-- small spacecraft icon at trail end -->
  <g transform="translate(${trailEndX}, ${trailEndY}) scale(0.6)">
    <path d="M-8,10 L0,-12 L8,10 L0,6 Z" fill="#ffffff" stroke="#222" stroke-width="0.5" />
  </g>

  <!-- caption -->
  <text x="20" y="${height - 20}" fill="#ddd" font-size="12">Biosphere & release trail visualization</text>
</svg>`;

  return svg;
}

async function saveOrbitSVG(opts, outPath) {
  const svg = generateOrbitSVG(opts);
  await fs.promises.mkdir(path.dirname(outPath), { recursive: true });
  await fs.promises.writeFile(outPath, svg, "utf8");
  return outPath;
}

async function svgToPngBuffer(opts) {
  const svg = generateOrbitSVG(opts);
  return await convertSvgStringToPngBuffer(svg, {
    width: opts.width,
    height: opts.height,
  });
}

module.exports = { generateOrbitSVG, saveOrbitSVG, svgToPngBuffer };
