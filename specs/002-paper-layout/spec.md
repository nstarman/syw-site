# Feature Specification: the paper site's layout — card header, tabs, figures

**Feature Branch**: `002-paper-layout`

**Created**: 2026-10-23

**Status**: Draft

**Input**: User description: "Set up a paper's site like its entry on the Research page — the card at the
top, without Context — then a tab bar: Overview, Explore, Figures, Cite, Info. Figures in one column,
each with a small icon of me, top-right by default and placeable per figure. Cite also describes the
software and how to cite it. Info holds a collaborator map and the funding. The card comes from the
website's data through @nstarkman/research-kit, snapshot in the paper repo by `syw-site card`, refreshed
weekly (and by hand)."

Depends on `@nstarkman/research-kit` (nstarman.github.io, feature 002-research-kit).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The card at the top (Priority: P1)

Every page of a paper's site opens with the paper's entry as the Research page shows it — title,
authors with student marks, venue · year · status, the card with thumbnail and summary, the Software row,
Abstract and BibTeX — without "Context ›".

**Independent Test**: on the example paper, the header's HTML matches what the website renders for the
same item and preset.

**Acceptance Scenarios**:

1. **Given** `website_id` in `syw-site.yml`, **When** the author runs `syw-site card`, **Then**
   `docs/card.json`, the card's thumbnail and `docs/portrait.jpg` are written from the website's data on
   GitHub, resolved by `@nstarkman/data-resolver`.
2. **Given** that snapshot, **When** the site builds (offline), **Then** every page has the header.
3. **Given** no snapshot, **When** the site builds, **Then** it fails saying to run `syw-site card`.

---

### User Story 2 - Tabs (Priority: P1)

Under the header, a tab bar in the website's pill style: Overview (`/`), Explore (`explore/`), Figures
(`figures/`), Cite (`cite/`), Info (`info/`), each its own page, the current one marked; a figure's page
marks Figures. A tab with nothing in it is not shown.

**Acceptance Scenarios**:

1. **Given** a paper with no Explore webapps and no Info content, **When** built, **Then** only Overview,
   Figures and Cite show.
2. **Given** a webapp with `explore: true`, **When** built, **Then** Explore shows it with its title and text.

---

### User Story 3 - Figures with my icon (Priority: P1)

The Figures tab shows every figure in one column: the image with my portrait stamped in a corner, "Figure
N." and the caption, then PDF · PNG · Interactive (when it has a counterpart) · More. The page shows
lossless WebP; the PNG download carries the icon too; the PDF is the paper's own.

**Acceptance Scenarios**:

1. **Given** no setting, **When** figures are made, **Then** the icon is top-right.
2. **Given** `figures: {"fig:rate": {icon: top-left}}` or `{icon: [0.82, 0.12]}`, **When** made, **Then**
   it is there; `icon: none` leaves it off; `image: 2` puts it on a figure's second image.
3. **Given** a changed setting, **When** `syw-site figures` runs, **Then** the images are re-stamped.

---

### User Story 4 - Cite: the paper and its software (Priority: P2)

Cite shows the BibTeX and links, then Software: each package the paper used (its `refs`, in order), what
it is, and how to cite it — its BibTeX or DOI where the website has one, otherwise its repository.

---

### User Story 5 - Info: collaborators and funding (Priority: P2)

Info shows a map of the paper's co-authors (`@nstarkman/collaborator-map`), the grants that funded it
(from the paper's `refs`, with their funders), and a list of the author's own pages in
`docs/src/pages/info/`.

---

### User Story 6 - The card stays current (Priority: P3)

A workflow added by `init` runs `syw-site card` weekly and on demand (`workflow_dispatch`) and opens a
pull request when the snapshot changed. It never deploys.

### Edge Cases

- `website_id` empty (no record yet): no card; a plain header (title from the paper) and a build warning.
- The website record has no highlight: the card without figure or summary, as on the website.
- A figure smaller than 400 px wide: the icon keeps its 48 px minimum.
- A paper already initialised (the spatial-correlations paper): the upgrade note moves its pages
  (`direction-earlier-layout` → `info/`) and adds `card.json`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `syw-site card` MUST resolve `website_id` with `@nstarkman/data-resolver` reading
  `nstarman/nstarman.github.io` at `main` from GitHub, and write `docs/card.json`, the thumbnail and
  `docs/portrait.jpg` (committed); `syw-site build` MUST NOT use the network.
- **FR-002**: The scaffold MUST depend on `@nstarkman/research-kit` at an exact version, and render the
  header with its `Publication`/`Card` from `docs/card.json`, using the card choice the snapshot carries.
- **FR-003**: The scaffold MUST provide the five tab pages, one per URL, with the tab bar; empty tabs are
  hidden; figure pages mark Figures.
- **FR-004**: The figures rule MUST stamp the portrait (round, white ring, ~7 % of the width, ≥ 48 px)
  into each figure's lossless WebP (shown) and PNG (download) at the configured place; the PDF is copied
  unchanged.
- **FR-005**: `syw-site.yml` MUST accept `figures: {<label>: {icon: <corner>|[x, y]|none, image: <n>}}`
  and `webapps.<name>.explore: true` (with `title`, `text`), validated.
- **FR-006**: Cite MUST list the paper's software with citation data from `docs/card.json`.
- **FR-007**: Info MUST render the collaborator map and the funding from `docs/card.json`, and list
  `src/pages/info/` pages; with none of these, the tab is hidden.
- **FR-008**: `init` MUST add `.github/workflows/card.yml`: weekly and `workflow_dispatch`, `syw-site
  card`, a pull request when changed.
- **FR-009**: The old header pieces (italic title line, `Authors`, `PaperLinks`, the overview's
  abstract) MUST give way to the card; `<Var>`, `<Fig>`, `<Webapp>` stay.
- **FR-010**: Released as a dated release (a feature release), with an upgrade note for initialised papers;
  both skills updated.

## Success Criteria *(mandatory)*

- **SC-001**: The example paper's site shows the card header, tabs and one-column stamped figures, and
  builds offline.
- **SC-002**: The spatial-correlations paper's site matches its Research-page entry in the header.
- **SC-003**: The icon's position follows the settings on every figure (checked on the example).

## Assumptions

- `@nstarkman/research-kit` is released first; the example paper uses a fixture `card.json` so CI does
  not depend on the website's data.
- The interactive counterparts (piece 2), the Explore app (piece 3) and the Overview text (piece 4) are
  separate features.
