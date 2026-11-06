# Tasks: Captions read citations and colour as the PDF does

**Input**: [plan.md](plan.md), [spec.md](spec.md). Tests come first in each story.

## Phase 1: User Story 1 — a caption names the papers it cites (P1)

- [X] T001 [US1] Fixture: add `tests/fixtures/paper/src/tex/bib.bib` (one, two and three authors; a braced group author; accented names; "Given Family" form; an entry without a year; an uncited entry) and `\citet`/`\citep`/`\cite` uses plus `\bibliography{bib}` to `tests/fixtures/paper/src/tex/ms.tex`
- [X] T002 [US1] Tests in `tests/test_facts.py`: `citations` holds exactly the cited keys the `.bib` defines, with the label forms (one, "and", "et al."), the family name of a group or "Given Family" author, accents read, a missing year as null; a paper without `\bibliography` gives `{}`; a named `.bib` that is missing gives `{}` without failing
- [X] T003 [US1] Implement `citations()` in `src/syw_site/facts.py` and add it to `extract()`
- [X] T004 [US1] `src/syw_site/rules.smk`: the `.bib` files under `src/tex/` as inputs of `syw_site_facts`
- [X] T005 [US1] Tests in `tests/test_site.py` (`TEXT` table, `plain`) with `citations` in `tests/fixtures/facts.json`: `\citet` one/two/many authors, `\citep` single, multiple, with `[see][p. 3]` notes, `\cite`, `\citealp`, `\citeauthor`, unknown keys (a `Surname:YYYY` key read as today, another left out with no empty parentheses), alt text
- [X] T006 [US1] Implement the citation forms in `src/syw_site/template/docs/src/lib/tex.js` from `facts.citations`

## Phase 2: User Story 2 — colour and line breaks read as text (P2)

- [X] T007 [US2] Tests in `tests/test_site.py`: `{\color{gray} solid gray}`, `\textcolor{cyan}{light blue}`, `a.\\ B`
- [X] T008 [US2] Implement in `tex.js`

## Phase 3: Polish

- [X] T009 `skills/syw-site/references/facts-schema.md` (the `citations` field), `skills/syw-site/SKILL.md` and `skills/syw-site-upgrade/SKILL.md` (what captions now render)
- [X] T010 `CHANGELOG.md` under Unreleased
- [X] T011 `uv run pytest` and `uv run pytest -m site`; open the PR (squash), saying which Spec Kit steps ran

## Dependencies

T001 → T002 → T003 → T004; T005 → T006; T007 → T008; T009–T011 last.
