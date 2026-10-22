---
description: "Tasks for docs sites for showyourwork papers"
---

# Tasks: docs sites for showyourwork papers

**Input**: `specs/001-docs-site/` — spec, design, plan, research (R1–R8), data-model, contracts/, quickstart

**Tests**: required (constitution VII; spec SC-002, FR-005).

## Phase 1: Setup

- [X] T001 Create `pyproject.toml` (name `syw-site`, version `2026.10.22`, Python ≥ 3.11, deps `figkit @ git+https://github.com/nstarman/figkit@v0.2.0`, `pyyaml`, `pypdfium2`; script `syw-site = syw_site.cli:main`; package data `template/**`, `rules.smk`; dev group pytest) and `src/syw_site/__init__.py` (`__version__`, `rules_path()`); `uv lock`
- [X] T002 [P] Add `CHANGELOG.md` (`## Unreleased`) and expand `README.md` (install from a tag, the four commands)
- [X] T003 [P] Add `.github/workflows/ci.yml` with job `unit` (uv, pytest) and the `CI Pass` gate (`re-actors/alls-green`); later phases add `site`, `e2e`, `preview`

## Phase 2: Foundational

- [X] T004 [P] `src/syw_site/settings.py` + `tests/test_settings.py`: load `docs/syw-site.yml` per data-model.md (unknown keys fail; `publish` bool, default false; webapp names `[a-z0-9-]+`, folder exists, inputs exist, optional `figure` label)
- [X] T005 [P] `src/syw_site/facts.py` + `tests/test_facts.py` + `tests/fixtures/tex/`: research R2 scanner → the facts dict of data-model.md (schema 1): `%` comments (keep `\%`), `\title`, AASTeX `\author[orcid=…,sname=…,gname=…]{}` + `\affiliation{}`, `abstract`, `figure`/`figure*` (all `\includegraphics`, `\caption`, `\label`; unlabelled → file stem + warning), `\todo{x}` → `x`, `\variable{output/p.tex}` → key `p`, value = file minus `%` lines and trailing `%`; missing variable file fails naming it

**Checkpoint**: `uv run pytest` passes.

## Phase 3: User Story 1 — add a docs site to a paper (P1) 🎯 MVP

**Independent test**: init + build + serve on `examples/paper` shows title, abstract, captioned figures under `/<repo>/`.

