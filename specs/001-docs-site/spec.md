# Feature Specification: docs sites for showyourwork papers

**Feature Branch**: `001-docs-site`

**Created**: 2026-10-22

**Status**: Draft

**Input**: "A skill to build GitHub-Pages docs for a showyourwork paper repo, hosting its webapps. Make
the docs a showyourwork output; pull the facts automatically; local only until arXiv. Use the
website's layout. Testbed: spatial-correlations-stream-convexities-paper."

The agreed design is in [design.md](design.md), the input to `/speckit-plan`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a docs site to a paper (Priority: P1)

The author runs one command in a showyourwork paper repository and gets a working docs site: a home
page with the paper's title, authors and abstract, a figure gallery with every figure and its real
caption, and a citation page — all taken from the paper, none typed in — viewable locally at the
same path it will have on the website.

**Why this priority**: the whole tool; everything else builds on it.

**Independent Test**: in the synthetic example paper, `syw-site init`, `syw-site build`,
`syw-site serve`; the site at `http://127.0.0.1:8000/<repo>/` shows the example's title, abstract
and figures with captions matching the PDF.

**Acceptance Scenarios**:

1. **Given** a showyourwork repository without `docs/`, **When** the author runs `syw-site init`,
   **Then** it gains `docs/` (the site scaffold and `syw-site.yml` with `publish: false`), one
   `include:` line in the `Snakefile`, and a `docs.yml` workflow — and nothing else changes.
2. **Given** an initialised paper, **When** the author runs `syw-site build`, **Then** showyourwork's
   own pipeline produces the facts, web figures and webapps, and the site is built into `docs/dist/`.
3. **Given** a built site, **When** the author runs `syw-site serve`, **Then** it is served under
   `/<repo>/` and every internal link works there.
4. **Given** an existing `docs/` that is not a syw-site scaffold, **When** `init` runs, **Then** it
   stops without overwriting and says what to move.

---

### User Story 2 - Write pages with the paper's facts (Priority: P1)

The author writes prose pages (MDX) that cite the paper's numbers, figures and abstract by name, and
the site shows exactly what the PDF shows.

**Why this priority**: prose that drifts from the paper is the problem being solved.

**Independent Test**: a page using `<Var name="…">`, `<Fig label="…">` and `<Abstract />` renders the
values and caption from the example paper; a misspelt name fails the build with the name.

**Acceptance Scenarios**:

1. **Given** a `\variable{output/x.tex}` in the paper, **When** a page uses `<Var name="x">`,
   **Then** the page shows the value as the PDF prints it (LaTeX math rendered).
2. **Given** a figure labelled `fig:a`, **When** a page uses `<Fig label="fig:a">`, **Then** it shows
   the figure image, its caption and a PDF download.
3. **Given** a reference to a fact, figure or webapp that does not exist, **When** the site builds,
   **Then** the build fails naming it.
4. **Given** a changed number in the paper, **When** the author rebuilds, **Then** the page shows the
   new number with no edit to the page.

---

### User Story 3 - Interactive figures (Priority: P2)

The author attaches a figkit webapp to the site; it is built by the paper's pipeline from the
paper's data and embedded on its figure's page, with full-page and single-file versions.

**Why this priority**: the reason for figkit; the site works without it.

**Independent Test**: the example paper's webapp, listed in `syw-site.yml`, appears embedded on its
figure page and opens full-page and as a single downloadable file.

**Acceptance Scenarios**:

1. **Given** `webapps/<name>/` (a figkit app) listed in `syw-site.yml`, **When** the site builds,
   **Then** its export runs on the pipeline's data and `figkit build` output is part of the site.
2. **Given** `<Webapp name="<name>">` on a page, **When** it renders, **Then** the app is embedded
   and links to its full-page and single-file versions.

---

### User Story 4 - Publish at arXiv submission (Priority: P2)

Until the author decides, nothing is published. On arXiv day the author flips one setting and makes
the repository public; from then on every push to `main` deploys the site to
`nstarkman.space/<repo>/`.

**Why this priority**: protects unpublished work; publishing is a one-time switch.

**Independent Test**: the generated workflow builds on every push and deploys only when
`publish: true` and the repository is public; with `publish: true` in a private repository it fails
with a message.

**Acceptance Scenarios**:

1. **Given** `publish: false`, **When** a push runs the workflow, **Then** the site is built and
   checked, and nothing is deployed or uploaded as a public artifact.
2. **Given** `publish: true` and a public repository with Pages from Actions, **When** `main` is
   pushed, **Then** the site deploys to `nstarkman.space/<repo>/`.
3. **Given** `publish: true` and a private repository, **When** the workflow runs, **Then** it fails
   before deploying and says why.

---

### User Story 5 - Agents can do all of this (Priority: P3)

An agent asked to "add a project page for this paper" follows the `syw-site` skill end to end, and
the `syw-site-upgrade` skill moves a paper to a newer syw-site release using the changelog's
migration notes. Both are installable from `nstarman/skills`.

