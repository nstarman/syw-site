# Research: docs sites for showyourwork papers

## R1 Building an extra target through showyourwork (0.4.3)

- **Finding**: `showyourwork build <target>` passes `<target>` to *both* steps: preprocess
  (`workflow/prep.smk`, which does not include the paper's `Snakefile`) and build
  (`workflow/build.smk`, which does). Preprocess therefore fails with no rule for `syw_site_all`.
  `showyourwork tarball` avoids this by giving its target only to the build step — an internal
  Python call, not a CLI option.
- **Decision**: `syw-site build` runs, in the paper's environment:
  1. `showyourwork build` — preprocess and the PDF (needed anyway: web figures come from its PDFs);
  2. the build step again with the target, exactly as showyourwork runs it:
     `snakemake --cores N --use-conda --conda-frontend <f> --reason --cache -s <build.smk> syw_site_all`
     with `SNAKEMAKE_RUN_TYPE=build` and `SNAKEMAKE_OUTPUT_CACHE=<repo>/.showyourwork/cache`, where
     `<build.smk>` is found by asking the showyourwork CLI's Python for its install path in a
     subprocess.
  All of this lives in one adapter, `syw_site/showyourwork.py`, which checks the showyourwork
  version against the ones it supports (0.4.3) and fails with a clear message otherwise; the CI
  end-to-end job runs it on the example paper.
- **Rationale**: Principle I forbids importing showyourwork into syw-site; a subprocess against
  the documented command line it already runs keeps syw-site out of showyourwork's Python and
  contains the one coupling to its internals in one tested file. Step 2 is cheap: everything the
  PDF needed is cached.
- **Alternatives**: `showyourwork build syw_site_all` (fails, above); making the docs data a
  dependency of the PDF (would rebuild docs on every PDF build and changes the paper's DAG);
  patching showyourwork upstream (worth proposing — an issue — but not something to wait for).

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

- **Decision**: `syw-site serve` = stdlib `http.server` with a handler mapping `/<repo>/…` to
  `docs/dist/…` and 404 elsewhere (so a link that forgot the base fails locally as it would live).
- **Alternatives**: `astro preview` (needs Node at serve time; fine, but the stdlib server also
  catches base mistakes the same way and needs nothing).

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
