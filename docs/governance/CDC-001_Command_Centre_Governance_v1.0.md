# CDC-001: ATE Command Centre Governance Specification

Document ID: CDC-001
Title: ATE Command Centre Governance Specification
Version: 1.0.0
Status: Draft
Date: 2026-07-05
Author: Hermes (Austin Trading Team Engineering Agent)
Reviewer: Paul Austin (pending)
Approver: Paul Austin (pending)
Related Documents: ATOS v1.1, Project Charter, Quality Manual v1.1, RDR Framework,
                   EDR Framework, ATE User Handbook, ATT Knowledge Base,
                   CDC-001 reserved documents CCM/CCU/CCR/CCV/CCA/CCP

---

## 1. Purpose

The ATE Command Centre has evolved into an official component of the Austin
Trading Engine (ATE) project. As a governed subsystem in its own right, it
requires governance independent of the TradingView Pine indicator.

CDC-001 establishes the long-term governance, scope, architecture, quality
standards, ownership, release process and documentation framework for the
Command Centre. Once approved by Paul Austin, CDC-001 becomes the governing
specification for every future version of the Command Centre.

### 1.1 Mission

The Command Centre exists to provide a central operational dashboard for the
Austin Trading Team. It provides visibility into:

- Research
- Validation
- Releases
- Documentation
- Development Progress
- Engineering Verification
- Evidence
- Roadmaps
- Project Status
- Knowledge Base
- Austin Trading Team activities

The Command Centre is an **operational information system**.

It is **NOT** a trading platform.
It is **NOT** a broker.
It does **NOT** execute trades.
It does **NOT** provide financial advice.
It does **NOT** replace TradingView.

---

## 2. Scope

The Command Centre is responsible for surfacing, navigating and
cross-referencing the following areas of the Austin Trading Engine project:

| # | Area | Description |
|---|---|---|
| 1 | Research Journal | Living Research Journal (current and archived versions). |
| 2 | RDR Library | All RDR-* folders under the experimental backtests area. |
| 3 | Engineering Reports | EDR / ERP / EDR-equivalent decision documents. |
| 4 | Design Decisions | Ratified design decisions across engines and subsystems. |
| 5 | Evidence Map | Question → evidence → decision linkages. |
| 6 | Backtests | Experimental backtest catalogue and embedded CSV previews. |
| 7 | Roadmap | ATE roadmap, phase status and forward RDR plan. |
| 8 | Project Documentation | All approved docs under `docs/`. |
| 9 | Knowledge Base | ATT Knowledge Base entries. |
| 10 | Release Management | Release manifests, version tracking and rollback status. |
| 11 | Validation Status | Canonical + ad-hoc verification results. |
| 12 | Repository Status | Git working-tree state, SHA tracking, branch hygiene. |
| 13 | Version Tracking | Pine release SHAs, verifier version, dashboard version. |
| 14 | Austin Trading Team Dashboard | Functional roles and operational ownership. |
| 15 | Project Links | GitHub, TradingView, local folder paths, Hermes workflow notes. |
| 16 | Future AI Agent Monitoring | Reserved — see §12. |

---

## 3. Out of Scope

The Command Centre **must never** perform any of the following. This list is
exhaustive within the no-execution boundary and exists to prevent scope
drift.

- No broker connectivity.
- No paper trading.
- No live trading.
- No order execution.
- No position management.
- No account management.
- No financial advice.
- No automatic trading.
- No automated investment decisions.
- No credential storage.
- No modification of research artefacts unless explicitly authorised by
  Paul Austin and recorded as a controlled change.

---

## 4. Architecture

### 4.1 Layers

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Local browser dashboard UI. |
| Backend | Python | Scanners, formatting, validation glue. |
| Repository | GitHub | Version control for all CDC artefacts. |
| Documentation | Markdown | All governance, knowledge and release docs. |
| Validation | Hermes Verifier | Canonical and ad-hoc verification. |
| Research | RDR Framework | Underlying research output surface. |
| Knowledge | ATT Knowledge Base | Cross-referenced governance memory. |

### 4.2 Design

- Modular page architecture — each page is an independent function in
  `app.py`, registered in the central `PAGES` list.
- Source folders are read-only by contract; the dashboard never writes back.
- Missing files surface as friendly warnings; the app never crashes on a
  missing report.
- Local-first: no network calls during normal operation.

### 4.3 Future Expansion

