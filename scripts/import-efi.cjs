#!/usr/bin/env node
/*
  Simple import scaffold for EFI online/base files.
  Supports: --source, --base, --file, --dry-run, --verbose
*/
const fs = require('fs');
const path = require('path');
const os = require('os');

function parseArgs() {
  // Minimal built-in argument parser to avoid external deps
  const args = process.argv.slice(2);
  const opts = { source: 'online', base: 'base', file: undefined, dryRun: true, verbose: false };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--source' && args[i + 1]) {
      opts.source = args[++i];
    } else if (a === '--base' && args[i + 1]) {
      opts.base = args[++i];
    } else if ((a === '--file' || a === '-f') && args[i + 1]) {
      opts.file = args[++i];
    } else if (a === '--dry-run') {
      opts.dryRun = true;
    } else if (a === '--no-dry-run') {
      opts.dryRun = false;
    } else if (a === '--verbose' || a === '-v') {
      opts.verbose = true;
    } else if (a === '--help' || a === '-h') {
      console.log('Usage: node scripts/import-efi.cjs --source [online|local] --base [base] [--file path] [--dry-run] [--verbose]');
      process.exit(0);
    }
  }
  return opts;
}

async function main() {
  const opts = parseArgs();
  const { source, base, file, dryRun, verbose } = opts;

  console.log(`Import script: source=${source}, base=${base}, file=${file || '(none)'}, dryRun=${dryRun}`);

  // Simulate discovery
  const discovered = [];
  if (file) {
    if (!fs.existsSync(file)) {
      console.error(`File not found: ${file}`);
      process.exit(2);
    }
    discovered.push({ type: 'local-file', path: path.resolve(file) });
  } else if (source === 'local') {
    // look under data/efi or efi/
    const candidates = [path.join(process.cwd(), 'data', 'efi'), path.join(process.cwd(), 'efi')];
    for (const c of candidates) {
      if (fs.existsSync(c)) {
        const files = fs.readdirSync(c).filter(n => n && !n.startsWith('.'));
        files.forEach(f => discovered.push({ type: 'local-dir', dir: c, file: f }));
      }
    }
    if (discovered.length === 0) {
      if (verbose) console.log('No local EFI files discovered in data/efi or efi/');
    }
  } else if (source === 'online') {
    // In dry-run we won't fetch anything; show what would happen.
    discovered.push({ type: 'online-source', url: `https://example.com/efi/${base}` });
  } else {
    console.error('Unknown source:', source);
    process.exit(2);
  }

  // Report discovered
  console.log('\nDiscovered items to import:');
  if (discovered.length === 0) console.log('  (none)');
  discovered.forEach((d, i) => console.log(`  ${i + 1}. ${JSON.stringify(d)}`));

  // Plan actions
  const actions = [];
  for (const d of discovered) {
    if (d.type === 'local-file' || d.type === 'local-dir') {
      actions.push({ action: 'copy', src: d.path || path.join(d.dir, d.file), dest: path.join('data', 'efi', d.file || path.basename(d.path)) });
    } else if (d.type === 'online-source') {
      actions.push({ action: 'fetch', url: d.url, dest: path.join('data', 'efi', `${base}.json`) });
    }
  }

  console.log('\nPlanned actions:');
  if (actions.length === 0) console.log('  (nothing to do)');
  actions.forEach((a, i) => console.log(`  ${i + 1}. ${JSON.stringify(a)}`));

  if (dryRun) {
    console.log('\nDry-run enabled: no files will be written.');
    process.exit(0);
  }

  // Execute actions (not used in dry-run)
  try {
    if (!fs.existsSync(path.join(process.cwd(), 'data'))) fs.mkdirSync(path.join(process.cwd(), 'data'));
    if (!fs.existsSync(path.join(process.cwd(), 'data', 'efi'))) fs.mkdirSync(path.join(process.cwd(), 'data', 'efi'));

    for (const a of actions) {
      if (a.action === 'copy') {
        const src = a.src;
        const dest = path.join(process.cwd(), a.dest);
        fs.copyFileSync(src, dest);
        if (verbose) console.log(`Copied ${src} -> ${dest}`);
      } else if (a.action === 'fetch') {
        // naive fetch – only when not dry-run
        const fetch = require('node-fetch');
        const res = await fetch(a.url);
        if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
        const body = await res.text();
        fs.writeFileSync(path.join(process.cwd(), a.dest), body, 'utf8');
        if (verbose) console.log(`Fetched ${a.url} -> ${a.dest}`);
      }
    }
    console.log('\nImport complete.');
    process.exit(0);
  } catch (err) {
    console.error('Import failed:', String(err));
    process.exit(3);
  }
}

main();
