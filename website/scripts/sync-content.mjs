#!/usr/bin/env node
/**
 * Content sync util — re-reads the upstream ATT-Trading-Framework
 * repository at build time and emits `src/data/sync-meta.json`.
 *
 * The website renders from an in-repo content snapshot in
 * `src/data/content.ts`. Run this script before publishing if you
 * want the RDR inventory to reflect the current HEAD of the framework
 * repo. Use ATT_REPO_PATH=... to override the repo root.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.resolve(__dirname, '..');
const DEFAULT_REPO = '/Users/paul/Code/repos/development-att-framework/ATT-Trading-Framework';
const REPO = process.env.ATT_REPO_PATH ?? DEFAULT_REPO;

if (!fs.existsSync(REPO)) {
  console.warn(`[sync] repo not found at ${REPO}. Skipping sync.`);
  process.exit(0);
}

const read = (rel) => fs.readFileSync(path.join(REPO, rel), 'utf8');

const rdrFiles = fs
  .readdirSync(path.join(REPO, 'research/Reports/RDR'))
  .filter((f) => f.endsWith('.md') && !f.includes('Spec') && !f.startsWith('.'));

const rdrs = rdrFiles.map((file) => {
  const text = read(`research/Reports/RDR/${file}`);
  const id =
    text.match(/^# (RDR-\d+\w?)/m)?.[1] ??
    file.split('-')[0].toUpperCase();
  const title =
    text.match(/^# RDR-\w+:?\s+(.+)$/m)?.[1]?.trim() ?? file;
  const date = text.match(/Date:\s*(\d{4}-\d{2}-\d{2})/)?.[1] ?? '';
  const engine =
    text.match(/Engine\**\s*[:|]\s*([A-Za-z]+Engine)/)?.[1] ??
    text.match(/(\w+Engine) diagnostic validation/i)?.[1] ??
    '—';
  const classification =
    text.match(/Research Classification:\**\s*(.*)$/im)?.[1]?.trim() ?? '—';
  return { file, id, title, date, engine, classification };
});

const manifest = {
  rdrs: rdrs.length,
  lastSync: new Date().toISOString(),
  repoPath: REPO,
  files: rdrs,
};

const out = path.join(webRoot, 'src', 'data', 'sync-meta.json');
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify(manifest, null, 2));

console.log(`[sync] captured ${rdrs.length} RDRs at ${manifest.lastSync}`);
for (const r of rdrs) {
  console.log(`  ${r.id} · ${r.engine} · ${r.classification}`);
}
