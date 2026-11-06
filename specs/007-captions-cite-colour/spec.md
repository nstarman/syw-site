# Feature Specification: Captions read citations and colour as the PDF does

**Feature Branch**: `captions-cite-colour`

**Created**: 2026-11-05

**Status**: Draft

**Input**: User description: "Captions and prose read citations and colour as the PDF does. Today the site's TeX converter drops \citep entirely and reads \citet only for keys shaped Surname:YYYY, so a real paper's caption reads "Figure 1 of with the updated…" and "(as revised in )"; `{\color{gray} solid gray}` prints "gray solid gray"; and a `\\` line break prints literally. The facts gain the paper's citations… \citet{k} as "Sidhu et al. (2020)", \citep{k} as "(Sidhu et al. 2020)"… \color keeps only its text; \\ reads as a space. Alt text and short titles follow. Updates the facts schema reference and both skills."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A caption names the papers it cites (Priority: P1)

A reader opens a figure on a paper's site. Its caption cites other papers, as captions often do
("Figure 1 of \citep{Sidhu2020reconsider} with the updated constraints"; "(\citet{Graham2018} as
revised in \citet{Sidhu2020reconsider})"). The caption names each cited paper by its authors and
year, so the sentence reads whole.

**Why this priority**: today the citation vanishes and leaves a broken sentence ("Figure 1 of with
the updated…", "( as revised in )"), on the page, in the figure's alt text and in the gallery's
short title. It is the most visible fault on a real paper's site.

**Independent Test**: build a site from a paper whose captions cite keys of any shape defined in its
bibliography; every cited key reads as authors and year, and no caption has an empty pair of
parentheses or a dangling "of".

**Acceptance Scenarios**:

1. **Given** a caption with `\citet{k}` and k is in the paper's bibliography with three or more
   authors, the first "Sidhu", year 2020, **When** the site is built, **Then** it reads
   "Sidhu et al. (2020)".
2. **Given** `\citep{k}` for the same key, **Then** it reads "(Sidhu et al. 2020)".
3. **Given** a key with one author, **Then** "Sidhu (2020)"; two authors, **Then**
   "Sidhu and Starkman (2020)".
4. **Given** `\citep{a,b}`, **Then** "(Sidhu et al. 2020; Graham et al. 2018)".
5. **Given** `\citep[see][p. 3]{k}`, **Then** "(see Sidhu et al. 2020, p. 3)".
6. **Given** a key not in the bibliography, **Then** a `Surname:YYYY` or `Surname+:YYYY` key reads
   from the key ("Surname", "Surname et al.") in every citation form, and any other key is left out
   without leaving empty parentheses or a doubled space.

---

### User Story 2 - Colour and line breaks in a caption read as text (Priority: P2)

A caption describes regions by their colour in the plot ("the {\color{gray} solid gray} region",
"\textcolor{cyan}{light blue}") and breaks a long caption with `\\`. The page shows the words once,
without the colour name doubled, and the line break as a space.

**Why this priority**: it garbles reading ("the gray solid gray region", a literal `\\`) but the
meaning survives, so it comes after citations.

**Independent Test**: a caption with `{\color{c} text}`, `\textcolor{c}{text}` and `\\` renders
"text", "text" and a space.

**Acceptance Scenarios**:

1. **Given** `{\color{gray} solid gray}`, **Then** "solid gray".
2. **Given** `\textcolor{cyan}{light blue}`, **Then** "light blue".
3. **Given** `regions.\\ Objects`, **Then** "regions. Objects".

### Edge Cases

- A paper with no `\bibliography` (or a `.bib` that is missing): the facts' citations are empty and
  captions behave as today; the build does not fail.
- An author written as a group (`{Astropy Collaboration}`), with accents (`{\'E}`, `\"{o}`), or as
  "Given Family" instead of "Family, Given": the label uses the family name as printed.
- An entry with no year: the label is the authors alone ("Sidhu et al.").
- Several `.bib` files in `\bibliography{a,b}`: all are read; the first definition of a key wins.
- A `\cite`, `\citealp` or `\citeauthor` (natbib's other forms): `\cite` and `\citealp` read like
  `\citep` without parentheses; `\citeauthor` reads as the authors alone.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The facts MUST include `citations`: for each key the paper cites anywhere in its text
  that its bibliography defines, an author label and a year (or none).
- **FR-002**: The author label MUST be the first author's family name alone (one author), both family
  names joined by "and" (two), or the first family name and "et al." (three or more).
- **FR-003**: The site MUST render `\citet{k}` as "label (year)", `\citep{k}` as "(label year)",
  several keys joined by "; ", and `\citep`'s optional notes before and after, as natbib prints them.
- **FR-004**: A key missing from the citations MUST read from the key when it is shaped
  `Surname:YYYY` or `Surname+:YYYY` (in every citation form), and otherwise be left out; leaving
  it out MUST NOT leave empty parentheses.
- **FR-005**: `{\color{c} …}` and `\textcolor{c}{…}` MUST render their text alone; `\\` in prose
  MUST render as a space.
- **FR-006**: The figure alt text and the gallery's short titles MUST follow, since they are made
  from the same captions.
- **FR-007**: A missing or unreadable bibliography MUST NOT fail the build; citations are then empty.
- **FR-008**: The facts schema reference and both skills MUST describe the new field and behaviour.

### Key Entities

- **Citation**: a bibliography key the paper cites, with its author label and year as the site
  prints them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the macro-lightning paper's site, Figure 2's caption reads "Figure 1 of Sidhu et al.
  (2020)…" (or the parenthetical form) and "(Graham et al. (2018) as revised in Sidhu et al.
  (2020))", with no empty parentheses and no "gray gray".
- **SC-002**: Across the example paper and the test fixtures, no rendered caption, alt text or short
  title contains "()", "( ", a raw citation key, a colour name doubled, or a literal `\\`.
- **SC-003**: A paper without a bibliography builds and renders exactly as before.

## Assumptions

- The bibliography is BibTeX (`.bib`), named by `\bibliography{…}` relative to `src/tex/`, as
  showyourwork papers use.
- Only keys the paper actually cites are carried, so the facts stay small.
- No full bibliography is shown on the site; a citation reads as author and year in place.
