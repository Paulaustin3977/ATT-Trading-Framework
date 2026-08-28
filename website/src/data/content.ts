/**
 * Authoritative content store for the ATT website.
 *
 * Every value here is sourced from the actual repo, not invented.
 * When the repo changes, refresh these files alongside the build.
 *
 * Cross-checked against:
 *   - README.md (current status table)
 *   - docs/Architecture.md
 *   - docs/Project_Charter.md
 *   - docs/releases/ATE_v2.2_Release_Manifest.md
 *   - ROADMAP.md
 *   - CHANGELOG.md
 */

export const SITE = {
  organisation: 'Austin Trading Team',
  organisationAbbr: 'ATT',
  product: 'Austin Trading Engine',
  productAbbr: 'ATE',
  tagline: 'Evidence-Based Market Intelligence',
  subtitle:
    'A modular, explainable, evidence-based market diagnostics and research framework.',
  description:
    'Austin Trading Engine (ATE) is a research-grade market diagnostics framework: spec-driven, immutable-released, RDR-validated, and TradingView-native.',
  // Public canonical origin. The base path is set via astro.config.mjs
  // (`base: '/ATT-Trading-Framework'`). When a custom domain is added,
  // update `site` here AND drop the `base` field in astro.config.mjs.
  url: 'https://paulaustin3977.github.io',
  github: 'https://github.com/Paulaustin3977/ATT-Trading-Framework',
  license: 'MIT',
  copyright: '© 2026 Austin Trading Team',
} as const;

/** Risk disclaimer shown in the footer. */
export const DISCLAIMER = {
  intro:
    'The Austin Trading Engine (ATE) is a market-diagnostics and research framework. Nothing on this site constitutes financial advice, an investment recommendation, or a solicitation to trade any instrument.',
  bullets: [
    'All content, documentation, and validation reports are for research and educational purposes only.',
    'ATE does not place orders, route trades, manage positions, or connect to brokers.',
    'Past diagnostic performance does not guarantee future diagnostic behaviour or any trading outcome.',
    'Trading carries risk of loss; consult a regulated adviser before any decision.',
  ],
};

/** Per the README status table — non-negotiable source of truth. */
export interface Engine {
  id: string;
  name: string;
  concern: string;
  versionLabel: string;          // e.g. "1.0.0-draft" or "—"
  implemented: boolean;
  implementedWhere: string;       // path
  verified: boolean;
  verifiedNote: string;
  validated: null | {
    rdr: string;
    classification: 'Supported' | 'Weakly Supported' | 'Mixed' | 'Unsupported' | 'Pending';
    cadence: string;
  };
  approvedScope: string;
  status:
    | 'Production Baseline'
    | 'Implemented (Diagnostic-Only)'
    | 'Implemented (Release)'
    | 'Implemented (Development Mirror)'
    | 'Development Mirror (Research-Only)'
    | 'Deferred'
    | 'Presentation-Only';
  bullets: string[];
}

