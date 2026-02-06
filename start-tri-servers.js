#!/usr/bin/env node
/**
 * NetworkBuster Tri-Server Audio System
 * Starts all three servers for dual/tri setup:
 * - Main Web Server (port 3000)
 * - API Server (port 3001)
 * - Audio Streaming Server (port 3002)
 */

import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const servers = [
  {
    name: "Main Web Server",
    file: "server-universal.js",
    port: 3000,
    icon: "🌐",
  },
  {
    name: "API Server",
    file: "api/server-universal.js",
    port: 3001,
    icon: "⚙️",
  },
  {
    name: "Audio Streaming Server",
    file: "server-audio.js",
    port: 3002,
    icon: "🎵",
  },
];

const processes = [];

console.log("\n╔════════════════════════════════════════════════════════════╗");
console.log("║     NetworkBuster Tri-Server Audio System                   ║");
console.log("║     Starting all three servers...                            ║");
console.log("╚════════════════════════════════════════════════════════════╝\n");

servers.forEach((server, index) => {
  setTimeout(() => {
    const child = spawn("node", [path.join(__dirname, server.file)], {
      cwd: __dirname,
      stdio: "inherit",
      env: {
        ...process.env,
        AUDIO_PORT: server.port,
      },
    });

    processes.push(child);

    console.log(`${server.icon} ${server.name} (PID: ${child.pid})`);

    child.on("error", (err) => {
      console.error(`✗ ${server.name} error:`, err.message);
    });

    child.on("exit", (code) => {
      console.log(`✗ ${server.name} exited with code ${code}`);
    });
  }, index * 1000);
});

console.log(`\n✅ All servers starting...\n`);
console.log(`🌐  Main Web:     http://localhost:3000`);
console.log(`⚙️   API Server:   http://localhost:3001/api/health`);
console.log(`🎵  Audio Lab:    http://localhost:3002/audio-lab\n`);

// Graceful shutdown
process.on("SIGINT", () => {
  console.log("\n\nShutting down all servers...");
  processes.forEach((proc) => {
    proc.kill("SIGTERM");
  });
  setTimeout(() => {
    process.exit(0);
  }, 2000);
});

process.on("SIGTERM", () => {
  console.log("Terminating all servers...");
  processes.forEach((proc) => {
    proc.kill("SIGTERM");
  });
  process.exit(0);
});
