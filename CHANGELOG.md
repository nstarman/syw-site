# Changelog

Versions are dates, `YYYY.MM.DD`; a bug-fix release of one is `YYYY.MM.DD.N`. Breaking changes are
announced here with a migration note: **What changed**, **Find**, **Edit**.

## Unreleased

## 2026.10.31.1 — 2026-10-31

### Changed — migration

- The Cite tab: the paper's links are buttons with their marks (arXiv, the journal, ADS, and the
  showyourwork "s" for the code), and the BibTeX sits on a panel with **Copy** in its corner, as
  on nstarkman.space's Publications. The paper's entry at the top no longer links to the site
  itself (its `homepage`, which nstarkman.space now uses for a paper's own site), and shows its
  showyourwork button. The scaffold now pins `@nstarkman/site-layout` 20261022.0.2 (the "s") and
  `@nstarkman/research-kit` 20261028.0.1 (the `syw` link). **What changed**: the Cite tab's look
  and the header's buttons. **Find**: `docs/src/pages/cite.astro`, `docs/src/components/PaperLinks.astro`,
  `docs/src/components/Page.astro`, `docs/src/lib/store.js`, `docs/package.json`. **Edit**: copy them
  from the scaffold (or `syw-site upgrade`), `npm install` in `docs/`, then refresh the snapshot
  (`syw-site card`).

## 2026.10.31 — 2026-10-31

### Changed — migration

- A figure's or app's link to its own page reads **Open**, not "More", and a paper figure with an
  interactive version has that one link instead of "Interactive · More" (both went to the same page).
  `<Webapp full="explore/">` adds **Full**, a link to a fuller version elsewhere on the site.
  **What changed**: the labels under captions. **Find**: `docs/src/components/Fig.astro`,
  `docs/src/components/Webapp.astro`. **Edit**: copy both from the scaffold (or `syw-site upgrade`);
  optionally pass `full` to a `<Webapp>` that has a fuller version.

## 2026.10.29.3 — 2026-10-29

### Changed — migration

- The Figures tab is a gallery: a card per figure (its image, "Paper Figure N", the caption's short
  title, and "Interactive" where a webapp names it) opening the figure's page, which now links back.
  **What changed**: the tab no longer shows every figure with its caption. **Find**:
  `docs/src/pages/figures/index.astro`. **Edit**: copy it, `pages/figures/[slug].astro`,
  `components/Page.astro` and `lib/tex.js` from the scaffold (or `syw-site upgrade`).
- Links under a caption read "Download HTML · PDF · PNG": the word once, each format its own link. A
  figure page whose webapp replaces the image has one row under the caption (the app's More; its HTML
  with the figure's PDF and PNG). **Find**: `components/Fig.astro`, `components/Webapp.astro`.
  **Edit**: copy them and `pages/figures/[slug].astro` from the scaffold.

## 2026.10.29.2 — 2026-10-29

- `<Webapp>` frames follow the site's theme toggle: the page's `data-theme` is copied onto the app's
  document as it changes. Before, an app followed the system's setting, so with the system dark and
  the site toggled light, the figure stayed dark. Copy `docs/src/components/Webapp.astro` from the
  scaffold (or `syw-site upgrade`).
- A webapp may replace its figure's image on the figure's page: `replaces: true` (needs `figure`).
  The caption and downloads stay; elsewhere the figure is the image as before.
- figpress-apps 2026.10.29: apps follow the site's theme toggle too (with the `<Webapp>` change above).

## 2026.10.29.1 — 2026-10-29

- A webapp may be a figpress-plotly figure: `webapps/<name>/figure.py` defining `figure` is written
  as the figure's web page and single file, where a figpress-apps app's would be. Nothing to change
  for existing apps.

## 2026.10.29 — 2026-10-29

### Changed — migration

Learned on the first real paper's site:

- Figures and tabs: the paper's figures are "Paper Figure N" (caption, alt text, figure page), the
  tab is "Figures", and the tabs end with Info, then Cite.
- Under a caption, the links are a row of their own: pages (Interactive, More) left, downloads
  (PDF · PNG) right. An interactive figure has the same row — More, Download HTML — under its
  caption, which `<Webapp name="…">Caption.</Webapp>` now takes as content.
- `<Webapp>`'s frame takes the app's own height once it loads and follows it (`height` is only the
  height until then).
- `<div class="syw-card">…</div>` sets a figure or an app apart in the overview.
- The scaffold pins `@nstarkman/research-kit` 20261028.0.0, whose map pins list the author's papers.

- **What changed**: the scaffold's `src/components/Fig.astro`, `Webapp.astro`, `Page.astro`,
  `src/lib/tabs.js`, `src/pages/figures/[slug].astro` and `package.json`. **Find**: a paper
  initialised before this release (`ls docs/src/components/Webapp.astro`); unless you changed them,
  `diff` them against syw-site's `src/syw_site/template/docs/`. **Edit**: copy those five files from
  the template; in `docs/package.json` set `"@nstarkman/research-kit": "20261028.0.0"` and run
  `npm install` in `docs/`. A `<Webapp>` caption you wrote after it (`<Webapp …/> <p>…</p>`) can
  move inside it.

## 2026.10.28.1 — 2026-10-28

### Changed — migration

- **What changed**: webapps are built with [figpress-apps](https://github.com/nstarman/figpress-apps)
  2026.10.28 (installed from PyPI), the renamed figkit, instead of figkit 0.2.0; `syw-site webapp`
  no longer builds an app that imports `figkit/…`. **Find**:
  `grep -rn "figkit" webapps/ docs/syw-site.yml environment.yml`. **Edit**: move each app as
  figpress-apps' [2026.10.28 migration notes](https://github.com/nstarman/figpress-apps/blob/main/CHANGELOG.md)
  say (`figkit/<m>.js` → `figpress-apps/<m>.js`, `figkit/figkit.js|css` →
  `figpress-apps/index.js|css`, `import figkit` → `import figpress_apps`, …); in `syw-site.yml`'s
  `python:` and in `environment.yml`, replace `figkit @ git+https://github.com/nstarman/figkit@v0.2.0`
  with `figpress-apps==2026.10.28`. Data exported by figkit still loads; it need not be re-exported.

## 2026.10.28 — 2026-10-28

### Fixed

Found adding syw-site to the first real paper (AASTeX with siunitx, cleveref, natbib and a local
preamble package):

- A paper's macros defined in its own packages (`.sty` files under `src/tex/` that `ms.tex` loads,
  and the ones they load by bare name through `\input@path`) were missing from `facts.json`, so
  math using them (`\mrm{}`, `\mcal{}`) stopped the site build; `syw-site facts` now reads them
  (`ms.tex`'s own definitions win), and a change to a `.sty` re-runs the facts rule.
- Figure slugs kept other characters than letters, digits, `.`, `_` and `-` from the label:
  `fig:cosmology:zlr` was `/figures/cosmology:zlr/`, which some file systems and artifact uploads
  refuse. Such characters are now `-`: `/figures/cosmology-zlr/`.
- `tex.js` (the scaffold's LaTeX-to-HTML conversion):
  - `\ensuremath` and `\textsl` (LaTeX, not KaTeX) stopped the build in math.
  - siunitx: prefixes (`\giga`, `\mega`, `\kilo`, `\centi`, `\milli`, `\micro`; `\kilo\parsec`
    read "k pc"), `\square`/`\cubic`, `\parsec`, `\gram`, `\percent`, `\arcminute`, `\arcsecond`,
    `\unit{}`, `\numrange{}` and numbers without a mantissa (`e12` → 10¹²); siunitx inside the
    paper's macros (`\newcommand{\kpc}{\unit{\kilo\parsec}}`).
  - `\autoref`/`\cref` to a figure read "Figure N" (`\autoref` was not handled); to anything else
    they read "the paper" (capitalised at a sentence start), not "()" or a sentence without subject.
  - `\citet`/`\citetalias` with `Surname+:YYYY` keys read "Surname et al. (YYYY)" (`Surname:YYYY`:
    "Surname (YYYY)") instead of vanishing; a dropped `\citep` takes the space before it.
  - In text, the paper's macros without arguments are expanded (`\euclid` → *Euclid*) and
    `\ensuremath{}` is math, instead of vanishing.

### Changed — migration

- **What changed**: the slugs of figures whose label has a `:` (after `fig:`) or other characters
  than letters, digits, `.`, `_`, `-`, so those figures' pages move (`/figures/cosmology:zlr/` →
  `/figures/cosmology-zlr/`); and the scaffold's `docs/src/lib/tex.js`. **Find**: slugs with `:` in
  `docs/syw-site.yml` (`figures:` keys, a webapp's `figure:`) and in `<Fig label="…">` in
  `docs/src/pages/`; links to the old figure pages; `docs/src/lib/tex.js`. **Edit**: use the
  label (`fig:cosmology:zlr`, which always works) or the new slug; take `tex.js` from the new
  scaffold (`src/syw_site/template/docs/src/lib/tex.js`), re-adding any extensions of your own
  (most papers' workarounds are now upstream — drop them); then `syw-site build`.

## 2026.10.24 — 2026-10-24

### Added

- The paper's site opens with its entry as nstarkman.space draws it — the website's own
  `Publication` and card (`@nstarkman/research-kit`), without the context link — from
  `docs/card.json`, which **`syw-site card`** fetches from the website's data on GitHub with the
  card's images and the author's portrait; a `Card` workflow refreshes it weekly or by hand.
- **Tabs**: Overview, Explore (webapps with `explore: true`, with `title` and `text`), Figures,
  Cite, Info; one page each, empty ones hidden.
- **Figures** in one column, each with the author's portrait stamped, semi-transparent (top-right
  by default; `figures: {<label>: {icon, image, alpha}}` in `syw-site.yml`, `icon` a list for one per
  panel), shown as lossless WebP, offered as PNG.
- **Cite** lists the software the paper used and how to cite each package; **Info** shows the
  co-authors' collaborator map, the grants that funded the paper (its `refs` on the website) and the
  author's pages in `src/pages/info/`.

### Changed — migration

- **What changed**: the scaffold's header, `Page.astro`, the pages and `astro.config.mjs` (the
  research-kit alias); `Card.astro` (the website card iframe) is gone; `docs/package.json` gains
  `@nstarkman/research-kit`. **Find**: `docs/src/components/Page.astro`, `docs/astro.config.mjs`,
  `docs/package.json`, `docs/src/pages/`. **Edit**: take those files from the new scaffold
  (`src/syw_site/template/docs/`), keeping your own pages; move extra pages to
  `docs/src/pages/info/`; add `docs/scripts/card.mjs`, `docs/src/lib/{store,tabs}.js` and
  `.github/workflows/card.yml`; then `npm install` in `docs/` and `syw-site card`.

## 2026.10.23.2 — 2026-10-23

### Fixed

- `docs.yml` checked out without submodules or history, so a paper whose LaTeX preamble is a git
  submodule failed to build in CI; it now checks out with `submodules: recursive` and
  `fetch-depth: 0`, as showyourwork's own workflow does. Papers already initialised: add both to
  the checkout step of `.github/workflows/docs.yml`.

## 2026.10.23.1 — 2026-10-23

### Fixed

Found adding syw-site to the first real paper:

- Figures labelled with a paper's own label command (`\figlabel{}`, any `\…label{}`) had no
  label; they now get it, and labels never show in text.
- A paper's math macros (`\newcommand`, `\renewcommand`, `\DeclareMathOperator` in `ms.tex`)
  stopped the site build in KaTeX; they now reach it through `facts.json` (`macros`).
- `syw-site init`'s Snakefile include broke the paper's own build in an environment without
  syw-site; it is now guarded by `import syw_site` (the docs rules are off there, with a message).
  Papers already initialised can replace their include line with the new block (see `init.py`).
- `docs.yml` stalled on rules cached on Zenodo: it now passes the `SANDBOX_TOKEN` secret, never
  `OVERLEAF_TOKEN`, and stops after 120 minutes.
- The paper's own links (Overview, Figures, Cite) stuck over the website's header (its stylesheet
  makes every `nav` sticky); a reference to a section or appendix showed "?"; a figure's "PDF" and
  "More" links ran together.
- `$math$` written in a page did not get the paper's macros and showed KaTeX's red error text; it
  now gets them (`astro.config.mjs`), and an unknown command stops the build.

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