export const ENGINES: Engine[] = [
  {
    id: 'trend',
    name: 'TrendEngine',
    concern: 'Direction and persistence of the prevailing move',
    versionLabel: '— (release) / 0.2.0-spec-impl (development)',
    implemented: true,
    implementedWhere: 'pine/releases/ATE_v2.2.pine (existing trend score) · pine/development/ATE_Current.pine (research mirror)',
    verified: true,
    verifiedNote: 'Release: covered by canonical verifier. Development mirror: contract + deterministic fixture checks.',
    validated: {
      rdr: 'RDR-010 (re-attempt)',
      classification: 'Mixed',
      cadence: 'Daily + Weekly',
    },
    approvedScope:
      'No downstream action authority. No TradingView compile claim is made for the development-only TrendEngine.',
    status: 'Production Baseline',
    bullets: [
      'Direction strength, persistence, and structure-relative regime read.',
      'Existing trend score implemented in the v2.2 release.',
      '0.2.0-spec-impl research mirror adds fixed-parameter diagnostics only in development.',
    ],
  },
  {
    id: 'structure',
    name: 'StructureEngine',
    concern: 'Market structure: highs, lows, breakouts, range behaviour',
    versionLabel: '—',
    implemented: true,
    implementedWhere: 'pine/releases/ATE_v2.2.pine',
    verified: true,
    verifiedNote: 'Covered by canonical release verification.',
    validated: null,
    approvedScope: 'No downstream action authority.',
    status: 'Implemented (Release)',
    bullets: [
      'Pivots, swing distances, break of structure (BOS).',
      'Preserved across the v2.2 release baseline.',
    ],
  },
  {
    id: 'momentum',
    name: 'MomentumEngine',
    concern: 'Rate of change and momentum characteristics',
    versionLabel: '—',
    implemented: true,
    implementedWhere: 'pine/releases/ATE_v2.2.pine',
    verified: true,
    verifiedNote: 'Covered by canonical release verification.',
    validated: null,
    approvedScope: 'No downstream action authority.',
    status: 'Implemented (Release)',
    bullets: [
      'Direction-aware momentum read used by confidence and risk.',
      'Helps distinguish persistent from failing moves.',
    ],
  },
  {
    id: 'volatility',
    name: 'VolatilityEngine',
    concern: 'Volatility regime and contraction/expansion cycles',
    versionLabel: '1.0.0-draft',
    implemented: true,
    implementedWhere: 'pine/releases/ATE_v2.2.pine (preserved from v2.1)',
    verified: true,
    verifiedNote: 'Release verification + 270/270 contract/behaviour checks (incl. RDR-002 verifier ad-hoc 43/43).',
    validated: {
      rdr: 'RDR-002 (daily) + RDR-002W (weekly)',
      classification: 'Weakly Supported',
      cadence: 'Daily + Weekly',
    },
    approvedScope:
      'Diagnostic display/research only; downstream integration not approved.',
    status: 'Implemented (Diagnostic-Only)',
    bullets: [
      'Compressed, normal, expanding, elevated, unstable, shock, unknown states.',
      'Diagnostic-only across v2.2 — no ConfidenceEngine or RiskEngine coupling.',
      'No reserved-language emissions (safe/unsafe/suitable/approved/blocked).',
    ],
  },
  {
    id: 'confidence',
    name: 'ConfidenceEngine',
    concern: 'Strength and agreement of the current market evidence',
    versionLabel: '—',
    implemented: true,
    implementedWhere: 'pine/releases/ATE_v2.2.pine',
    verified: true,
    verifiedNote: 'Covered by canonical release verification.',
    validated: null,
    approvedScope:
      'Uses only trend score, structure, and momentum in v2.2. No Volatility or Risk input.',
    status: 'Implemented (Release)',
    bullets: [
      'Confidence is evidence-strength — it does not create risk.',
      'Engine Output Contract: score / state / direction / reason / version.',
    ],
  },
  {
    id: 'risk',
    name: 'RiskEngine',
    concern: 'Safety, suitability, exposure, and protective adjustment',
    versionLabel: '1.0.0-draft',
    implemented: true,
    implementedWhere: 'pine/releases/ATE_v2.2.pine (diagnostic-only)',
    verified: true,
    verifiedNote:
      'Release verification covers diagnostic contracts; 442/442 verifier checks pass against v2.2 release SHA.',
    validated: {
      rdr: 'RDR-003 (daily) + RDR-003W (weekly)',
      classification: 'Weakly Supported',
      cadence: 'Daily + Weekly',
    },
    approvedScope:
      'Diagnostic display/research only; DecisionEngine and ConfidenceEngine integration remain deferred. Does not publish riskApproved.',
    status: 'Implemented (Diagnostic-Only)',
    bullets: [
      'Six states (calm, normal, elevated, tense, extreme, unknown); five directions (none, elevated, conflict, stable, indeterminate); never bullish or bearish.',
      'Four-component scoring: volatility 35 / extension 30 / structure 20 / conflict 15, clamped 0–100.',
      'No reserved language (safe / unsafe / suitable / approved / blocked) may appear in dashboard labels, Research Mode text, state values, direction values, or reason text.',
    ],
  },
  {
    id: 'dashboard',
    name: 'DashboardEngine',
    concern: 'Visual presentation and information density',
    versionLabel: '—',
    implemented: true,
    implementedWhere: 'pine/releases/ATE_v2.2.pine',
    verified: true,
    verifiedNote: 'Covered by canonical release verification.',
    validated: null,
    approvedScope:
      'Presentation only. Dashboard display transformations are clearly labelled as such; they never rewrite engine values.',
    status: 'Presentation-Only',
    bullets: [
      'Renders the engine state on TradingView and supports a Research Mode panel.',
      '10 preserved alertcondition titles (ATE v2.1 baseline maintained exactly).',
    ],
  },
  {
    id: 'decision',
    name: 'DecisionEngine',
    concern: 'Final actionable signal from confidence adjusted by risk',
    versionLabel: '—',
    implemented: false,
    implementedWhere: '—',
    verified: false,
    verifiedNote: 'Not implemented.',
    validated: null,
    approvedScope:
      'No DecisionEngine or action logic is implemented or active. Out of current research-only scope.',
    status: 'Deferred',
    bullets: [
      'Explicitly deferred per docs/Architecture.md and ROADMAP.md.',
      'No action authority, no `riskApproved` contract, no execution.',
    ],
  },
];

