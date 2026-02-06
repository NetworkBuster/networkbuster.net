#!/usr/bin/env node

/**
 * NetworkBuster Build & Power Pipeline
 * Trigger: Option 2 after build 1, then Option 4 after build 3
 */

import { spawn, execSync } from "child_process";
import fs from "fs";
import path from "path";

const PROJECT_PATH = "C:\\Users\\daypi\\OneDrive\\Desktop\\networkbuster.net";

class BuildPipeline {
  constructor() {
    this.builds = [
      {
        num: 1,
        name: "Web Server Build",
        cmd: "node",
        args: ["server-universal.js"],
      },
      {
        num: 2,
        name: "API Server Build",
        cmd: "node",
        args: ["api/server-universal.js"],
      },
      {
        num: 3,
        name: "Audio Server Build",
        cmd: "node",
        args: ["server-audio.js"],
      },
      {
        num: 4,
        name: "Auth Server Build",
        cmd: "node",
        args: ["auth-ui/v750/server.js"],
      },
    ];

    this.currentBuild = 0;
    this.buildLog = [];
  }

  log(msg) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${msg}`;
    console.log(logEntry);
    this.buildLog.push(logEntry);
  }

  async runBuild(buildNum) {
    const build = this.builds[buildNum - 1];
    if (!build) {
      this.log(`❌ Build ${buildNum} not found`);
      return false;
    }

    this.log(`\n${"═".repeat(60)}`);
    this.log(`🔨 Starting Build ${buildNum}: ${build.name}`);
    this.log(`${"═".repeat(60)}`);

    return new Promise((resolve) => {
      const proc = spawn(build.cmd, build.args, {
        cwd: PROJECT_PATH,
        stdio: "inherit",
      });

      proc.on("close", (code) => {
        if (code === 0) {
          this.log(`✅ Build ${buildNum} successful`);
          resolve(true);
        } else {
          this.log(`❌ Build ${buildNum} failed with code ${code}`);
          resolve(false);
        }
      });

      proc.on("error", (err) => {
        this.log(`❌ Build ${buildNum} error: ${err.message}`);
        resolve(false);
      });
    });
  }

  async triggerPowerOption(option) {
    this.log(`\n${"═".repeat(60)}`);
    this.log(`⚡ Triggering Power Option ${option}`);
    this.log(`${"═".repeat(60)}`);

    return new Promise((resolve) => {
      const proc = spawn("node", ["power-manager.js", option.toString()], {
        cwd: PROJECT_PATH,
        stdio: "inherit",
      });

      proc.on("close", (code) => {
        if (code === 0) {
          this.log(`✅ Power Option ${option} triggered successfully`);
          resolve(true);
        } else {
          this.log(`⚠️ Power Option ${option} returned code ${code}`);
          resolve(true); // Continue anyway
        }
      });

      proc.on("error", (err) => {
        this.log(`⚠️ Power Option ${option} error: ${err.message}`);
        resolve(true); // Continue anyway
      });
    });
  }

  displayMenu() {
    console.log(`
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster Build & Power Pipeline                      ║
║  Options:                                                  ║
║  1. Run full pipeline (Builds 1-4 + Power Options)        ║
║  2. Run builds only                                        ║
║  3. Run power management only                              ║
║  4. Check server status                                    ║
╚════════════════════════════════════════════════════════════╝
`);
  }

  async runFullPipeline() {
    this.log("🚀 Starting full build & power pipeline...\n");

    // Build 1 → Option 2
    const build1 = await this.runBuild(1);
    if (build1) {
      await this.triggerPowerOption(2);
    }

    // Builds 2 & 3
    const build2 = await this.runBuild(2);
    const build3 = await this.runBuild(3);

    // After Build 3 → Option 4
    if (build3) {
      await this.triggerPowerOption(4);
    }

    // Build 4
    await this.runBuild(4);

    this.log(`\n${"═".repeat(60)}`);
    this.log("✅ Pipeline complete!");
    this.log(`${"═".repeat(60)}\n`);

    this.saveBuildLog();
  }

  async runBuildsOnly() {
    this.log("🏗️ Running builds only...\n");

    for (let i = 1; i <= 4; i++) {
      const success = await this.runBuild(i);
      if (!success) {
        this.log(`⚠️ Build ${i} failed, continuing...`);
      }
      // Small delay between builds
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    this.saveBuildLog();
  }

  async runPowerManagementOnly() {
    this.log("⚡ Running power management only...\n");

    this.log("Option 2: Boot Command Injection");
    await this.triggerPowerOption(2);

    this.log("\nOption 4: Server Power Management");
    await this.triggerPowerOption(4);

    this.saveBuildLog();
  }

  checkServerStatus() {
    this.log("\n📊 Checking server status...\n");

    const servers = [
      { port: 3000, name: "Web Server" },
      { port: 3001, name: "API Server" },
      { port: 3002, name: "Audio Server" },
      { port: 3003, name: "Auth Server" },
    ];

    servers.forEach((server) => {
      try {
        const response = execSync(
          `curl -s http://localhost:${server.port}/api/health`,
          {
            encoding: "utf8",
            timeout: 2000,
          },
        );
        const health = JSON.parse(response);
        console.log(`✅ ${server.name} (${server.port}): RUNNING`);
      } catch (err) {
        console.log(`❌ ${server.name} (${server.port}): NOT RUNNING`);
      }
    });
  }

  saveBuildLog() {
    const logPath = path.join(PROJECT_PATH, ".build-pipeline.log");
    fs.writeFileSync(logPath, this.buildLog.join("\n"));
    this.log(`\n📝 Build log saved: ${logPath}`);
  }

  async execute(option = 1) {
    switch (option) {
      case 1:
        await this.runFullPipeline();
        break;
      case 2:
        await this.runBuildsOnly();
        break;
      case 3:
        await this.runPowerManagementOnly();
        break;
      case 4:
        this.checkServerStatus();
        break;
      default:
        this.displayMenu();
    }
  }
}

// Parse command line arguments
const option = parseInt(process.argv[2]) || 1;
const pipeline = new BuildPipeline();

pipeline.execute(option).catch((err) => {
  console.error("Pipeline error:", err);
  process.exit(1);
});
