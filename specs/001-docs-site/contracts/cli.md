# Contract: `syw-site` CLI

| command | does | fails when |
|---|---|---|
| `syw-site init [--repo owner/name]` | writes `docs/` scaffold, `docs/syw-site.yml` (`publish: false`), `include:` line in `Snakefile`, `.github/workflows/docs.yml`; repo from `git remote get-url origin` | not a showyourwork repo; any target file exists and differs (prints what to move) |
| `syw-site facts [-o PATH]` | writes `facts.json` (also the Snakemake rule's action) | `ms.tex` missing; a `\variable` file missing |
| `syw-site build [--cores N]` | `showyourwork build`, then the docs target (research R1), then `npm ci` (if needed) and `astro build` in `docs/` | any step fails (exit code passed through) |
| `syw-site serve [--port 8000]` | serves `docs/dist/` at `/<repo>/` only | `docs/dist/` missing |

Snakemake: `include: syw_site.rules_path()` — the line `init` adds is
`include: __import__("syw_site").rules_path()`. Targets: `syw_site_facts`, `syw_site_figures`,
`syw_site_webapp_<name>`, `syw_site_all`.
