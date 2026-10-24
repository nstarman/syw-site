# Contract: CLI and workflow additions

- `syw-site card` — writes `docs/card.json`, `docs/public/card/*`, `docs/portrait.jpg` from the website at `main` (needs the network).
- `syw-site figures` — re-stamps (offline).
- `.github/workflows/card.yml` — `schedule: weekly` + `workflow_dispatch`: `syw-site card`, PR if changed (`peter-evans/create-pull-request`), never deploys.
