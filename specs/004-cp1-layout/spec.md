# Feature Specification: what the first paper's site taught the scaffold

**Feature Branch**: `004-cp1-layout`

**Created**: 2026-10-28

**Status**: Done

**Input**: User description: "Upstream the CP1 site's scaffold changes into syw-site and update the
skill": the layout changes made by hand to the first real paper's site (paper-stream-convexities-1),
so the next paper gets them from `syw-site init`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Figures named as the paper names them (Priority: P1)

A reader tells the paper's figures from the site's own interactive figures: the paper's are "Paper
Figure N" (in the caption, the alt text and the figure page's title), and the tab is "Figures".

**Independent Test**: the example site's figure caption and page title read "Paper Figure N"; the
tab reads "Figures".

### User Story 2 - Links that read as a row (Priority: P1)

Under a figure's caption, the links sit on a line of their own: the pages (Interactive, More) on the
left, the downloads (PDF · PNG) on the right. An interactive figure has the same row: More on the
left, Download HTML on the right.

**Independent Test**: the example's figure and webapp captions each hold one `fig-links` row with
those links on those sides.

### User Story 3 - An interactive figure with its caption, sized to fit (Priority: P1)

The author captions an interactive figure in the overview, `<Webapp name="…">Caption.</Webapp>`, and
can set it apart in a card, `<div class="syw-card">…</div>`, as a paper figure. The frame takes the
app's own height once it loads, and follows it when the app's layout changes with the page's width.

**Independent Test**: the example's overview shows a captioned webapp in a card; the frame carries
`data-fit`.

### User Story 4 - Cite last (Priority: P2)

The tabs are Overview, Explore, Figures, Info, Cite: Cite, which a reader looks for last, at the end.

**Independent Test**: the example's tabs, in that order.

### Edge Cases

- A webapp without a caption: just the link row.
- An app on another origin cannot be measured: the frame keeps `height` (all apps are same-origin
  here, built into the site).

## Requirements *(mandatory)*

- **FR-001**: The scaffold's `Fig.astro`, `figures/[slug].astro` and alt text MUST say "Paper Figure N".
- **FR-002**: Figure and webapp captions MUST end in one `.fig-links` row: pages left, downloads right.
- **FR-003**: `Webapp.astro` MUST take its caption as content and size its frame to the app's content.
- **FR-004**: `Page.astro` MUST style `.syw-card` and `.fig-links`; the overview template MUST show how
  to use both.
- **FR-005**: The tabs MUST be Overview, Explore, Figures, Info, Cite.
- **FR-006**: The scaffold MUST pin `@nstarkman/research-kit` 20261028.0.0 (the pins list the
  author's papers).
- **FR-007**: The changelog MUST give a migration note for papers initialised earlier; the
  `syw-site` skill MUST describe captions and cards.

## Success Criteria *(mandatory)*

- **SC-001**: The site tests and CI's end-to-end build pass with the new assertions.
- **SC-002**: The scaffold files equal CP1's (but for its own name, base and content).
