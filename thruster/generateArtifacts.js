#!/usr/bin/env node
// generateArtifacts.js
// Generate thruster artifacts: status snapshot, optionally converted SVGs, and package them

const fs = require('fs');
const path = require('path');
const os = require('os');
const { promisify } = require('util');
const exec = promisify(require('child_process').exec);
const archiver = require('archiver');

const { combustionStatus, isGitAvailable } = require('./combustion');
const { convertSvgToPng } = require('./publishGraph');
const { saveToPath } = require('./saveToD');

async function makeDir(dir) {
    await fs.promises.mkdir(dir, { recursive: true });
}

function timestamp() {
    return new Date().toISOString().replace(/[:.]/g, '-');
}

async function packageDir(sourceDir, outPath) {
    return new Promise((resolve, reject) => {
        const output = fs.createWriteStream(outPath);
        const archive = archiver('zip', { zlib: { level: 9 } });
        output.on('close', () => resolve(outPath));
        archive.on('error', (err) => reject(err));
        archive.pipe(output);
        archive.directory(sourceDir, false);
        archive.finalize();
    });
}

async function run() {
    const base = path.join(process.cwd(), 'build', 'thruster-artifacts');
    const runId = `run-${timestamp()}`;
    const outDir = path.join(base, runId);
    await makeDir(outDir);

    // 1) Collect git status or fallback
    const statusFile = path.join(outDir, 'status.txt');
    try {
        const status = await combustionStatus();
        await fs.promises.writeFile(statusFile, `git available: ${isGitAvailable()}\n\n${status}`, 'utf8');
    } catch (e) {
        await fs.promises.writeFile(statusFile, `Combustion status failed: ${e.message}`, 'utf8');
    }

    // 2) Convert example SVG if present
    const exampleSvg = path.join('api', 'maven-mvnd-1.0.3', 'src', 'main', 'images', 'mvnd-logo.svg');
    if (fs.existsSync(exampleSvg)) {
        const pngOut = path.join(outDir, 'mvnd-logo.png');
        try {
            await convertSvgToPng(exampleSvg, pngOut, { width: 512, height: 512 });
        } catch (e) {
            // fallback: copy source svg
            await fs.promises.copyFile(exampleSvg, path.join(outDir, 'mvnd-logo.svg'));
            await fs.promises.writeFile(path.join(outDir, 'convert-failure.txt'), `SVG conversion failed: ${e.message}`, 'utf8');
        }
    }

    // 3) Save a copy to THRUSTER_SAVE_DIR if configured
    const saveDirName = process.env.THRUSTER_SAVE_DIR ? process.env.THRUSTER_SAVE_DIR : path.join(os.homedir(), 'thruster-artifacts');
    try {
        await saveToPath(saveDirName, `${runId}.txt`, `Artifacts produced at ${new Date().toISOString()}\nPath: ${outDir}`);
    } catch (e) {
        // non-fatal
    }

    // 4) Package artifacts into zip
    const zipPath = path.join(base, `${runId}.zip`);
    await packageDir(outDir, zipPath);

    console.log('Artifacts created:', outDir);
    console.log('Packaged:', zipPath);
    return { outDir, zipPath };
}

if (require.main === module) {
    (async () => {
        try {
            const res = await run();
            console.log('Done:', res);
            process.exit(0);
        } catch (err) {
            console.error('Error generating artifacts:', err);
            process.exit(1);
        }
    })();
}

module.exports = { run };
