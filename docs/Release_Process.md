# Release Process

## Goals

- Reproducible releases
- Clear evidence trail per version
- No silent changes to released code

## Versioning

- Semantic Versioning: `MAJOR.MINOR.PATCH`
- **MAJOR.** Breaking change to an engine interface or to the decision contract.
- **MINOR.** New engine, new feature, additive change.
- **PATCH.** Bug fix, performance, documentation.

## Promotion Path

1. **Laboratory.** Experimental ideas live in `laboratory/Experimental/`.
2. **Development.** Promoted code lives in `pine/development/ATE_Current.pine`.
3. **Release.** Frozen code is copied into `pine/releases/ATE_vX.Y.pine`.
4. **Tagged.** The release commit is tagged `vX.Y.Z` on `main`.

A version is **never** edited in-place after release. Corrections ship as a new version.

## Pre-release Checklist

- [ ] Spec for each affected engine updated
- [ ] CHANGELOG entry drafted
- [ ] ROADMAP item closed
- [ ] Hermes backtests recorded under `backtests/Hermes/`
- [ ] Regression suite green
- [ ] Coding Standards review complete
- [ ] No repainting, no lookahead violations confirmed

## Release Day

1. Merge development branch into `main`.
2. Copy `pine/development/ATE_Current.pine` to `pine/releases/ATE_vX.Y.pine`.
3. Update `README.md` Current Version.
4. Update `CHANGELOG.md`.
5. Tag the commit: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
6. Push the tag: `git push origin vX.Y.Z`.

## Post-release

- Open a Hermes validation sweep across all asset categories.
- File any drift between expected and actual behaviour as a regression case.