The architecture must reserve capacity for the modules listed in §12
without requiring a breaking change to the page registry or scanner
contract.

---

## 5. Design Principles

The Command Centre shall be governed by the following principles, in order
of precedence (higher-numbered principles yield to lower-numbered ones when
they conflict):

1. **Evidence before opinion.** No claim, status or classification appears
   in the dashboard without an underlying approved document or reproducible
   scanner result.
2. **Documentation first.** Every change is preceded by or accompanied by a
   documentation update (CHANGELOG, KB entry, or release note).
3. **Reproducibility.** Any visible state must be regenerable from the
   source folders using only the published scanner code.
4. **Deterministic behaviour.** Folder scans produce stable, sorted
   output; widget IDs and keys are stable across reruns.
5. **Stable navigation.** The sidebar nav is the single entry point; page
   labels and order do not change without a CDC minor-version bump.
6. **Transparency.** Scanners expose what they read and how they derive
   counts; no hidden aggregations.
7. **Readability over complexity.** Plain language in user-visible surfaces;
   technical detail in governance docs only.
8. **Minimal user friction.** The dashboard opens with a single command and
   requires no configuration for the local default case.
9. **Modular design.** Adding a page is a single-function + single-registry
   entry change.
10. **Scalable architecture.** New modules (§12) plug into the existing
    page registry without refactoring shared code.
11. **No hidden automation.** No background jobs, no scheduled writes, no
    silent file mutations.
12. **No hidden state.** Caches are explicit and time-bounded; no client-side
    state that survives a session reset unexpectedly.

---

## 6. Quality Gates

Every release of the Command Centre must satisfy **all** of the following
gates before being tagged Approved. A failed gate blocks the release.

| # | Gate | Owner | Evidence |
|---|---|---|---|
| 1 | Python compile clean | Hermes | `python3 -m py_compile app.py` exit 0. |
| 2 | Streamlit runtime verification | Hermes | AppTest sweep — every page renders without exception. |
| 3 | Canonical verifier passes | Hermes | `tools/scripts/verify_ate.py` exit 0 (where applicable). |
| 4 | Ad-hoc verifier passes | Hermes | `hermes-verify-*.py` script — 20/20 PASS minimum. |
| 5 | No unexpected repository modifications | Hermes | `git diff --name-only` empty for the official ATE repo. |
| 6 | Research folders read-only | Hermes | `find` shows zero files newer than the release commit. |
| 7 | Backtest folders unchanged unless authorised | Hermes | `find` shows zero unauthorised newer files. |
| 8 | Git working tree clean | Paul Austin | `git status --short` shows only intended + reviewed items. |
| 9 | No temporary artefacts committed | Hermes | No `hermes-verify-*` files tracked. |
| 10 | No scratch files committed | Hermes | No `*.pyc`, no `__pycache__/`, no `.DS_Store` in tracked set. |
| 11 | No broken internal links | Hermes | Markdown link audit — 0 dead anchors. |

A waiver may be recorded against a single gate, but waivers expire on the
schedule defined in the Quality Manual v1.1 and must be approved by Paul
Austin before the release is tagged Approved.

---

## 7. Versioning

The Command Centre uses Semantic Versioning: **Major.Minor.Patch**.

| Bump | Trigger | Examples |
|---|---|---|
| Major | Architectural change, scope change, breaking page-registry change. | 1.0.0 → 2.0.0 |
| Minor | New page, new scanner, new feature, backwards-compatible. | 1.0.0 → 1.1.0 |
| Patch | Bug fix, doc fix, dependency bump within current spec. | 1.1.0 → 1.1.1 |

Every release shall:

- Be tagged in GitHub with the full SemVer string.
- Carry a corresponding entry in `CHANGELOG.md` under a dated section.
- Carry a corresponding CCR-001 release-notes entry.
- Preserve the prior version as a rollback target (see §8).

---

## 8. Release Policy

### 8.1 Stages

The Command Centre release lifecycle has six stages:

| # | Stage | Description | Authority to advance |
|---|---|---|---|
| 1 | Development | In-progress work on a feature branch. | Hermes |
| 2 | Internal Testing | Self-verification + ad-hoc verifier green. | Hermes |
| 3 | Release Candidate | Tagged SemVer-RCn; awaits external review. | Hermes |
| 4 | Approved Release | All §6 gates green; merged to main. | Paul Austin |
| 5 | Archived | Superseded; retained for reference. | Automatic |
| 6 | Rollback | Restored to a prior Approved Release. | Paul Austin |

