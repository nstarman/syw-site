# Feature Specification: build webapps with figpress-apps

**Feature Branch**: `003-figpress-apps`

**Created**: 2026-10-28

**Status**: Done

**Input**: User description: "figkit is renamed figpress-apps (v2026.10.28, on PyPI); move syw-site to
it."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A paper's webapps build with figpress-apps (Priority: P1)

An author whose paper lists webapps in `docs/syw-site.yml` builds the site; `syw-site webapp`
builds each app with figpress-apps.

**Independent Test**: CI's end-to-end job builds the example paper's `helix` webapp and site.

**Acceptance Scenarios**:

1. **Given** an app importing `figpress-apps/<module>.js`, **When** `syw-site webapp <name>` runs,
   **Then** the served site and single file are built, vendoring `figpress-apps-2026.10.28`.
2. **Given** a paper moving from figkit, **When** its author reads this release's changelog, **Then**
   a migration note says what to find and edit, pointing to figpress-apps' own notes.

## Requirements *(mandatory)*

- **FR-001**: syw-site MUST depend on `figpress-apps==2026.10.28` from PyPI and call
  `figpress_apps.cli`.
- **FR-002**: The example paper, scaffold comments, skills, README, AGENTS.md and constitution MUST
  name figpress-apps; the constitution is amended (PATCH, wording).
- **FR-003**: The changelog MUST carry a migration note (What changed, Find, Edit).

## Success Criteria *(mandatory)*

- **SC-001**: All tests pass, including CI's end-to-end build of the example's webapp.
- **SC-002**: No live file names figkit except the migration note.
