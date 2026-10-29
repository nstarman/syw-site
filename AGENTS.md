# AGENTS.md

syw-site turns a showyourwork paper repository into a docs site for the paper, published at
`nstarkman.space/<repo>/` with the website's layout. Read `.specify/memory/constitution.md` first;
it overrides everything here.

## How work is done here

This repo uses [Spec Kit](https://github.com/github/spec-kit) v1.1.3 (`.specify/`, commands as
`.claude/skills/speckit-*`). A feature goes `/speckit-specify` → `/speckit-plan` → `/speckit-tasks`
→ `/speckit-implement`, in `specs/NNN-name/`. Small fixes that change no public interface go
straight to a pull request. Squash merges only; the required check is **CI Pass**.

## Layout

```
src/syw_site/
  facts.py           ms.tex + \variable files → facts (a scanner for the commands papers use)
  settings.py        docs/syw-site.yml
  figures.py         figure PDFs → PNG (pypdfium2)
  showyourwork.py    the only code that knows how showyourwork runs (see below)
  init.py, cli.py     (`serve` is `astro preview`, which serves only under the base path)
  rules.smk          the Snakemake rules a paper includes
  template/docs/     the Astro scaffold `init` copies ({{REPO}}, {{NAME}}, {{VERSION}} filled in;
                     `gitignore` becomes `.gitignore`); template/workflows/docs.yml
skills/              syw-site, syw-site-upgrade (registered in nstarman/skills)
examples/paper/      a synthetic showyourwork paper (from showyourwork's cookiecutter) with a webapp
tests/               pytest; fixtures/paper (TeX shapes), fixtures/facts.json, e2e_check.py
```

## Boundaries

- showyourwork owns the paper's pipeline; syw-site reads its files and adds Snakemake rules, never
  imports it. figpress-apps owns webapps (`figpress-apps build`). The website owns the look
  (`@nstarkman/site-layout`, pinned exactly in `template/docs/package.json`).
- `syw-site build` is one `showyourwork build … syw__main syw_site_all` (`showyourwork.py`): the
  PDF and the docs data. Building a target from the paper's Snakefile needs showyourwork main
  (`0.4.4.dev*`; showyourwork#690 — 0.4.3 fails in preprocessing). CI pins commit 44d15103f.
- showyourwork forbids `run:` in user rules and runs each in the paper's conda env, so the rules
  call syw-site through the absolute interpreter that included them, and do all their reading in
  input functions — a broken docs/ never breaks the paper's PDF build.

## Testing

```bash
uv run pytest                 # unit tests
uv run pytest -m site         # builds the Astro scaffold with fixtures/facts.json (Node, npm)
```

CI's `e2e` job builds `examples/paper` end to end (conda, showyourwork, TeX) and runs
`tests/e2e_check.py`. Locally: a Python 3.12 venv with showyourwork at 44d15103f and `pip install -e .`,
conda on PATH; copy the example into a git repo, `syw-site init`, add the webapp to
`docs/syw-site.yml` (see ci.yml), `syw-site build`. On Apple silicon, Snakemake's default ILP
scheduler may fail to start its x86 solver: add `-- --scheduler greedy`.

## Never

- Never put a real, unpublished paper's content in this repository, its tests, its CI logs or its
  previews. `examples/` is synthetic.

## Releasing

Versions are dates: `vYYYY.MM.DD` (`__version__ = "YYYY.MM.DD"`), fixes `vYYYY.MM.DD.N`. Every bug
fix is backported to every released version that has it, on `versions/<tag>.x` branches created
from the tag when first needed (the procedure is figpress-apps' AGENTS.md "Releasing"). A release: set
`__version__`, turn `## Unreleased` in `CHANGELOG.md` into `## YYYY.MM.DD — YYYY-MM-DD` (migration
notes for breaking changes), squash-merge, tag the merge commit, `gh release create`. CI checks the
tag against `__version__`. Public-interface changes update both skills in the same pull request.
