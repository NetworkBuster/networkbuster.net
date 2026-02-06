const fs = require("fs");
const path = require("path");
const fetch = require("node-fetch");
const child = require("child_process");

// start server in background
const server = child.spawn(
  process.execPath,
  [require.resolve("../../thruster/server.cjs")],
  { stdio: "inherit", detached: true },
);

function wait(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

(async () => {
  try {
    // wait for server
    await wait(1200);
    const url = "http://localhost:3800/plan/visualize";
    const body = {
      initialMass: 1000,
      propellantAvailable: 500,
      isp: 300,
      maxThrust: 15000,
      maxG: 3,
      targetDeltaV: 200,
      format: "png",
    };
    const res = await fetch(url, {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) {
      console.error("server responded", res.status, await res.text());
      process.exit(2);
    }
    const buf = await res.buffer();
    const out = path.resolve(__dirname, "..", "output", "visualization.png");
    fs.writeFileSync(out, buf);
    console.log("wrote", out);
    process.exit(0);
  } catch (err) {
    console.error(err);
    process.exit(2);
  }
})();
