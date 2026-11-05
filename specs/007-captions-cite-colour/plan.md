# Implementation Plan: Captions read citations and colour as the PDF does

**Branch**: `captions-cite-colour` | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/007-captions-cite-colour/spec.md`

## Summary

`facts.py` reads the paper's `.bib` (the files `\bibliography{…}` names, under `src/tex/`) for the keys
the paper cites, and writes `citations: {key: {"label": "Sidhu et al.", "year": "2020"}}` into
`facts.json`. The scaffold's `tex.js` renders `\citet`, `\citep`, `\cite`, `\citealp` and
`\citeauthor` from it, falling back to today's `Surname:YYYY` reading; it drops `\color{…}` and
`\textcolor{…}`'s colour argument and reads `\\` as a space. `plain()` (alt text) and `short()`
(gallery titles) go through the same text path, so they follow.

## Technical Context

**Language/Version**: Python ≥ 3.11 (`facts.py`); the scaffold's JavaScript (`tex.js`, run by Astro/Node)

**Primary Dependencies**: none new. The `.bib` reader is a few dozen lines on `facts.py`'s existing
brace scanner (`_group`); a BibTeX library would be a new dependency for two fields.

**Storage**: `docs/public/generated/facts.json` gains an optional field (`schema` stays 1, as the
schema reference says for optional fields)

**Testing**: pytest — `tests/test_facts.py` over a fixture `.bib` beside the fixture paper;
`tests/test_site.py`'s `TEXT` table and `plain` checks, run in Node against `fixtures/facts.json`

**Target Platform**: a paper's docs build (Snakemake rule `syw_site_facts`) and its Astro site

**Project Type**: library + site scaffold

**Performance Goals**: N/A (a `.bib` of a few hundred entries is read once per build)

**Constraints**: no new dependency; a missing or unreadable `.bib` never fails the build (FR-007)

**Scale/Scope**: `facts.py`, `tex.js`, two fixtures, two tests, the facts schema reference, both
skills, CHANGELOG

## Constitution Check

| Principle | How this plan meets it |
|---|---|
| I. A bridge, never a reimplementation | Reads the paper's own `.bib` like it reads `ms.tex`; no BibTeX engine, no import of showyourwork. |
| II. Facts come from the paper | Citations come from the paper's bibliography through `facts.json`; nothing is typed into pages. A citation is not a name a page refers to, so a missing key falls back rather than failing the build. |
| III. The docs are a showyourwork output | Produced by the existing `syw_site_facts` rule; the `.bib` joins its inputs so a changed bibliography rebuilds the facts. |
| IV. Private until the author publishes | No change to publishing; fixtures are synthetic. |
| V. Looks like the website | No layout change; captions read better. |
| VI. Small, generic, earned | Every paper cites; the macro-lightning paper needed it. Only two fields per key are read. |
| VII. Tested on a paper's shape | Unit tests over a fixture `.bib` with one, two and many authors, groups, accents and a missing year; the site test table gains the citation and colour cases. |
| Releases and Upgrades | A feature with fixes: CHANGELOG under Unreleased, in the next dated release; no migration (the scaffold's `tex.js` refreshes on upgrade); both skills updated (facts schema reference; the syw-site skill's caption notes; the upgrade skill's note that captions change). |

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/007-captions-cite-colour/
├── spec.md
├── plan.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/syw_site/facts.py                          # citations(): cited keys → {label, year} from the .bib
src/syw_site/rules.smk                         # the .bib as an input of syw_site_facts
src/syw_site/template/docs/src/lib/tex.js      # cite forms from facts.citations; \color, \textcolor, \\
tests/fixtures/paper/src/tex/{ms.tex,bib.bib}  # cites and a .bib in real shapes
tests/fixtures/facts.json                      # citations for the site tests
tests/test_facts.py, tests/test_site.py
skills/syw-site/references/facts-schema.md, skills/syw-site/SKILL.md, skills/syw-site-upgrade/SKILL.md
CHANGELOG.md
```

**Structure Decision**: extend the existing modules; no new files besides the fixture `.bib`.

## Complexity Tracking

None.