### 8.2 Rollback Policy

- A rollback returns the Command Centre to the most recent Approved Release
  that is not itself broken.
- Rollback packages must remain **permanently archived** — they are
  immutable once a successor Approved Release exists.
- A rollback event must be recorded as a CCR-001 release-notes entry
  within 24 hours.
- A rollback does **not** delete the failed release; it merely redirects
  the `Approved` pointer.

---

## 9. Documentation Standards

Every Command Centre document shall contain, at minimum, the following
metadata and sections. This template applies to CDC-, CCM-, CCU-, CCR-,
CCV-, CCA- and CCP-prefixed documents.

### 9.1 Required Metadata

- Document ID
- Title
- Version
- Status
- Date
- Author
- Reviewer
- Approver

### 9.2 Required Sections

- Purpose
- Scope
- Assumptions
- Limitations
- Dependencies
- Verification Status
- Revision History
- Related Documents

The `Specification_Template.md` style (top metadata block, numbered
sections, fenced example blocks where helpful) is the canonical layout.

---

## 10. Validation Policy

Every Command Centre release requires, **at minimum**:

1. Canonical verification — `tools/scripts/verify_ate.py` exit 0 (where
   the release touches the canonical scope).
2. Ad-hoc verification — a `hermes-verify-*.py` script executed against
   the release candidate, with all checks PASS.
3. Manual review — Paul Austin inspects the rendered dashboard.
4. Evidence attached — verifier output, ad-hoc script output and any
   screenshots are committed to the release's evidence directory.
5. Verification logs archived — logs are stored in the rollback package.
6. Git verification — `git status` clean, expected SHAs confirmed.
7. SHA verification where applicable — Pine release SHAs match the
   manifests; Command Centre SHA matches the CCR-001 entry.

---

## 11. Security

The Command Centre is governed by the following security principles:

- **Read-only by default.** Source folders are never written to.
- **No credentials displayed.** No API keys, tokens or secrets are loaded
  or rendered, even from environment variables.
- **No API keys.** The dashboard does not call authenticated endpoints.
- **No secrets.** No secrets are stored on disk by the application.
- **No automatic external communication.** No outbound network calls
  during normal operation.
- **No automatic execution.** No background processes, cron jobs or
  scheduled tasks originate from the Command Centre.
- **No broker interaction.** The dashboard has no concept of a broker,
  account, position or order.

These principles are the operational expression of the project-level
`docs/governance/Security_Policy.md` for the Command Centre scope.

---

## 12. Future Expansion

The architecture reserves capacity for the following modules. None are
implemented in v1.0.0; each will require its own CDC amendment before
promotion to Active.

| # | Reserved Module | Notes |
|---|---|---|
| 1 | Agent Management | Multi-agent status, personas, persona routing. |
| 2 | Live Monitoring | Real-time RDR / verification / heartbeat stream. |
| 3 | Telemetry | Structured event logs from verifiers and scanners. |
| 4 | Metrics | Quantitative rollups of validation throughput, gate failures. |
| 5 | Notifications | Cross-channel alerting for verification failures. |
| 6 | Release Dashboard | Visualisation of the CCR-001 release history. |
| 7 | Research Analytics | Cross-RDR aggregations, asset-class splits, trend lines. |
| 8 | Trading Dashboard | Read-only Pine state and alert surface — **never** an order entry surface. |
| 9 | Performance Analytics | Backtest performance rollups with disclaimer banners. |
| 10 | System Health | Homelab / Ollama / Hermes uptime surface. |
| 11 | AI Operations Dashboard | Persona activity, task counts, fallback chain state. |

Any of these modules crossing into the §3 Out-of-Scope boundary (broker,
orders, advice, automatic trading, etc.) is **prohibited** by this CDC.

---

## 13. Relationship to ATE

The Command Centre is a governed subsystem of the Austin Trading Engine.
Its relationship to the wider governance pack:

| Document | Scope | Relationship to CDC-001 |
|---|---|---|
| ATOS | Overall ATE operational governance. | ATOS is upstream; CDC-001 derives from ATOS but does not modify it. |
| Project Charter | Mission, scope, no-execution boundary. | CDC-001 honours the no-execution boundary (§3). |
| Quality Manual v1.1 | Quality gates, waivers, manifests. | CDC-001 §6 and §8 reference Quality Manual gates. |
| RDR Framework | Research Decision Records. | Command Centre surfaces RDR outputs read-only (§2). |
| EDR Framework | Engineering Decision Records. | Command Centre is an EDR consumer (CC architecture changes require an EDR). |
| Knowledge Base | Permanent principles and findings. | CDC-001 amendment requires a corresponding KB entry. |
| ATE User Handbook | Plain-English user guide for Pine users. | Command Centre is for operators; handbook is for Pine users. No functional overlap. |

