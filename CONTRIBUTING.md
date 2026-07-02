# Contributing

The Austin Trading Engine is maintained by the Austin Trading Team. Contributions from team members are welcome and follow a strict evidence-first process.

## Workflow

1. **Specification first.** Every change starts in `specifications/ATE/`. If you are adding or modifying engine behaviour, update the spec before writing code.
2. **Development branch.** Work happens in `pine/development/ATE_Current.pine`. Released versions in `pine/releases/` are immutable.
3. **Evidence.** Every engine change must include evidence: a Hermes backtest output, a regression note, or a documented observation.
4. **Tests.** Behaviour changes require at least one regression case in `tests/Regression/`.
5. **Review.** Pull requests are reviewed against `docs/Coding_Standards.md` and `docs/Research_Methodology.md`.

## Commit Conventions

- Imperative mood ("Add TrendEngine spec", not "Added").
- Reference the engine or doc changed in the subject.
- Keep subjects under 72 characters.

## Evidence Requirements

A contribution is **not** accepted on intent alone. It must ship with:

- A clear statement of the hypothesis
- The dataset(s) used
- The evaluation method
- The outcome, including negative results

Negative results are first-class outputs. Record them honestly.

## What Not To Do

- Do not commit directly to `pine/releases/`.
- Do not repaint: any feature referencing future data is rejected.
- Do not introduce lookahead in validation: every backtest must respect the bar-close rule.

## Review Checklist

- [ ] Spec updated
- [ ] Code follows Coding Standards
- [ ] Regression test added or updated
- [ ] Hermes backtest recorded under `backtests/Hermes/`
- [ ] CHANGELOG entry drafted