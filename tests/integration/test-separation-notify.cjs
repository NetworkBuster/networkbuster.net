const http = require("http");
const child = require("child_process");
const fetch = require("node-fetch");
const path = require("path");
const fs = require("fs");

async function startCaptureServer(port = 49211) {
  let last = null;
  const server = http.createServer((req, res) => {
    if (req.method === "POST") {
      let body = "";
      req.on("data", (c) => (body += c.toString()));
      req.on("end", () => {
        try {
          last = JSON.parse(body);
        } catch (e) {
          last = body;
        }
        res.writeHead(200, { "Content-Type": "text/plain" });
        res.end("ok");
      });
    } else {
      res.writeHead(200);
      res.end("ok");
    }
  });
  await new Promise((r) => server.listen(port, r));
  return {
    server,
    port,
    getLast: () => last,
    close: () => new Promise((r) => server.close(r)),
  };
}

(async () => {
  const capture = await startCaptureServer(49211);

  // start thruster server
  const server = child.spawn(
    process.execPath,
    [require.resolve("../../thruster/server.cjs")],
    { detached: true, stdio: "inherit" },
  );

  function wait(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }
  await wait(1200);

  try {
    const url = "http://localhost:3800/plan/separate";
    const body = {
      initialMass: 1000,
      propellantAvailable: 600,
      isp: 300,
      maxThrust: 20000,
      maxG: 5,
      targetDeltaV: 100,
      driftSeconds: 2,
      onlyIfEven: false,
      notifyWebhook: "http://localhost:49211/",
      format: "json",
    };

    const res = await fetch(url, {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    });
    const json = await res.json();
    if (!json.ok) {
      console.error("server error", json);
      process.exit(2);
    }

    // wait for notification
    await wait(300);
    const rec = capture.getLast();
    if (!rec || rec.action !== "separation") {
      console.error("no notify received", rec);
      process.exit(2);
    }

    const out = path.resolve(
      __dirname,
      "..",
      "output",
      "separation-notify.json",
    );
    fs.writeFileSync(out, JSON.stringify(rec, null, 2));
    console.log("wrote", out);

    await capture.close();
    process.kill(-server.pid);
    process.exit(0);
  } catch (err) {
    console.error(err);
    await capture.close();
    process.kill(-server.pid);
    process.exit(2);
  }
})();
