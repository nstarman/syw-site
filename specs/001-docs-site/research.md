# Research: docs sites for showyourwork papers

## R1 Building the docs target through showyourwork

- **Decision**: `syw-site build` runs `showyourwork build --cores N --conda-frontend F [extra]
  syw__main syw_site_all` — the PDF (showyourwork's default target, needed anyway: web figures come
  from its PDFs) and the docs data in one run, with showyourwork's cache and config.
- **Version**: this needs showyourwork's main branch (`0.4.4.dev*`, the author's papers pin commit
  44d15103f), whose `showyourwork build <targets>` strips targets before preprocessing
  (showyourwork#690, merged 2026-03-28). The 0.4.3 release passes them to preprocessing too, where a
  target from the paper's Snakefile is unknown; 0.4.3 also runs on Python 3.10, which figkit cannot
  join. syw-site refuses other versions.
- **History**: the first implementation read only `cli/main.py`, concluded main had the 0.4.3
  behavior, reran showyourwork's build step by hand, and filed showyourwork#769; a follow-up found
  #690 and removed the workaround.

## R2 Facts extraction

- **Decision**: stdlib only — a small brace-matching scanner over `ms.tex` with `%` comments
  stripped (escaped `\%` kept), reading `\title{}`, AASTeX `\author[opts]{name}` (opts:
  `orcid`, `sname`, `gname`), `\affiliation{}`, the `abstract` environment, `figure`/`figure*`
  environments (`\includegraphics[...]{path}` — all of them, `\caption{}`, `\label{}`), and every
  `\variable{path}`. A `\variable` file's value is its content with `%` comment lines and the
  trailing `%` removed, trimmed. `\todo{x}` is kept as `x`. Text stays LaTeX (math rendered by
  KaTeX on the site).
- **Rationale**: the shapes are few and known (testbed checked); a TeX parser library adds a
  dependency for little.
- **Alternatives**: pylatexenc (more general, still not TeX; add only if a paper needs it).

## R3 Web figures from the paper's PDFs

- **Decision**: render each figure PDF's first page to PNG at 2× CSS width with `pypdfium2`
  (Apache-2.0/BSD, pip wheel, no system dependency); ship the PDF beside it for download.
- **Alternatives**: `pdftoppm` (system dependency), PyMuPDF (AGPL).

## R4 Webapps

- **Decision**: a webapp in `syw-site.yml` lists its data inputs:
  ```yaml
  webapps:
    globe: { inputs: [src/data/directional.npz] }
  ```
  Rule `syw_site_webapp_<name>`: inputs = those files + `webapps/<name>/**`; runs
  `python webapps/<name>/export.py --out docs/.syw-site/webapps/<name>/data` then
  `figkit build webapps/<name> --data <each dataset dir> --out docs/public/generated/webapps/<name>/site
  --single-file docs/public/generated/webapps/<name>/<name>.html`. figkit is pinned (`v0.2.0`).

## R5 The site: Astro + MDX + math

- **Decision**: Astro 7 (as the website), `@astrojs/mdx`, `remark-math` + `rehype-katex` (KaTeX's
  CSS and fonts bundled from npm, never a CDN), `@nstarkman/site-layout@20261022.0.0`; exact
  versions and a committed lockfile in the scaffold. Facts are imported as JSON at build time.
  Components throw on unknown names, so the build fails naming them (FR-005).
- **Decision**: generated output lives at `docs/public/generated/` (git-ignored), so
  Astro serves and copies it with no integration; `facts.json` is imported from there.

## R6 Serving under the base path

- **Decision**: `syw-site serve` = `astro preview` in `docs/`: it serves `docs/dist/` under the
  base path only (checked: `/<repo>/…` 200, `/`, `/research/` 404), so a link that forgot the base
  fails locally as it would live. Node is already required to build.
- **Alternatives**: a stdlib `http.server` with a base-path handler (first implementation; removed in
  review: ~60 lines with its test for what Astro already does).

## R7 Workflow in the paper repo (`docs.yml`)

- **Decision**: on push and pull request: set up the paper's environment (the template uses
  `conda-incubator/setup-miniconda` + `pip install showyourwork==0.4.3 syw-site@git+…@<tag>`;
  the author adapts it to their env), Node 22, `syw-site build`. A `publish` job runs only on
  `main` when `publish: true` is read from `docs/syw-site.yml`: it fails if
  `github.event.repository.private` is true, else `actions/upload-pages-artifact` +
  `actions/deploy-pages` (environment `github-pages`). With `publish: false` no artifact is
  uploaded at all.
- **Rationale**: SC-003 — nothing leaves CI while private.

## R8 syw-site's own CI

- **Decision**: (1) unit tests (pytest: facts, settings, init idempotence, serve mapping, the
  adapter's command line); (2) site job: Node + a fixture `facts.json` + Astro build of the scaffold
  (fast; covers components and FR-005 failure on a bad name); (3) end-to-end job: conda +
  showyourwork 0.4.3 + `syw-site init/build` on `examples/paper`, asserting the site's numbers
  equal the `\variable` values (SC-002); (4) `CI Pass` gate; PR preview of the example site
  (Cloudflare, as figkit) — the example is synthetic, so previews are allowed (Principle IV).