/** ATE release-line — preserve provenance. */
export const RELEASES = [
  {
    version: 'v2.2',
    name: 'Diagnostic RiskEngine release',
    type: 'Diagnostic',
    baseline: 'pine/releases/ATE_v2.2.pine',
    sha256: 'd55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239',
    manifest: 'docs/releases/ATE_v2.2_Release_Manifest.md',
    status: 'Compiles cleanly in TradingView',
    approval:
      'Approved only as the stored diagnostic rollback/release baseline by Paul Austin.',
    headline: 'RiskEngine v1.0.0-draft added as diagnostic-only. VolatilityEngine preserved. 10 alertconditions preserved exactly.',
    highlights: [
      'RiskEngine implemented as diagnostic-only — no ConfidenceEngine, DecisionEngine, entry/exit, position sizing, stop logic, or trade-action alert impact.',
      'VolatilityEngine v1.0.0-draft preserved from ATE v2.1 unchanged.',
      'All 10 existing ATE alertcondition calls preserved (Golden Cross, Death Cross, Strong Bull, Strong Bear, Bullish BOS, Bearish BOS, Momentum Bullish, Momentum Bearish, High Confidence Bull, Low Confidence Bear). No RiskEngine alerts added.',
      'Canonically verified: 442/442 contract & integrity checks.',
      'Dashboard display: YES · Research Mode output: YES · Confidence impact: NO · Decision impact: NO · Risk alerts: NO.',
    ],
  },
  {
    version: 'v2.1',
    name: 'Diagnostic VolatilityEngine release',
    type: 'Diagnostic',
    baseline: 'pine/releases/ATE_v2.1.pine',
    sha256: '7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893',
    manifest: 'docs/releases/ATE_v2.1_Release_Manifest.md',
    status: 'Preserved unchanged as rollback baseline',
    approval:
      'Approved as a stored diagnostic baseline. TradingView compile confirmed clean.',
    headline: 'VolatilityEngine v1.0.0-draft added as diagnostic-only. Existing engines preserved.',
    highlights: [
      'VolatilityEngine added to dashboard and Research Mode as diagnostic-only.',
      'No ConfidenceEngine, RiskEngine, or DecisionEngine coupling.',
      'First canonical EDR-001 verifier published against this baseline.',
    ],
  },
  {
    version: 'v2.0',
    name: 'Initial structured release',
    type: 'Diagnostic',
    baseline: 'pine/releases/ATE_v2.0.pine',
    sha256: null,
    manifest: 'docs/releases/',
    status: 'Earlier diagnostic release baseline',
    approval: 'Historical baseline.',
    headline: 'Predecessor release. Preserved for reference.',
    highlights: [],
  },
];

