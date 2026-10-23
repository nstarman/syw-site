# Changelog

Versions are dates, `YYYY.MM.DD`; a bug-fix release of one is `YYYY.MM.DD.N`. Breaking changes are
announced here with a migration note: **What changed**, **Find**, **Edit**.

## Unreleased

## 2026.10.23 — 2026-10-23

### Changed

- `syw-site build` is a single `showyourwork build syw__main syw_site_all`: showyourwork main
  already builds targets from the paper's Snakefile (showyourwork#690), so syw-site no longer reruns
  showyourwork's build step itself. No change for papers.

### Fixed

- A webapp's `inputs` may be files the paper's pipeline makes; `syw-site.yml` no longer requires
  them to exist before the build. (Also in 2026.10.22.1.)

## 2026.10.22.1 — 2026-10-22

### Fixed

- A webapp's `inputs` may be files the paper's pipeline makes; `syw-site.yml` no longer requires
  them to exist before the build.

## 2026.10.22 — 2026-10-22

First release: `syw-site init | facts | build | serve`, the Snakemake rules, the Astro docs
scaffold with `<Var>`, `<Fig>`, `<Webapp>`, `<Abstract>`, `<Authors>`, `<PaperLinks>`, the publish
workflow, and the `syw-site` and `syw-site-upgrade` skills. Supports showyourwork main
(`0.4.4.dev*`, tested at 44d15103f) with figkit v0.2.0 and `@nstarkman/site-layout` 20261022.0.0.
