# Feature Specification: the Figures tab as a gallery

**Feature Branch**: `005-figures-gallery`

**Created**: 2026-10-29

**Status**: Done

**Input**: User description: "the Figures pane should be more of a gallery, and clicking into it
brings you to the details, which includes the caption and interactive elements" — with only the
first sentence of a caption, or part of it ("Mock observation of the GD-1 stream"), on each card,
and a back link to the gallery on a figure's page (no previous/next links). This replaces 002's
"Figures in one column".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find a figure at a glance (Priority: P1)

The Figures tab is a grid of cards (as many columns as fit, one on a phone). Each card shows the
figure's image, "Paper Figure N" and the caption's short title, and opens the figure's page. A
figure with an interactive version is marked "Interactive".

**Independent Test**: the example's Figures tab has one card per figure linking to its page, no
full caption, and the badge only on a figure that a webapp names.

### User Story 2 - The details, and back (Priority: P1)

A figure's page is as before — its image or interactive version, the whole caption, the downloads —
with a link back to the gallery at the top.

**Independent Test**: each figure page links to `figures/`.

### Edge Cases

- A caption that opens with an italic title (`\emph{…}`): the title, cut as below.
- Commas, colons and parentheses inside math or braces do not cut the title.
- A figure with several images: the card shows the first; its page shows them all.

## Requirements *(mandatory)*

- **FR-001**: A card's title is the caption's leading `\emph`/`\textit`/`\textbf` title if any, else
  its first sentence, cut at the first colon, comma, semicolon or opening parenthesis outside math
  and braces; rendered as the caption is (math, references).
- **FR-002**: The badge appears where a webapp's `figure` is the figure's label or slug.
- **FR-003**: Other uses of `<Fig>` (the overview, cards) are unchanged.

## Success Criteria *(mandatory)*

- **SC-001**: On CP1, every card's title is a short phrase (e.g. "Mock observation of the GD-1
  stream"); the grid is three columns on a desktop and one on a phone.
