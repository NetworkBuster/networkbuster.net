// Simple unit test for thruster/combustion.cjs
const assert = require("assert");
const {
  isGitAvailable,
  combustionStatus,
} = require("../../thruster/combustion");

async function runTests() {
  console.log("Running thruster combustion tests (CJS)...");
  const gitAvail = isGitAvailable();
  assert.strictEqual(
    typeof gitAvail,
    "boolean",
    "isGitAvailable should be boolean",
  );

  const status = await combustionStatus();
  assert.ok(
    typeof status === "string",
    "combustionStatus should return a string",
  );

  console.log("All thruster tests passed (CJS)");
}

runTests().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});
