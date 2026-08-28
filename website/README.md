# Austin Trading Team · website

The public-facing website for **Austin Trading Team (ATT)** and the **Austin Trading Engine (ATE)**, built as a static export and deployed to GitHub Pages.

The site consumes every value it shows from the upstream ATT-Trading-Framework repository (canonical content layer: `src/data/content.ts`, plus live markdown fetched at build time from `../docs`, `../specifications`, `../research/Reports/RDR`, and release manifests). **Nothing is invented** — if the website shows a number, an engine status, an RDR classification, or a SHA-256, that string comes from the framework repo.

If you want to add a fact to the site, edit the repo first, then refresh this snapshot. See "Content integration" below.

---

## Stack

| Layer            | Tool                                              |
| ---------------- | ------------------------------------------------- |
| Site framework   | Astro v7 (static export, `output: 'static'`)      |
| Content rendering| Markdown rendered at build time, hand-rolled subset (headings, lists, paragraphs, code fences, tables) inside the docs page. No external renderer at runtime. |
| Styling          | Hand-written CSS with design tokens (`src/styles/global.css`). No Tailwind, no runtime CSS framework. |
| Type             | TypeScript strict (Astro check, `tsconfig.json`)  |
| Diagrams         | Inline SVG (architecture diagram)                  |
| Sitemap          | `@astrojs/sitemap`                                 |
| OG image         | Generated at build time from `public/og/att-default.svg` via `@resvg/resvg-js`  |
| Hosting          | GitHub Pages (free tier)                           |

No client-side framework, no heavy JS bundles. The site ships ~870 KB of static HTML + ~30 KB of JS for nav-toggle, IntersectionObserver fade-ins, and the research-centre filter.

---

## Quick start (one-minute)

Requires Node 22+ (matches CI).

```bash
cd website
npm install
npm run dev          # http://127.0.0.1:4321
```

A live build of the parent framework repo is NOT required for `dev`. It IS required for `build` because the docs page imports live markdown files (the build reads from `../docs/`, etc. via the `ATT_REPO_PATH` env var). The default repo path is the one cloned next to this folder.

---

## Commands

```bash
# Always
npm run dev          # Astro dev server (http://127.0.0.1:4321)
npm run build        # Build static site + OG image → ./dist
npm run preview      # Serve ./dist locally

# Verification
npm run check        # astro check (TypeScript + Astro diagnostics)
npm run lint         # alias for `astro check`
npm test             # verifies build works end-to-end (npm test and npm run test:build)
npm run sync:content # Emits src/data/sync-meta.json with the live RDR inventory
npm run og:build     # only regenerates the OG PNG (rare — usually automated)
```

---

## Build

```bash
npm run build
```

`build` runs `scripts/build-og.mjs` (PNG rasterisation of the OG SVG) then `astro build`. Output is written to `dist/`. Each route is generated as `dist/<route>/index.html` for clean GitHub Pages hosting.

The Astro sitemap integration also emits `dist/sitemap-index.xml` and `dist/sitemap-0.xml`.

### Serving locally

```bash
npm run preview
# OR, for a vanilla static server (matches GitHub Pages behaviour):
python3 -m http.server 8089 --directory dist
```

---

## Project layout

```
website/
├── astro.config.mjs              # Astro config (static export + sitemap)
├── tsconfig.json                 # TS strict, ~/ alias → src/
├── package.json
├── public/                       # Copied verbatim to dist/ at build time
│   ├── favicon.svg
│   ├── robots.txt
│   └── og/
│       ├── att-default.svg       # Generated → att-default.png via resvg
│       └── att-default.png       # Built artefact (rebuilt on every build)
├── scripts/
│   ├── sync-content.mjs          # Re-emits src/data/sync-meta.json from the repo
│   └── build-og.mjs              # Rasterises the OG SVG → PNG
├── src/
│   ├── data/
│   │   ├── content.ts            # ⭐ Canonical content snapshot for the site
│   │   └── sync-meta.json        # Build-time-only record (gitignored)
│   ├── layouts/
│   │   └── Base.astro            # <head>, header, footer, JSON-LD
│   ├── components/
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   ├── Pill.astro
│   │   ├── SectionHeader.astro
│   │   ├── EngineCard.astro
│   │   ├── RDRCard.astro
│   │   ├── BacktestCard.astro
│   │   ├── ArchitectureDiagram.astro
│   │   ├── DashboardMock.astro   # ← ILLUSTRATIVE — clearly labelled as such
│   │   └── Ticker.astro          # ← ILLUSTRATIVE — clearly labelled as such
│   ├── pages/
│   │   ├── index.astro           # Home
│   │   ├── engine.astro          # What ATE is
│   │   ├── engines.astro         # Engine Explorer
│   │   ├── release/
│   │   │   └── v2-2.astro        # ATE v2.2 release page
│   │   ├── research.astro        # RDR centre (filterable)
│   │   ├── validation.astro     # Verifier + classification
│   │   ├── backtests.astro      # Hermes artefacts
│   │   ├── architecture.astro    # Engine map, contracts, constraints
│   │   ├── methodology.astro    # Hypothesis → promotion
│   │   ├── docs.astro            # Live MD render of repo docs
│   │   ├── roadmap.astro         # 5 tracks of work
│   │   ├── changelog.astro       # Highlight timeline
│   │   ├── about.astro
│   │   └── 404.astro
│   ├── styles/global.css
│   └── env.d.ts
└── .github/README.md             # CI/CD notes (workflow lives at repo root)
```

