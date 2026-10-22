# syw-site — agreed design (input to /speckit-plan)

Agreed with the author 2026-10-21/22, sections 1–5, with section 3 revised to take the layout from
npm. Testbed: `spatial-correlations-stream-convexities-paper` (private until arXiv).

## 1. The repo and the package

```
nstarman/syw-site/                    public, MIT, date-versioned (vYYYY.MM.DD, fixes .N, backported everywhere)
  pyproject.toml                      package "syw-site": depends on figkit (pinned tag); no showyourwork import
  src/syw_site/
    facts.py                          paper → facts.json (title, authors, abstract, captions, \variable values)
    rules.smk                         Snakemake rules a paper's Snakefile includes
    cli.py                            syw-site init | facts | build | serve
    template/                         the docs/ scaffold init copies into a paper repo
  skills/syw-site/, skills/syw-site-upgrade/   registered in nstarman/skills/registry/
  examples/paper/                     a minimal synthetic showyourwork paper (test fixture)
  .specify/, specs/, AGENTS.md, CHANGELOG.md
```

Boundaries: syw-site knows showyourwork's files; figkit knows webapps; the website owns the look
(`@nstarkman/site-layout`). syw-site connects them and reimplements none. Same process as figkit:
Spec Kit, CI, PR previews of the example's site, skills pinned to date tags in nstarman/skills.

## 2. What a paper repo gains, and the docs as a showyourwork output

```
docs/
  syw-site.yml        website id; arXiv id / DOI / ADS bibcode once known; webapps; publish: false
  src/pages/*.mdx     the author's prose, citing facts by name
  generated/          git-ignored build output: facts.json, figure images, built webapps
webapps/<name>/       figkit apps (index.html, widget.js, science.js, export.py)
Snakefile             + include: of syw-site's rules
```

Rules (`syw_site/rules.smk`), all writing into `docs/generated/`:
- `syw_site_facts`: reads `ms.tex` and the values behind every `\variable{output/…}` → `facts.json`:
  title, authors and affiliations, abstract; each figure's label, caption, source files; every
  `\variable` value. Inline math stays LaTeX.
- `syw_site_figures`: a web image (PNG, plus the PDF) of each figure the paper includes, from the
  PDF showyourwork already produced. No figure script runs twice.
- `syw_site_webapp_<name>`: per webapp in `syw-site.yml`: its `export.py` on the pipeline's data,
  then `figkit build` (served + single file); depends on the same data rules as the paper.
- `syw_site_all`: the target the docs build asks for.

`showyourwork build syw_site_all` builds the docs data through showyourwork's Snakemake, Zenodo cache
included. **Research**: confirm how to pass an extra target through `showyourwork build`.

Observed in the testbed: `\variable` files are a generated `%` comment line then the value with a
trailing `%`; the testbed's Snakefile already reads `ms.tex` for `\variable` paths; figures are
`\includegraphics{figures/fig_x.pdf}` inside `figure`/`figure*` with `\label{fig:…}`; authors use
AASTeX 7 `\author[orcid=…,sname=…,gname=…]{…}`. The testbed's existing `docs/` (index.md, scripts/,
figures/) moves under this: figure scripts become webapps or paper figures, `index.md` the first MDX
page.

## 3. The docs site

- Astro project in `docs/`: `astro.config.mjs` with `site: 'https://nstarkman.space'`,
  `base: '/<repo>'`; `docs/package.json` depends on `@nstarkman/site-layout` at an exact version
  (`20261022.0.0`), `remark-math`/`rehype-katex` for math; lockfile committed; Dependabot (`npm`)
  proposes layout releases.
- Every page: `<SiteLayout section="/research/" repo="<owner>/<repo>">`.

| Page | Content |
|---|---|
| `index.mdx` | title, authors, abstract (facts), overview prose, key numbers, the paper's card from the website (`/embed/<id>/`) |
| `figures/` | gallery: each figure's image, caption, PDF; interactive version where a webapp is attached |
| `figures/<label>/` | one figure: larger image, full caption, notes, embedded webapp |
| `cite/` | BibTeX and links (arXiv, journal, ADS) when known; code and data repository |

Components: `<Var name>` (a number as the PDF prints it), `<Fig label>`, `<Webapp name>` (iframe of
`webapps/<name>/`, sized to content, links to full-page and single-file), `<Abstract />`,
`<Authors />`, `<PaperLinks />`.

Build: Astro reads `docs/generated/facts.json`; built webapps and figure images are copied into the
output. Missing `facts.json` fails with "run `syw-site build`". Light/dark from the layout; figkit
apps follow the system theme.

## 4. Building, previewing, publishing

```bash
syw-site build     # showyourwork build syw_site_all, then the Astro build into docs/dist/
syw-site serve     # docs/dist/ at http://127.0.0.1:8000/<repo>/
```

`docs.yml` (added by init): every push builds the docs and fails on a broken build; deploys only when
`publish: true` in `docs/syw-site.yml`; refuses to deploy from a private repository. On arXiv day:
make the repo public, `publish: true`, Pages source = GitHub Actions. Paper releases are tags; the
site shows `main`; showyourwork's Zenodo deposit archives versions. Linking from the website card is
sub-project D.

## 5. Skills and maintenance

`skills/syw-site/SKILL.md` triggers on "add a docs site / project page / website for this paper", on
work in a showyourwork repo's `docs/`, and on syw-site. Steps: (1) pin syw-site, `syw-site init`,
fill the website record id; (2) write MDX with `<Var>`, `<Fig>`, `<Webapp>` — facts never typed in;
(3) interactive figures with the figkit skill, listed in `syw-site.yml`; (4) `syw-site build` and
`serve`, which check every reference resolves and no link leaves the base path by mistake; (5) go
public at arXiv: checklist (public repo, `publish: true`, Pages, arXiv id/DOI in `syw-site.yml`,
then sub-project D's skill). `references/`: components, `syw-site.yml`, facts schema, a worked example.

`skills/syw-site-upgrade` applies CHANGELOG migration notes, as figkit's. Both registered in
`nstarman/skills/registry/` pinned to date tags; the weekly bump job keeps them current. The testbed
gets syw-site in a PR on its repo, built locally only.