- [ ] T006 [P] [US1] `examples/paper/`: synthetic showyourwork 0.4.3 paper — `showyourwork.yml`, `Snakefile`, `src/tex/ms.tex` (AASTeX 7, two authors, abstract with math, one `figure` + one `figure*` with two panels, labels), `src/scripts/` (figure scripts, a `make_variables.py` writing two `\variable` files incl. one with math), `environment.yml`; no real paper content (Principle IV)
- [ ] T007 [P] [US1] `src/syw_site/figures.py` + test: PDF → PNG at 2× via pypdfium2 (R3), PDF copied beside it
- [ ] T008 [US1] `src/syw_site/rules.smk`: `syw_site_facts` (inputs `src/tex/ms.tex` + the `\variable` files it names; output `docs/public/generated/facts.json`), `syw_site_figures` (inputs the paper's figure PDFs; outputs `docs/public/generated/figures/*`), `syw_site_all`; plus `syw-site facts` CLI path used by the rule
- [ ] T009 [P] [US1] `src/syw_site/showyourwork.py` + test: version check (0.4.3), locate `build.smk` via a subprocess, the R1 command line and env; tests assert the command without running showyourwork
- [ ] T010 [US1] `src/syw_site/template/` docs scaffold: `package.json` (exact pins: astro 7, @astrojs/mdx, remark-math, rehype-katex, katex, `@nstarkman/site-layout` 20261022.0.0) + `package-lock.json`, `astro.config.mjs` (`site`, `base` from a placeholder filled by init, mdx + math), `.gitignore` (`public/generated/`, `.syw-site/`, `dist/`, `node_modules/`), `syw-site.yml`, `src/lib/facts.js` (imports `public/generated/facts.json`; missing → throw "run `syw-site build`"), pages `index.mdx`, `figures/index.astro`, `figures/[slug].astro`, `cite.astro`, all in `<SiteLayout section="/research/" repo>`
- [ ] T011 [US1] `src/syw_site/init.py` + tests: copies the scaffold, fills repo/base (from `--repo` or `git remote get-url origin`), appends `include: __import__("syw_site").rules_path()` to `Snakefile` once, writes `.github/workflows/docs.yml`; refuses a non-showyourwork repo; refuses to overwrite a differing existing file (lists it); rerun is a no-op
- [ ] T012 [P] [US1] `src/syw_site/serve.py` + test: stdlib server, `/<repo>/…` → `docs/dist/…`, 404 elsewhere (R6)
- [ ] T013 [US1] `src/syw_site/cli.py`: `init | facts | build | serve` per contracts/cli.md; `build` = adapter, then `npm ci` when `node_modules` is missing or stale, then `npx astro build` in `docs/`
- [ ] T014 [US1] CI job `e2e`: conda + showyourwork 0.4.3 + TeX as showyourwork needs, Node 22; `syw-site init --repo nstarman/syw-site-example && syw-site build` in a copy of `examples/paper`; assert `docs/dist/index.html` has the title and each figure page exists

## Phase 4: User Story 2 — pages with the paper's facts (P1)

**Independent test**: a page with `<Var>`, `<Fig>`, `<Abstract />` renders the example's values; a bad name fails the build.

- [ ] T015 [US2] Template components `src/components/{Var,Fig,Abstract,Authors,PaperLinks}.astro` per contracts/components.md; unknown name → `throw new Error('syw-site: no variable "<name>" in facts.json')` (and likewise figure); math via KaTeX; `index.mdx` uses them
- [ ] T016 [US2] CI job `site` + `tests/site/`: install the scaffold with `tests/fixtures/facts.json`, `astro build` passes; a page with `<Var name="nope" />` fails with `nope` in the output (script `tests/site/run.sh`)
- [ ] T017 [US2] e2e assertion (SC-002): every `\variable` value of the example appears verbatim (after KaTeX for math) on the home page

## Phase 5: User Story 3 — interactive figures (P2)

- [ ] T018 [US3] `rules.smk`: `syw_site_webapp_<name>` per settings (R4): inputs + `webapps/<name>/**`; `export.py --out docs/.syw-site/webapps/<name>/data`; `figkit build` → `docs/public/generated/webapps/<name>/site/` and `<name>.html`; `syw_site_all` includes them
- [ ] T019 [US3] Template `src/components/Webapp.astro` (iframe of `…/site/` sized to content, links to full page and single file; unknown/unbuilt → throw) and its use on `figures/[slug].astro` when a webapp names the figure (`figure:` key in the webapp settings — add to data-model and settings validation)
- [ ] T020 [US3] `examples/paper/webapps/<name>/`: a minimal figkit app over the example's data; e2e asserts its page and single file exist

## Phase 6: User Story 4 — publish at arXiv (P2)

- [ ] T021 [US4] `src/syw_site/template/workflows/docs.yml` per R7: build on push/PR; `publish` job on `main` only when `publish: true` (read with `yq`-free Python one-liner), fails when `github.event.repository.private`, else upload-pages-artifact + deploy-pages; no artifact upload otherwise
- [ ] T022 [US4] `tests/test_workflow.py`: parse the template; assert the publish job's `if:` requires `main` and the setting, the private-repo guard step precedes upload, and no upload step exists outside the publish job (SC-003)

## Phase 7: User Story 5 — skills (P3)

- [ ] T023 [P] [US5] `skills/syw-site/SKILL.md` (+ `references/components.md`, `settings.md`, `facts-schema.md`): design §5 steps 1–5; frontmatter `name` = folder, description ≤ 1024
- [ ] T024 [P] [US5] `skills/syw-site-upgrade/SKILL.md`: apply CHANGELOG migration notes between two tags, as figkit-upgrade
- [ ] T025 [US5] `tests/test_skills.py`: both skills' frontmatter meets claude.ai limits (name `[a-z0-9-]{1,64}` = folder, description ≤ 1024)

## Phase 8: Polish and release

- [ ] T026 [P] `AGENTS.md`: layout, testing commands, the adapter's showyourwork coupling and how to support a new showyourwork version
- [ ] T027 [P] CI job `preview`: Cloudflare Pages preview of the example site per PR (skips without the secrets), sticky comment, as figkit
- [ ] T028 Run all checks locally that can run (unit, site); open the PR; independent subagent review; fix; merge on the author's go
- [ ] T029 After merge, with the author's go: tag `v2026.10.22` (or the release date), GitHub release; register both skills in `nstarman/skills` (PR there); propose the upstream showyourwork issue (R1) to the author before filing
- [ ] T030 Testbed (local only, private): a PR on the paper repo with `syw-site init`, its `docs/` content moved per design §2, one page using `<Var>` and `<Fig>`, built and served locally (SC-004) — after asking the author how they run showyourwork, and without touching their uncommitted work

## Dependencies

T001 → T004/T005 → US1. T006, T007, T009, T012 parallel. T008 needs T005/T007; T010 before T011; T013 needs T008–T012; T014 needs all US1. US2 needs T010; US3 needs T008/T015; US4 needs T011; US5 any time after US1. T028 after all; T029, T030 after merge.

## Implementation strategy

MVP = Phases 1–4 (a site of facts and figures). US3–US5 complete the feature in the same PR. Nothing
of the testbed's is committed anywhere public.