/** RDR (Research Decision Record) summary cards. */
export const RDRS = [
  {
    id: 'RDR-002',
    title: 'VolatilityEngine daily diagnostic validation',
    engine: 'VolatilityEngine',
    assetClass: 'Multi-asset (metals, equities, FX, bonds, commodities)',
    timeframe: 'Daily',
    cadence: '10y daily bars',
    assets: 14,
    date: '2026-07-03',
    classification: 'Weakly Supported',
    recommendation:
      'Keep Diagnostic; retest thresholds after more observation',
    file: 'research/Reports/RDR/RDR-002-volatility-diagnostic-validation.md',
    companion: 'RDR-002W',
    findings: [
      '14 assets passed the minimum-300-row daily filter.',
      'No hidden directional bias; state sequence reproducible.',
      'Reserved-language audit: 0 hits.',
    ],
    confidenceEngineIntegration: 'Deferred',
    riskEngineIntegration: 'Deferred',
  },
  {
    id: 'RDR-002W',
    title: 'VolatilityEngine weekly diagnostic validation',
    engine: 'VolatilityEngine',
    assetClass: 'Multi-asset (metals, equities, FX, bonds)',
    timeframe: 'Weekly',
    cadence: 'Weekly OHLC, 10y',
    assets: 15,
    date: '2026-07-03',
    classification: 'Weakly Supported',
    recommendation:
      'Keep Diagnostic; retest thresholds after more observation',
    file: 'research/Reports/RDR/RDR-002W-volatility-diagnostic-validation.md',
    companion: 'RDR-002',
    findings: [
      'Weekly states smoother than daily; abs momentum overlap ~2.6× daily but well under redundancy threshold.',
      'No hidden directional bias.',
    ],
    confidenceEngineIntegration: 'Deferred',
    riskEngineIntegration: 'Deferred',
  },
  {
    id: 'RDR-003',
    title: 'RiskEngine daily diagnostic validation',
    engine: 'RiskEngine',
    assetClass:
      'Metals (Gold, Silver, Copper), index proxies (Nasdaq, S&P 500), major equities, bonds/rates proxies, FX, commodities',
    timeframe: 'Daily',
    cadence: '34,436 daily bars · 2018-01-02 → 2026-07-03',
    assets: 16,
    date: '2026-07-04',
    classification: 'Weakly Supported',
    recommendation:
      'Keep Diagnostic; weekly RDR-003W and threshold review before any confidence-integration attempt',
    file: 'research/Reports/RDR/RDR-003-riskengine-daily-diagnostic-validation.md',
    companion: 'RDR-003W',
    findings: [
      'Median abs Spearman RiskScore vs VolScore: 0.17 (low, distinct from VolatilityEngine).',
      'Median vs Momentum: 0.31; vs Confidence: 0.43 (moderate, distinct).',
      'Median state_changes_per_100_bars: 9.89 — not noisy.',
      'Median max |pct_up − 50|: 4.5pp — low directional bias.',
      'Reserved-language audit: 0/432 hits.',
    ],
    negative: [
      'Distribution heavily calm-skewed (median pct_calm ~70%).',
      '`tense` / `extreme` evidence thin.',
      'Volatility component dominates >60% of bars in 6/16 assets (FX, TLT, IGLT.L, CL=F).',
    ],
    confidenceEngineIntegration: 'Deferred',
    riskEngineIntegration: 'Deferred',
  },
  {
    id: 'RDR-003W',
    title: 'RiskEngine weekly diagnostic validation',
    engine: 'RiskEngine',
    assetClass:
      'Same 16-asset universe as RDR-003 (Gold, Silver, Copper, Nasdaq, S&P 500, NVDA, MSFT, AAPL, AMZN, GOOGL, TLT, IGLT.L, EUR/USD, GBP/USD, USD/JPY, WTI crude)',
    timeframe: 'Weekly',
    cadence: '8,355 weekly bars · 2014-01-01 → 2026-07-03',
    assets: 16,
    date: '2026-07-04',
    classification: 'Supported',
    recommendation:
      'Keep Diagnostic; allow controlled weekly research use; DecisionEngine / ConfidenceEngine integration remains deferred',
    file: 'research/Reports/RDR/RDR-003W-riskengine-weekly-diagnostic-validation.md',
    companion: 'RDR-003',
    findings: [
      'All 9 weekly classification rules pass.',
      'Daily-vs-weekly state_changes_per_100_bars: 9.89 → 10.15 (stable).',
      'Volatility-component dominance: 51.29% → 48.08% (-3.2pp) on weekly aggregation.',
      'Assets with `dominant_vol_pct > 60`: 6 → 4 (clears 4-asset daily threshold).',
      'Median abs Spearman vs VolScore: 0.167 → 0.211; vs Momentum 0.309 → 0.258; vs Confidence 0.425 → 0.405.',
      'Median max |pct_up − 50|: 4.52pp → 7.48pp (small-sample weekly noise, both below 12pp threshold).',
      'Reserved-language audit: 0/418 hits.',
    ],
    negative: [
      'Distribution remains calm/normal-skewed (median pct_calm 68.0%).',
      '`tense` / `extreme` evidence thin on weekly bars.',
      'Hidden-bias median moves modestly upward 4.5pp → 7.5pp due to small `extreme`/`tense` weekly samples.',
    ],
    confidenceEngineIntegration: 'Deferred',
    riskEngineIntegration: 'Deferred',
  },
  {
    id: 'RDR-010',
    title: 'TrendEngine diagnostic validation — measurement re-attempt',
    engine: 'TrendEngine (development mirror)',
    assetClass: 'Gold (GC=F), Silver (SI=F), Gilts (IGLT.L)',
    timeframe: 'Daily + Weekly',
    cadence: 'Fixed-parameter deterministic harness, mirror of v2.2 inputs',
    assets: 3,
    date: '2026-07-25',
    classification: 'Mixed (instrument- and timeframe-dependent)',
    recommendation:
      'Retain as research-only diagnostic output. Do not couple to ConfidenceEngine, RiskEngine, DecisionEngine, alerts, or any trading/execution path.',
    file: 'research/Reports/RDR/RDR-010-trendengine-validation.md',
    companion: null,
    findings: [
      'Pooled daily hit rates 51.32% / 51.64% / 50.40% at 1/5/20 bars — but all three underperform the always-long no-TrendEngine benchmark on both hit rate and expectancy.',
      'Pooled weekly hit rates 52.97% / 54.79% / 62.66%; exceeds benchmark at 5 & 20 bars on hit rate; expectancy exceeds only at 20 bars.',
      'No TradingView compile claim is made for the development-only TrendEngine.',
    ],
    negative: [
      'Daily Gold positive at all horizons; daily Gilts negative at all horizons; daily Silver 20-bar hit rate < 50% despite positive arithmetic expectancy.',
      'State sequence almost never emits `RANGE` after warm-up (0.00%–0.77% daily; 0.00%–8.14% weekly) — material limitation.',
      'Volatility-slice and early/late results change materially (e.g. weekly IGLT.L early/late TVD 49.57%).',
    ],
    confidenceEngineIntegration: 'Deferred',
    riskEngineIntegration: 'Deferred',
  },
];

