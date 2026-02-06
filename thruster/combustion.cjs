// thruster/combustion backend feature (CJS)
// This module provides combustion logic for the thruster backend with lightweight
// cross-platform compatibility and optional fallback when git isn't available.

const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");

function isGitAvailable() {
  try {
    const which = process.platform === "win32" ? "where" : "which";
    const out = require("child_process")
      .execSync(`${which} git`, { stdio: "pipe" })
      .toString();
    return Boolean(out && out.trim());
  } catch (e) {
    return false;
  }
}

function runGitCommand(command) {
  return new Promise((resolve, reject) => {
    if (!isGitAvailable()) {
      return reject(new Error("git is not available on PATH"));
    }
    exec(`git ${command}`, { cwd: process.cwd() }, (error, stdout, stderr) => {
      if (error) {
        reject(stderr || error.message);
      } else {
        resolve(stdout);
      }
    });
  });
}

async function combustionStatus() {
  if (isGitAvailable()) {
    return await runGitCommand("status --porcelain");
  }
  const fallback = path.join(process.cwd(), ".git-status");
  try {
    return await fs.promises.readFile(fallback, "utf8");
  } catch (e) {
    return "git not available and no fallback .git-status file present";
  }
}

module.exports = {
  runGitCommand,
  combustionStatus,
  isGitAvailable,
};
