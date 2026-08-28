#!/usr/bin/env node
/**
 * Build-time helper: convert public/og/att-default.svg → PNG and PNG variants.
 * Run via `npm run og:build`. Not part of the production deps tree.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Resvg } from '@resvg/resvg-js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ogDir = path.resolve(__dirname, '..', 'public', 'og');
const svgPath = path.join(ogDir, 'att-default.svg');
const svgText = fs.readFileSync(svgPath, 'utf8');

function writePng(target, width, height) {
  const resvg = new Resvg(svgText, {
    fitTo: { mode: 'width', value: width },
    background: '#07090d',
    font: { loadSystemFonts: true },
  });
  const png = resvg.render().asPng();
  fs.writeFileSync(path.join(ogDir, target), png);
  console.log(`[og] wrote ${target} (${(png.length / 1024).toFixed(1)} KB)`);
}

writePng('att-default.png', 1200);
fs.mkdirSync(path.join(ogDir, 'twitter'), { recursive: true });
writePng('twitter/att-default.png', 1200);