/** Verifier pre-flight results snapshot. */
export const VERIFIER = {
  command: 'python3 tools/scripts/verify_ate.py',
  totalChecks: 442,
  passed: 442,
  failed: 0,
  v22ReleaseShaMatches: true,
  v22DevByteIdentical: true,
  v21ShaUnchanged: true,
  source: 'RDR-003 verifier pre-flight, 2026-07-04',
  notes: [
    'Release SHA-256 d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239.',
    'v2.1 release SHA-256 7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893 unchanged.',
    'No ATE Pine logic modified by verifier-infrastructure changes.',
  ],
};

/** Public GitHub surface (rendered statically — no API dependency). */
export const REPO = {
  name: 'ATT-Trading-Framework',
  owner: 'Paulaustin3977',
  url: 'https://github.com/Paulaustin3977/ATT-Trading-Framework',
  defaultBranch: 'main',
  license: 'MIT',
  ciBadge: 'https://github.com/Paulaustin3977/ATT-Trading-Framework/actions/workflows/ci.yml/badge.svg',
  ciUrl: 'https://github.com/Paulaustin3977/ATT-Trading-Framework/actions/workflows/ci.yml',
  licenseBadge: 'https://img.shields.io/badge/License-MIT-yellow.svg',
};

/** Documentation surface for the docs centre. */
export interface DocEntry {
  path: string;
  title: string;
  oneLiner: string;
  category:
    | 'Getting Started'
    | 'Charter & Governance'
    | 'Architecture'
    | 'Engine Specifications'
    | 'Research'
    | 'Releases'
    | 'Operational'
    | 'Coding Standards'
    | 'Security'
    | 'Hermes Integration'
    | 'MT5';
  includeInDocs: boolean;
}

export const DOCS: DocEntry[] = [
  // Getting started
  { path: 'README.md', title: 'README', oneLiner: 'Project entry point and current status overview.', category: 'Getting Started', includeInDocs: true },
  { path: 'docs/Project_Charter.md', title: 'Project Charter', oneLiner: 'Mission, scope, principles, stakeholders, success criteria, non-goals.', category: 'Charter & Governance', includeInDocs: true },
  { path: 'docs/user/ATE_User_Handbook.md', title: 'ATE User Handbook', oneLiner: 'Plain-English guide for reading the TradingView chart.', category: 'Getting Started', includeInDocs: true },

  // Architecture
  { path: 'docs/Architecture.md', title: 'Architecture', oneLiner: 'Active architecture baseline: 8 engines, one-way flow, contract, versioning.', category: 'Architecture', includeInDocs: true },
  { path: 'docs/Research_Methodology.md', title: 'Research Methodology', oneLiner: 'Hypothesis-driven, pre-registered, reproducible research workflow.', category: 'Research', includeInDocs: true },
  { path: 'docs/Hermes_Integration.md', title: 'Hermes Integration', oneLiner: 'How the validation harness consumes and produces ATE evidence.', category: 'Hermes Integration', includeInDocs: true },

  // Releases & Operational
  { path: 'docs/Release_Process.md', title: 'Release Process', oneLiner: 'SemVer, laboratory → development → release → tag flow.', category: 'Releases', includeInDocs: true },
  { path: 'docs/releases/ATE_v2.2_Release_Manifest.md', title: 'ATE v2.2 — Release Manifest', oneLiner: 'Diagnostic RiskEngine release. Compiles cleanly in TradingView.', category: 'Releases', includeInDocs: true },
  { path: 'docs/releases/ATE_v2.1_Release_Manifest.md', title: 'ATE v2.1 — Release Manifest', oneLiner: 'Diagnostic VolatilityEngine release.', category: 'Releases', includeInDocs: true },
  { path: 'docs/ATOS_Operational_Readiness_Review.md', title: 'ATOS Operational Readiness Review', oneLiner: 'Draft ATOS-001 governance review.', category: 'Operational', includeInDocs: true },
  { path: 'docs/ATOS_v1.1_Draft.md', title: 'ATOS v1.1 — Draft', oneLiner: 'Amendments in flight for ATOS.', category: 'Operational', includeInDocs: true },

  // Engine specifications
  { path: 'specifications/ATE/TrendEngine.md', title: 'TrendEngine spec', oneLiner: 'Direction & persistence of the prevailing move.', category: 'Engine Specifications', includeInDocs: true },
  { path: 'specifications/ATE/StructureEngine.md', title: 'StructureEngine spec', oneLiner: 'Market structure: highs, lows, breakouts, range behaviour.', category: 'Engine Specifications', includeInDocs: true },
  { path: 'specifications/ATE/MomentumEngine.md', title: 'MomentumEngine spec', oneLiner: 'Rate of change and momentum characteristics.', category: 'Engine Specifications', includeInDocs: true },
  { path: 'specifications/ATE/VolatilityEngine.md', title: 'VolatilityEngine spec', oneLiner: 'Volatility regime and contraction/expansion cycles.', category: 'Engine Specifications', includeInDocs: true },
  { path: 'specifications/ATE/ConfidenceEngine.md', title: 'ConfidenceEngine spec', oneLiner: 'Strength and agreement of market evidence.', category: 'Engine Specifications', includeInDocs: true },
  { path: 'specifications/ATE/RiskEngine.md', title: 'RiskEngine spec', oneLiner: 'Safety, suitability, exposure, protective adjustment.', category: 'Engine Specifications', includeInDocs: true },
  { path: 'specifications/ATE/DashboardEngine.md', title: 'DashboardEngine spec', oneLiner: 'Presentation and information density.', category: 'Engine Specifications', includeInDocs: true },
  { path: 'specifications/ATE/DecisionEngine.md', title: 'DecisionEngine spec', oneLiner: 'Final actionable signal layer (deferred).', category: 'Engine Specifications', includeInDocs: true },

  // Coding standards / Security / MT5
  { path: 'docs/Coding_Standards.md', title: 'Coding Standards', oneLiner: 'Engineering discipline applied across ATE.', category: 'Coding Standards', includeInDocs: true },
  { path: 'CONTRIBUTING.md', title: 'Contributing', oneLiner: 'How to contribute, review, and approve.', category: 'Coding Standards', includeInDocs: true },
  { path: 'SECURITY.md', title: 'Security Policy', oneLiner: 'Vulnerability reporting and scope.', category: 'Security', includeInDocs: true },
  { path: 'docs/MT5_Subsystem_Integration.md', title: 'MT5 Subsystem Integration', oneLiner: 'Governed MetaTrader 5 subsystem: research-only, not live-trading.', category: 'MT5', includeInDocs: true },
  { path: 'specifications/MT5/Austin_M15_Scalper_Specification.md', title: 'Austin M15 Scalper — Specification', oneLiner: 'Research-only MetaTrader 5 strategy specification.', category: 'MT5', includeInDocs: true },
];