---

## Content integration

The site has **one** source of structured truth: `src/data/content.ts`. Every
piece of data on the site (engine status, RDR inventory, release SHA, roadmap
phases, changelog highlights) lives there. The values are sourced from the
upstream repo, never invented.

### To refresh from the upstream repo

1. Make sure the parent `ATT-Trading-Framework/` repo is at the HEAD you want
   to publish. `cd .. && git pull` if needed.

2. Manually update the affected entries in `src/data/content.ts`. Each block in
   the file is preceded by a comment listing the source paths and the build
   commands that emit the equivalent JSON.

3. For RDRs, run:

   ```bash
   npm run sync:content
   ```

   This emits `src/data/sync-meta.json` with the live RDR inventory — useful
   to spot RDRs that have appeared in the repo but haven't been wired into
   `content.ts` yet. The site does not auto-import this JSON; it is a build-time
   reconciliation aid.

4. Verify there are no authoring gaps by rebuilding and spot-checking. The
   build runs Astro's strict type-checker.

### Live markdown

The `/docs` page reads markdown files from the parent repo at **build time**
using `node:fs`. To add a new document to that page, add an entry to the
`DOCS[]` array in `src/data/content.ts`. If the file no longer exists at
`docs/<path>` at build time, the page renders a "Read on GitHub" fallback.

### What we don't ship

- No client-side API calls to GitHub. Repo metadata is hard-coded in
  `src/data/content.ts` to keep the site build-static.
- No fake performance numbers, no fake win-rates, no fake P&L. Every numerical
  claim is sourced from `tools/scripts/verify_ate.py` output or from an RDR.

---

## Deployment

GitHub Pages via a dedicated workflow at
`/Users/paul/Code/repos/development-att-framework/ATT-Trading-Framework/.github/workflows/website.yml`.

### First-time setup on a fresh repo

1. **Repository settings → Pages → Build and deployment → Source:**
   set to **GitHub Actions**.
2. Ensure the workflow file exists at the repo root (it does; see
   `website/.github/README.md` for the runtime contract).
3. Push to `main`. The `Website / Build` job runs, type-checks, builds, and the
   `Website / Deploy` job then publishes to the Pages URL.

The `deploy` job only runs on `push` to `main` (PRs build but don't deploy).

### Expected runtime

- Install: ~25 s
- Type-check: ~12 s
- Build: ~5 s (Astro is fast for static export)
- Deploy: ~10 s

### Custom domain

Add the `cname:` argument to the `actions/deploy-pages` step and configure the
custom domain in repo Settings → Pages. We do not require a paid domain name
for the site to work.

---

## Local development tips

- **Editing content.** Every change is in `src/data/content.ts`. The site hot-reloads on save.
- **Adding a page.** Drop a `.astro` file in `src/pages/`. It will be picked up by `astro build` and added to `sitemap-0.xml` automatically. Add a link in the Header's `NAV` array.
- **Adding a component.** Put a `.astro` file in `src/components/`. Astro scoped styles by default — keep component styles alongside markup with `<style>` blocks.
- **Re-running the OG image.** `npm run og:build` (or just `npm run build`).
- **Testing the docs page locally.** Make sure the parent repo is present
  (`../docs/`, `../specifications/`). If you have it elsewhere, set the
  environment variable:

  ```bash
  ATT_REPO_PATH=/path/to/ATT-Trading-Framework npm run dev
  ```

---

## Accessibility & SEO

- Semantic HTML throughout (`<header>`, `<main>`, `<footer>`, `<nav>`, `<article>`, `<section>`).
- `aria-label` on icon-only buttons and diagrams.
- `prefers-reduced-motion` is respected (animations and the ticker pause).
- WCAG-conscious colour contrast for text on the dark theme (gold accent is
  reserved for highlights and CTAs; body copy uses `--ink-1` on `--bg-0`).
- Per-page `<title>` and `<meta name="description">`.
- OpenGraph + Twitter card meta tags.
- JSON-LD for `Organization` and `SoftwareSourceCode`.
- Sitemap at `/sitemap-index.xml` (generated by `@astrojs/sitemap`).
- `robots.txt` allows all routes.
- Skip link: focus jumps to `<main>` on Tab from the address bar.

---

## Trading boundaries (the ones we explicitly preserve)

The site must not represent the framework as anything it isn't. We never claim:

- autonomous trading
- order routing or execution
- broker connectivity
- `riskApproved` publication
- DecisionEngine activation
- profitability or returns

The RiskEngine dashboard preview on `/release/v2-2` and on the homepage is
clearly labelled "Illustrative preview · values shown are diagnostic-concept
demonstrations, not real market data". The ticker tape is purely decorative.

---

## Dependencies

Production (`dependencies`):

- `astro` — static site generator
- `@astrojs/sitemap` — sitemap generation
- `@astrojs/check` — type-checker
- `@astrojs/mdx` — markdown support (unused by core pages, retained for blog-style expansions)
- `@astrojs/rss` — RSS (placeholder, optional)
- `@resvg/resvg-js` — SVG → PNG for the OG image (build only)
- `gray-matter`, `marked`, `rehype-slug`, `rehype-autolink-headings`, `shiki` — retained for future use
- `typescript` — strict TS

No frameworks on the client side; no React/Vue/Svelte.

---

## License

MIT — see the parent repo's `LICENSE`.