**Why this priority**: the author works through agents; the skills make the tool usable that way.

**Independent Test**: the skills validate in `nstarman/skills` (`build_index.py --check --remote`),
and following the skill on the example paper produces the site.

**Acceptance Scenarios**:

1. **Given** the skill, **When** an agent sets up the example paper, **Then** it runs init, writes a
   page with facts by name, builds and serves, and leaves `publish: false`.
2. **Given** a release with a breaking change, **When** an agent applies `syw-site-upgrade`, **Then**
   the migration note's edit is made and the site builds.

### Edge Cases

- A `\variable` file whose value contains LaTeX (`$\sim 3$`, `\SI{}{}`): shown as the PDF shows it.
- A figure with subfigures, or several `\includegraphics`: every image is in the gallery under the
  one label and caption.
- A figure without a `\label`: listed by its file name, and the build warns.
- Multiple authors with affiliations in AASTeX's `\author[...]` / `\affiliation` syntax.
- An unfinished paper (`\todo{}` in author or text): extraction keeps the text and does not fail.
- The paper's PDF build fails: the docs build fails the same way (no stale site).
- Two papers' sites with the same component names: no clash (each site is its own build).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `syw-site init` MUST scaffold `docs/` (an Astro site wrapping every page in the
  website's `<SiteLayout>` at an exact release, `site`/`base` set from the repository name),
  `docs/syw-site.yml` (`publish: false`), a one-line `include:` of syw-site's rules in the
  `Snakefile`, and `.github/workflows/docs.yml`; it MUST NOT overwrite existing files.
- **FR-002**: syw-site MUST extract from the paper, into `docs/generated/facts.json`: title, authors
  (with affiliations and ORCID where given), abstract, each figure's label, caption and image files,
  and every `\variable` value used by the manuscript, keeping inline math as LaTeX.
- **FR-003**: The docs data (facts, web images of the paper's figures with their PDFs, built
  webapps) MUST be produced by Snakemake rules in showyourwork's own build, writing only under
  `docs/generated/`, and MUST NOT rerun figure scripts.
- **FR-004**: The scaffold MUST provide components `<Var>`, `<Fig>`, `<Webapp>`, `<Abstract>`,
  `<Authors>` and `<PaperLinks>`, and pages: home, figure gallery, one page per figure, and cite.
- **FR-005**: The site build MUST fail on a missing `facts.json` (telling the author to run
  `syw-site build`) and on any unresolved fact, figure or webapp name.
- **FR-006**: `syw-site build` MUST run the docs targets through showyourwork and then build the
  site; `syw-site serve` MUST serve it under its real base path.
- **FR-007**: The generated workflow MUST build on every push, deploy to GitHub Pages only when
  `publish: true` and the repository is public, and fail if `publish: true` in a private repository.
- **FR-008**: syw-site MUST NOT import showyourwork; it reads the repository's files.
- **FR-009**: `skills/syw-site` and `skills/syw-site-upgrade` MUST exist, meet claude.ai limits, and be
  registered in `nstarman/skills` pinned to syw-site's release tag.
- **FR-010**: Releases follow the constitution (dated, backported fixes, changelog with migration
  notes).
- **FR-011**: `examples/` MUST contain a synthetic showyourwork paper whose docs site CI builds end
  to end, with a figkit webapp.

### Key Entities

- **Paper**: a showyourwork repository (`ms.tex`, `showyourwork.yml`, `Snakefile`, `\variable` files).
- **Facts** (`facts.json`): everything the site shows that comes from the paper.
- **Settings** (`docs/syw-site.yml`): website record id, arXiv id / DOI / ADS bibcode when known,
  webapps to build, `publish`.
- **Webapp**: a figkit app in `webapps/<name>/`, built by the pipeline.
- **Docs site**: the Astro project in `docs/` and its build `docs/dist/`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: From a fresh showyourwork paper, a site with title, abstract and every figure exists
  after `init` + `build` with no hand-written content.
- **SC-002**: Every number on the example site equals the PDF's (checked by a test on the example).
- **SC-003**: With `publish: false`, no deploy or public artifact happens in any workflow run.
- **SC-004**: The testbed paper builds its site locally with its existing figures and at least one
  page using `<Var>` and `<Fig>`.
- **SC-005**: Both skills pass `nstarman/skills`' checks and install from its marketplace.

## Assumptions

- Papers use showyourwork's standard layout (`src/tex/ms.tex`, `\variable{output/…}`) and AASTeX or a
  close variant; other classes are supported as they are met (Principle VI).
- Pinned dependencies: `@nstarkman/site-layout@20261022.0.0` and figkit at its latest release tag (v0.2.0 today).
- The testbed repository is private; its integration is local-only and lands as a pull request on it.
- Linking a paper's card on the website to its site is sub-project D, not this feature.