/** Roadmap status — taken verbatim from ROADMAP.md. */
export const ROADMAP = [
  {
    label: 'Completed baseline work',
    pill: 'Completed',
    items: [
      'Repository, documentation, research storage, and canonical verifier established.',
      'Immutable ATE v2.2 release stored at pine/releases/ATE_v2.2.pine.',
      'Paul Austin confirmed the immutable v2.2 release compiles cleanly in TradingView.',
      'Existing trend score, StructureEngine, MomentumEngine, ConfidenceEngine, DashboardEngine, and Research Mode implemented in v2.2.',
      'VolatilityEngine 1.0.0-draft implemented as diagnostic-only.',
      'RiskEngine 1.0.0-draft implemented as diagnostic-only (no riskApproved, no decision authority).',
      'Ten pre-existing indicator-event alerts preserved; no RiskEngine alert added.',
      'Canonical ATE release contract/integrity verification established.',
    ],
  },
  {
    label: 'Validation evidence completed',
    pill: 'Completed',
    items: [
      'RDR-002 daily VolatilityEngine validation — Weakly Supported; Keep Diagnostic.',
      'RDR-002W weekly VolatilityEngine validation — Weakly Supported; Keep Diagnostic.',
      'RDR-003 daily RiskEngine validation — Weakly Supported; Keep Diagnostic.',
      'RDR-003W weekly RiskEngine validation — Supported for controlled weekly research use; Keep Diagnostic.',
    ],
    note:
      'These classifications do not approve VolatilityEngine or RiskEngine consumption by ConfidenceEngine or DecisionEngine.',
  },
  {
    label: 'Active research lineage',
    pill: 'Active Research',
    items: [
      'TrendEngine 0.2.0-spec-impl specified and implemented in pine/development/ATE_Current.pine only.',
      'TrendEngine contract and deterministic fixture checks added to the canonical verifier.',
      'RDR-010 re-attempt: Mixed, instrument- and timeframe-dependent evidence. Retain diagnostic-only; no promotion.',
      'Investigate the near-absence of RANGE, add inference-aware / non-overlapping evaluation, pre-register any future acceptance criteria.',
      'Obtain explicit Product Owner approval before any promotion from development research to an immutable release.',
    ],
  },
  {
    label: 'Remaining diagnostic work',
    pill: 'Research',
    items: [
      'Complete and govern Pine-versus-research-mirror parity evidence where required before stronger empirical claims.',
      'Investigate documented weak/negative findings: RiskEngine calm/normal skew, thin tense/extreme samples, component dominance, threshold sensitivity.',
      'Add dedicated empirical validation for StructureEngine, MomentumEngine, ConfidenceEngine, and the existing trend score only if research priorities require claims beyond implementation/verification.',
      'Keep specifications, release manifests, RDRs, README, roadmap, and journal synchronised as evidence changes.',
      'Promote an engine only after separate verification, validation, and explicit approval gates are each satisfied.',
    ],
  },
  {
    label: 'Deferred — outside current scope',
    pill: 'Deferred',
    items: [
      'DecisionEngine implementation or activation.',
      'No trade approval/rejection logic and no riskApproved contract.',
      'Entries, exits, orders, broker connectivity, paper/live execution, position sizing, stop placement, and trade management.',
      'Any strategy layer or autonomous action based on diagnostic outputs.',
      'A live execution dashboard.',
    ],
    note:
      'A future proposal to change any of these boundaries requires a separate specification amendment, research evidence, architecture/governance review, and explicit Product Owner approval. It is not part of the current roadmap.',
  },
];

