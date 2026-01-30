#!/usr/bin/env node
// Render all SVGs in docs/diagrams to PNG using Puppeteer
// Usage: node scripts/render-svgs.js [scale]
import fs from 'fs/promises';
import path from 'path';
import puppeteer from 'puppeteer';

const scale = Number(process.argv[2] || 2);
const dir = path.resolve('docs', 'diagrams');

async function renderFile(file) {
  const svgPath = path.join(dir, file);
  const pngPath = path.join(dir, file.replace(/\.svg$/i, '.png'));
  const svg = await fs.readFile(svgPath, 'utf8');
  // Attempt to extract width/height from viewBox or attributes
  let width = 800, height = 600;
  const vb = svg.match(/viewBox=["']?([0-9\.\s]+)["']?/i);
  if (vb) {
    const parts = vb[1].trim().split(/\s+/).map(Number);
    if (parts.length === 4) { width = parts[2]; height = parts[3]; }
  } else {
    const w = svg.match(/width=["']?([0-9\.]+)["']?/i);
    const h = svg.match(/height=["']?([0-9\.]+)["']?/i);
    if (w) width = Math.round(Number(w[1]));
    if (h) height = Math.round(Number(h[1]));
  }

  const html = `<!doctype html><html><meta charset="utf8"><style>body{margin:0;padding:0;background:transparent}</style><body>${svg}</body></html>`;
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: Math.ceil(width), height: Math.ceil(height), deviceScaleFactor: scale });
  await page.setContent(html, { waitUntil: 'networkidle0' });
  const el = await page.$('svg');
  if (!el) {
    console.warn(`No <svg> found in ${file}`);
    await browser.close();
    return;
  }
  await el.screenshot({ path: pngPath, omitBackground: true });
  console.log(`Rendered ${pngPath}`);
  await browser.close();
}

async function main(){
  try {
    const files = await fs.readdir(dir);
    const svgs = files.filter(f => f.toLowerCase().endsWith('.svg'));
    if (!svgs.length) { console.log('No SVG files to render in', dir); return }
    for (const f of svgs) {
      await renderFile(f);
    }
  } catch (err) {
    console.error('Render error', err);
    process.exit(1);
  }
}

main();
