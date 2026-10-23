---
description: "Tasks for the paper layout"
---

# Tasks: the paper site's layout

**Input**: spec.md, plan.md, research.md (R1–R6), data-model.md, contracts/cli.md
**Depends on**: `@nstarkman/research-kit@20261023.0.0` (published)

## Phase 1: Setup
- [ ] T001 Template `docs/package.json` + lockfile: `@nstarkman/research-kit` `20261023.0.0` (exact); `astro.config.mjs`: alias `@nstarkman/research-store` → `src/lib/store.js`, `ssr.noExternal` and `environments.prerender.resolve.noExternal` `[/^@nstarkman\//]`
- [ ] T002 `src/lib/store.js` (template): `createStore` over `docs/card.json`, all store names exported, image paths (highlights, student photos) rewritten to the site's own `card/` copies; no `website_id` → an empty store and `root = null`; `website_id` but no `card.json` → throw "run `syw-site card`"
- [ ] T003 [P] `tests/fixtures/card.json`: a synthetic snapshot (a paper with a highlight, two co-authors with places, a package with its paper, a grant) — no real record

## Phase 2: US1 the card header, US6 its refresh
- [ ] T004 `docs/scripts/card.mjs` (template): `collect(website_id, fromGitHub(nstarman/nstarman.github.io, main))` → `card.json`; downloads, from that commit, every snapshot image (highlights, student photos) to `public/card/` and `cv/assets/portrait.jpg` to `portrait.jpg`
- [ ] T005 `src/syw_site/card.py` + CLI `syw-site card`: `npm ci` if needed, then `node scripts/card.mjs` in `docs/`; test with a fake (no network)
- [ ] T006 `Page.astro`: header = research-kit `Publication` (abstract, `card` = snapshot's preset) for the root; with no root, the paper's title from facts; the paper's own nav goes
- [ ] T007 `template/workflows/card.yml` (weekly + `workflow_dispatch`; Node; `npm ci`; `node scripts/card.mjs`; PR when changed; never deploys); `init` writes it; test its triggers

## Phase 3: US2 tabs
- [ ] T008 `TabBar.astro` (website pill style) in `Page.astro`; `tab` prop; pages `index.mdx` (Overview), `explore.astro`, `figures/index.astro`, `figures/[slug].astro` (marks Figures), `cite.astro`, `info/index.astro`; empty Explore/Info hidden
- [ ] T009 Settings: `webapps.<name>.explore` (bool), `title`, `text`; Explore shows each

## Phase 4: US3 figures with the icon
- [ ] T010 `figures.py`: `stamp()` — round portrait, white ring, `max(48, 0.07·W)`, margin `0.02·W`, corners or `[x, y]`, `none`; lossless WebP + PNG; PDF copied; tests for each position and the minimum
- [ ] T011 Settings `figures: {<label>: {icon, image}}` validated; facts images gain `webp`; rules: figures rule inputs + `docs/portrait.jpg`, `docs/syw-site.yml`
- [ ] T012 `Fig.astro`: WebP image, "Figure N.", caption, PDF · PNG · Interactive · More; Figures tab one column

## Phase 5: US4 Cite, US5 Info
- [ ] T013 `cite.astro`: BibTeX + links, then Software: each package (`softwareUsed`), its summary, how to cite it (its paper's BibTeX/DOI via the store, else its repository)
- [ ] T014 `info/index.astro`: `CollabMap` (when the snapshot has co-authors), Funding (the root's `grant` refs: title, funder, dates), the author's `info/*` pages listed

## Phase 6: Polish
- [ ] T015 Site test (`-m site`) with the fixture card: header, tabs (hidden empties), one-column figures, cite software, info map + funding
- [ ] T016 Example paper and e2e unchanged in spirit (no `website_id`: plain header); skills + references + README + CHANGELOG (upgrade note); version for a dated release
- [ ] T017 PR, review, merge on the author's go, release; then apply to the spatial-correlations paper (its PR #3)
