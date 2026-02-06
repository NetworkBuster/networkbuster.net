// Unit test for orbit SVG generation
const assert = require("assert");
const { generateOrbitSVG } = require("../../thruster/visualizeOrbit.cjs");

async function test() {
  console.log("Running orbit visualization unit test...");
  const svg = generateOrbitSVG({ width: 600, height: 400, releaseAngle: -30 });
  assert.ok(
    svg && svg.startsWith("<?xml"),
    "SVG should be generated and be XML",
  );
  assert.ok(svg.includes("Biosphere"), "SVG should include caption");
  assert.ok(
    svg.includes("<circle"),
    "SVG should have circles for planet/stars",
  );
  console.log("Orbit visualization unit test passed.");
}

test().catch((err) => {
  console.error(err);
  process.exit(1);
});
