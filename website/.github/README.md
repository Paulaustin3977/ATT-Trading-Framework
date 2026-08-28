# Austin Trading Team website — GitHub Actions CI/CD

This directory hosts the GitHub Actions workflow that builds the ATT website
(`/website`) and deploys it to **GitHub Pages** on every push to `main` *if* the
`website/` subdirectory changed, and on every feature branch as a Pages preview.

It is intentionally kept separate from the existing framework CI in
`.github/workflows/ci.yml` — they run independently.

## Triggers

| Trigger               | Effect                                                       |
| --------------------- | ------------------------------------------------------------ |
| `push` to `main`      | Build `website/`, run type-check, deploy to GitHub Pages.    |
| `pull_request`        | Build & lint only (no deploy).                               |
| `workflow_dispatch`   | Manual build & deploy (used for one-off publishes).          |

## Permissions

- `contents: read` — read source
- `pages: write`, `id-token: write` — Pages deploy via official action

## Environment

- `NODE_VERSION: '22'`

## Concurrency

`pages-prod` concurrency group with `cancel-in-progress: false` for the deploy
job, so a half-deployed run never gets pre-empted.

## Pages configuration

The workflow assumes **GitHub Pages → Source: GitHub Actions** in repo
Settings → Pages. The repository `ATT-Trading-Framework` will publish from this
action; no separate `gh-pages` branch is used.

For custom-domain or branch-based previews, edit `concurrency.group` and add a
`cname` step in the `deploy` job.
