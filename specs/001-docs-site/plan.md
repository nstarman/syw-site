# Implementation Plan: docs sites for showyourwork papers

**Branch**: `001-docs-site` | **Date**: 2026-10-22 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), [design.md](design.md)

## Summary

A Python package `syw-site` (CLI + Snakemake rules + an Astro scaffold) that a showyourwork paper
includes: rules generate `facts.json`, web figures and figkit webapps into `docs/public/generated/`
inside showyourwork's own build; the scaffold's MDX pages and components render them inside
`<SiteLayout>`; a generated workflow publishes only when the author says so. Plus two skills and a
synthetic example paper built end to end in CI.

## Technical Context

**Language/Version**: Python ≥ 3.11 (package, rules); Astro 7 + MDX in the scaffold (Node 22)

**Primary Dependencies**: figkit (git tag `v0.2.0`), pyyaml, pypdfium2; scaffold: astro,
@astrojs/mdx, remark-math, rehype-katex, katex, @nstarkman/site-layout `20261022.0.0` (exact pins)

**Storage**: files only (`facts.json`, generated images, built webapps)

**Testing**: pytest (unit + adapter); Astro build of the scaffold on a fixture; end-to-end
showyourwork 0.4.3 build of `examples/paper` in CI

**Target Platform**: macOS/Linux author machines; GitHub Actions; GitHub Pages under nstarkman.space

**Project Type**: CLI/library + project scaffold

**Performance Goals**: incremental `syw-site build` after a PDF build reruns only changed docs rules

**Constraints**: no showyourwork import (Principle I); nothing public while `publish: false`
(Principle IV); the scaffold never loads from a CDN

**Scale/Scope**: one paper per site; ~10 figures, ~100 variables, a few webapps

## Constitution Check

| Principle | Check | Status |
|---|---|---|
| I Bridge | figkit via its CLI, layout via npm, showyourwork via its CLI/Snakemake in a subprocess (research R1); one adapter file holds the showyourwork coupling, version-checked | ✅ |
| II Facts from the paper | all paper content via `facts.json`; components fail on unknown names | ✅ |
| III SYW output | rules run inside showyourwork's build step; figures converted, not re-run | ✅ |
| IV Private | `publish: false` default; no artifact upload unless publishing; private-repo guard; example is synthetic | ✅ |
| V Looks like the website | `<SiteLayout>` pinned exactly; `serve` under the base path | ✅ |
| VI Small | stdlib TeX scanner; no Astro integration (public/ dir); no options beyond the spec | ✅ |
| VII Tested | unit tests over real-shaped TeX; e2e on the example | ✅ |

Re-check after design: unchanged.

## Project Structure

```text
specs/001-docs-site/   spec, design, plan, research, data-model, contracts/, quickstart, tasks
pyproject.toml         syw-site; deps figkit@git+…@v0.2.0, pyyaml, pypdfium2; script syw-site
src/syw_site/
  __init__.py          __version__, rules_path()
  facts.py             ms.tex + \variable files → facts dict (R2)
  settings.py          docs/syw-site.yml load + validate
  figures.py           PDF → PNG (R3)
  showyourwork.py      the adapter (R1)
  init.py              scaffold copy, Snakefile include, workflow
  serve.py             base-path server (R6)
  cli.py               init | facts | build | serve
  rules.smk            syw_site_facts | _figures | _webapp_<name> | _all
  template/            docs/ scaffold (package.json, lockfile, astro.config.mjs, src/, .gitignore)
                       + workflows/docs.yml
skills/syw-site/, skills/syw-site-upgrade/
examples/paper/        synthetic showyourwork paper (one script figure, two \variable values, a webapp)
tests/                 pytest; fixtures/ (TeX snippets, a facts.json for the site job)
.github/workflows/ci.yml   unit | site | e2e | preview | CI Pass
CHANGELOG.md
```

**Structure Decision**: single Python package with package data (template, rules).

## Complexity Tracking

| Deviation | Why | Simpler alternative rejected |
|---|---|---|
| The adapter reruns showyourwork's build step itself (R1) | `showyourwork build <target>` breaks in preprocess | waiting for upstream; a docs-in-PDF-DAG dependency |
