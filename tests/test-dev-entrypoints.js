import assert from 'assert';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), '..');

function waitForOutput(child, scriptName, readyPattern) {
  return new Promise((resolve, reject) => {
    let output = '';
    const timeout = setTimeout(() => {
      child.kill('SIGINT');
      reject(new Error(`${scriptName} did not become ready.\n${output}`));
    }, 30000);

    const onData = (chunk) => {
      output += chunk.toString();
      if (readyPattern.test(output)) {
        clearTimeout(timeout);
        resolve(output);
      }
    };

    child.stdout.on('data', onData);
    child.stderr.on('data', onData);

    child.on('exit', (code, signal) => {
      if (readyPattern.test(output)) {
        return;
      }

      clearTimeout(timeout);
      reject(new Error(`${scriptName} exited before ready (code=${code}, signal=${signal}).\n${output}`));
    });
  });
}

function waitForExit(child, scriptName) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      if (process.platform === 'win32') {
        child.kill('SIGKILL');
      } else {
        process.kill(-child.pid, 'SIGKILL');
      }
      reject(new Error(`${scriptName} did not exit after SIGINT`));
    }, 15000);

    child.on('exit', (code, signal) => {
      clearTimeout(timeout);
      if (code === 0 || signal === 'SIGINT') {
        resolve();
        return;
      }

      reject(new Error(`${scriptName} exited unexpectedly (code=${code}, signal=${signal})`));
    });
  });
}

async function assertEntrypointStarts(scriptName, readyPattern) {
  const child = spawn(process.execPath, [scriptName], {
    cwd: repoRoot,
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: process.platform !== 'win32'
  });

  const output = await waitForOutput(child, scriptName, readyPattern);
  assert.doesNotMatch(output, /require is not defined in ES module scope/);
  if (process.platform === 'win32') {
    child.kill('SIGINT');
  } else {
    process.kill(-child.pid, 'SIGINT');
  }
  await waitForExit(child, scriptName);
}

async function run() {
  await assertEntrypointStarts('dev-server.js', /(Local:\s+http:\/\/localhost:5173|ready in \d+ ms|Starting Vite frontend development server)/);
  await assertEntrypointStarts('start-server.js', /(✅ Backend running on http:\/\/localhost:8080|API running at http:\/\/localhost:8080|Server running at http:\/\/localhost:8080)/);
  console.log('✓ Development entrypoints start without ESM import failures.');
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