**CDC-001 governs only the Command Centre.**
**ATOS governs the overall Austin Trading Engine.**
The two never conflict by design; where ambiguity exists, ATOS prevails
unless an explicit CDC amendment is approved by Paul Austin.

---

## 14. Ownership

| Role | Holder |
|---|---|
| Product Owner | Paul Austin |
| Primary Development Agent | Hermes |
| Verification Authority | Hermes Verifier |
| Final Approval Authority | Paul Austin |

**Hermes may recommend governance changes.**
**Only Paul Austin may approve governance changes.**

A governance change request must:

1. Be filed as a CDC amendment draft with explicit `Status: Draft`.
2. List the section(s) being added, removed or modified.
3. Reference any EDR, RDR or Quality Manual change that the amendment
   depends on.
4. Carry a corresponding CHANGELOG entry under `[Unreleased]`.
5. Carry a corresponding KB entry under the appropriate principle.
6. Remain `Draft` until Paul Austin explicitly sets the status to
   `Approved`.

---

## 15. Document Classification

Every Command Centre document shall carry **one** status from the
following set:

| Status | Meaning |
|---|---|
| Draft | Authored, awaiting review. Not authoritative. |
| Under Review | Submitted to Paul Austin. Not yet authoritative. |
| Approved | Paul Austin has approved this document. Authoritative. |
| Superseded | Replaced by a newer approved document. Retained for history. |
| Archived | No longer applicable; retained for record only. |

Every document shall display, in its top metadata block:

- Document ID
- Version
- Status
- Author
- Reviewer
- Approver
- Date
- Revision History

---

## 16. Command Centre Documentation Framework

The official Command Centre documentation hierarchy is reserved as follows.
Only **CDC-001** is fully authored during this task. The remaining
documents are reserved as future controlled documents and **must not** be
authored ad hoc — each requires an explicit CDC amendment.

| Document ID | Title | Purpose |
|---|---|---|
| **CDC-001** | Command Centre Governance Specification | **Authoritative governance.** This document. |
| CCM-001 | Command Centre Maintenance Manual | Installation, upgrades, backups, recovery. |
| CCU-001 | Command Centre User Manual | Plain-English guide: every page, navigation, workflow. |
| CCR-001 | Command Centre Release Notes | Release summaries and version history. |
| CCV-001 | Command Centre Validation Standard | Runtime testing, verification procedures, quality gates. |
| CCA-001 | Command Centre Architecture | System architecture, folder structure, design philosophy. |
| CCP-001 | Command Centre Product Vision | Long-term roadmap, objectives, strategic direction. |

Reserved document IDs are immutable once published. A reserved document
that is never authored does not consume an ID; it can be cancelled by
a CDC amendment that explicitly retires the reservation.

---

## 17. Approval

Once **Paul Austin** formally sets the `Status` field of this document to
`Approved`, CDC-001 v1.0.0 becomes the governing specification for every
future version of the ATE Command Centre.

Until that approval event, CDC-001 v1.0.0 is a **Draft** and **must not**
be cited as authority for any scope, gate or ownership claim against the
Command Centre.

---

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-07-05 | Hermes | Initial draft. |

---

## Related Documents

- `docs/governance/ATOS.md` (or successor) — overall ATE operational governance.
- `docs/Project_Charter.md` — mission, scope, no-execution boundary.
- `docs/governance/Quality_Manual.md` — quality gates, waivers, manifests.
- `docs/governance/Research_Decision_Record_Standard.md` — RDR framework.
- `docs/governance/Engineering_Decision_Record_Standard.md` — EDR framework.
- `docs/governance/Security_Policy.md` — project-level security.
- `docs/knowledge/ATT_Knowledge_Base.md` — permanent principles and findings.
- `docs/user/ATE_User_Handbook.md` — Pine user handbook (separate scope).
- `CHANGELOG.md` — release log.
- `pine/releases/ATE_v2.2_Release_Manifest.md` — current Pine release manifest.

---

**End of CDC-001 v1.0.0 — Draft.**