// Renders PNGs for the UnboundFS brand concepts with headless Chromium.
// Usage: node render.mjs jobs.json
// Each job: { "svg": "<path to .svg>", "out": "<png>", "w": 1024, "h": 1024 }
//       or: { "html": "<path to .html>", "out": "<png>", "w": 2000, "h": 1200, "fullPage": true }
// SVG jobs are rasterised at exactly w x h pixels with a transparent background.
import { readFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const jobs = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const browser = await chromium.launch();
const page = await browser.newPage({ deviceScaleFactor: 1 });

for (const job of jobs) {
  mkdirSync(dirname(job.out), { recursive: true });
  await page.setViewportSize({ width: job.w, height: job.h });
  if (job.svg) {
    const svg = readFileSync(job.svg, 'utf8');
    await page.setContent(
      `<!doctype html><html><head><style>html,body{margin:0;padding:0;background:transparent;overflow:hidden}` +
      `svg{display:block;width:${job.w}px;height:${job.h}px}</style></head><body>${svg}</body></html>`);
    await page.screenshot({ path: job.out, omitBackground: true, clip: { x: 0, y: 0, width: job.w, height: job.h } });
  } else {
    await page.goto('file://' + resolve(job.html));
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: job.out, fullPage: !!job.fullPage, omitBackground: !!job.transparent });
  }
  process.stdout.write('.');
}
await browser.close();
console.log(`\nrendered ${jobs.length} images`);