/** Top-of-mind changelog milestones. */
export const CHANGELOG_HIGHLIGHTS = [
  {
    version: 'v2.2',
    title: 'ATE v2.2 — Diagnostic RiskEngine release',
    summary:
      'RiskEngine v1.0.0-draft added as diagnostic-only. VolatilityEngine preserved. 10 alertcondition titles preserved exactly. Compiles cleanly in TradingView.',
  },
  {
    version: 'RDR-010',
    title: 'TrendEngine validation — measurement re-attempt',
    summary:
      'Mixed, instrument- and timeframe-dependent descriptive evidence. Retain as research-only diagnostic output; no promotion.',
  },
  {
    version: 'RDR-003W',
    title: 'RiskEngine weekly validation',
    summary:
      '16-asset weekly universe, 8,355 bars. Classification: Supported (controlled weekly research use). Confidence/Decision integration remains deferred.',
  },
  {
    version: 'RDR-003',
    title: 'RiskEngine daily validation',
    summary:
      '16 assets, 34,436 daily bars. Classification: Weakly Supported. Recommended weekly RDR-003W and threshold review before confidence integration.',
  },
  {
    version: 'RDR-002 / RDR-002W',
    title: 'VolatilityEngine daily + weekly validation',
    summary:
      'Classified Weakly Supported on both daily (14 assets) and weekly (15 assets). ConfidenceEngine and RiskEngine integration deferred.',
  },
  {
    version: 'EDR-001',
    title: 'Canonical ATE verifier published',
    summary:
      'tools/scripts/verify_ate.py — deterministic contract, boundary, fixture, and integrity checks. 442/442 against v2.2 release SHA.',
  },
  {
    version: 'ATOS-001',
    title: 'Operational Readiness Review drafted',
    summary:
      'Governance baseline, framework standards, RDR/EDR/ER discipline, and v1.1 amendments tabled for review.',
  },
  {
    version: 'Architecture',
    title: 'Architecture baseline approved by Paul Austin',
    summary:
      'RiskEngine moved after ConfidenceEngine; Engine Output Contract added; DashboardEngine confirmed presentation-only; RiskEngine defined as a safety/suitability filter.',
  },
];

/** Backtest / Hermes inventory summary. */
export interface BacktestSummary {
  id: string;
  rdr: string;
  engine: string;
  cadence: 'Daily' | 'Weekly' | 'Daily + Weekly';
  assets: number;
  bars: string;
  span: string;
  classification: string;
  recommendation: string;
  manifest: string;
}

