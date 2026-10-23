# Changelog

Versions are dates, `YYYY.MM.DD`; a bug-fix release of one is `YYYY.MM.DD.N`. Breaking changes are
announced here with a migration note: **What changed**, **Find**, **Edit**.

## Unreleased

## 2026.10.22.2 — 2026-10-23

### Fixed

Backported from 2026.10.23.1 (found adding syw-site to the first real paper):

- Figures labelled with a paper's own label command (`\figlabel{}`, any `\…label{}`) had no
  label; they now get it, and labels never show in text.
- A paper's math macros (`\newcommand`, `\renewcommand`, `\DeclareMathOperator` in `ms.tex`)
  stopped the site build in KaTeX; they now reach it through `facts.json` (`macros`).
- `syw-site init`'s Snakefile include broke the paper's own build in an environment without
  syw-site; it is now guarded by `import syw_site` (the docs rules are off there, with a message).
- `docs.yml` stalled on rules cached on Zenodo: it now passes the `SANDBOX_TOKEN` secret, never
  `OVERLEAF_TOKEN`, and stops after 120 minutes.
- The paper's own links (Overview, Figures, Cite) stuck over the website's header (its stylesheet
  makes every `nav` sticky); a reference to a section or appendix showed "?"; a figure's "PDF" and
  "More" links ran together.

## 2026.10.22.1 — 2026-10-22

### Fixed

- A webapp's `inputs` may be files the paper's pipeline makes; `syw-site.yml` no longer requires
  them to exist before the build.

## 2026.10.22 — 2026-10-22

First release: `syw-site init | facts | build | serve`, the Snakemake rules, the Astro docs
scaffold with `<Var>`, `<Fig>`, `<Webapp>`, `<Abstract>`, `<Authors>`, `<PaperLinks>`, the publish
workflow, and the `syw-site` and `syw-site-upgrade` skills. Supports showyourwork main
(`0.4.4.dev*`, tested at 44d15103f) with figkit v0.2.0 and `@nstarkman/site-layout` 20261022.0.0.