export const BACKTESTS: BacktestSummary[] = [
  {
    id: 'RDR-002',
    rdr: 'RDR-002',
    engine: 'VolatilityEngine',
    cadence: 'Daily',
    assets: 14,
    bars: '~3,500+ daily bars',
    span: '2018-01-02 → 2026-07-03',
    classification: 'Weakly Supported',
    recommendation: 'Keep Diagnostic; retest thresholds after more observation',
    manifest: 'backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/',
  },
  {
    id: 'RDR-002W',
    rdr: 'RDR-002W',
    engine: 'VolatilityEngine',
    cadence: 'Weekly',
    assets: 15,
    bars: '522 weekly bars / asset',
    span: '2014-01-01 → 2026-06-29',
    classification: 'Weakly Supported',
    recommendation: 'Keep Diagnostic; retest thresholds after more observation',
    manifest: 'backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/',
  },
  {
    id: 'RDR-003',
    rdr: 'RDR-003',
    engine: 'RiskEngine',
    cadence: 'Daily',
    assets: 16,
    bars: '34,436 daily bars (total)',
    span: '2018-01-02 → 2026-07-03',
    classification: 'Weakly Supported',
    recommendation:
      'Keep Diagnostic; weekly RDR-003W and threshold review before any confidence-integration attempt',
    manifest: 'backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/',
  },
  {
    id: 'RDR-003W',
    rdr: 'RDR-003W',
    engine: 'RiskEngine',
    cadence: 'Weekly',
    assets: 16,
    bars: '8,355 weekly bars (total)',
    span: '2014-01-01 → 2026-07-03',
    classification: 'Supported',
    recommendation:
      'Keep Diagnostic; allow controlled weekly research use; Decision/Confidence integration remains deferred',
    manifest: 'backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/',
  },
  {
    id: 'RDR-010',
    rdr: 'RDR-010',
    engine: 'TrendEngine (development mirror)',
    cadence: 'Daily + Weekly',
    assets: 3,
    bars: 'Gold (GC=F) · Silver (SI=F) · Gilts (IGLT.L)',
    span: 'Reuses RDR-003 daily + RDR-003W weekly caches',
    classification: 'Mixed (instrument- and timeframe-dependent)',
    recommendation:
      'Retain as research-only diagnostic output. Do not couple downstream.',
    manifest: 'backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/',
  },
];

/** Core capabilities list (engine-agnostic). */
export const CAPABILITIES = [
  {
    title: 'Explainable trend & structure',
    body:
      'Direction, persistence, and structure-relative regime reads — reproducible from the same inputs and bar.',
  },
  {
    title: 'Momentum diagnostics',
    body:
      'Rate-of-change engine helping distinguish persistent from failing moves; pipeline input to confidence.',
  },
  {
    title: 'Volatility regimes',
    body:
      'Compressed, normal, expanding, elevated, unstable, shock, unknown — diagnostic-only, validated on daily and weekly horizons.',
  },
  {
    title: 'Confidence of evidence',
    body:
      'Aggregates trend/structure/momentum into a single confidence assessment. Strength of evidence — never risk.',
  },
  {
    title: 'Risk diagnostics',
    body:
      'Four-component scoring (vol 35 / ext 30 / struct 20 / conflict 15) with explicit `riskApproved` rejection at the contract layer.',
  },
  {
    title: 'Research Mode',
    body:
      'Per-bar, per-engine text panel on TradingView — for human inspection, never for trading commands.',
  },
  {
    title: 'Deterministic verification',
    body:
      '442/442 contract, boundary, fixture, and integrity checks gate every immutable release.',
  },
  {
    title: 'Hermes validation harness',
    body:
      'RDRs across daily and weekly horizons — multi-asset, hypothesis-locked, reproducible from the manifest.',
  },
];

/** Layouts info — these are not promises. */
export const WHAT_WE_DONT_DO = [
  'No order placement or trade execution.',
  'No broker or paper-trading API.',
  'No DecisionEngine activity.',
  'No `riskApproved` published.',
  'No claim of profitability or returns.',
  'No autonomous action based on diagnostic outputs.',
];

/** Site nav. */
export const NAV = [
  { href: '/', label: 'Overview' },
  { href: '/engine', label: 'Austin Trading Engine' },
  { href: '/engines', label: 'Engine Explorer' },
  { href: '/release/v2-2', label: 'ATE v2.2' },
  { href: '/research', label: 'Research Centre' },
  { href: '/validation', label: 'Validation & Evidence' },
  { href: '/backtests', label: 'Backtest Centre' },
  { href: '/architecture', label: 'Architecture' },
  { href: '/methodology', label: 'Methodology' },
  { href: '/docs', label: 'Documentation' },
  { href: '/roadmap', label: 'Roadmap' },
  { href: '/changelog', label: 'Changelog' },
  { href: '/about', label: 'About' },
];

// =====================================================================
// UTILITIES
// =====================================================================

export function classificationColor(c: string): 'gold' | 'green' | 'red' | 'amber' | 'gray' | 'blue' {
  switch (c) {
    case 'Supported':
      return 'green';
    case 'Weakly Supported':
      return 'amber';
    case 'Mixed':
      return 'amber';
    case 'Unsupported':
      return 'red';
    case 'Pending':
      return 'gray';
    default:
      return 'gray';
  }
}

export function statusVariant(
  s: Engine['status'],
): 'gold' | 'green' | 'red' | 'amber' | 'gray' | 'blue' {
  switch (s) {
    case 'Production Baseline':
      return 'gold';
    case 'Implemented (Release)':
      return 'green';
    case 'Implemented (Diagnostic-Only)':
      return 'amber';
    case 'Development Mirror (Research-Only)':
      return 'blue';
    case 'Presentation-Only':
      return 'blue';
    case 'Deferred':
      return 'gray';
    default:
      return 'gray';
  }
}
