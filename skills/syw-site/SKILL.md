---
name: syw-site
description: Add and maintain a docs site (project page) for a showyourwork paper with syw-site — the paper's numbers, figures and interactive figpress-apps webapps, built by the paper's own pipeline and published at nstarkman.space/<repo>/ with the website's layout, local-only until arXiv. Use when asked for a docs site, project page or website for a paper, when working in a showyourwork repository's docs/ folder, or when a repository uses syw-site.
---

# A docs site for a showyourwork paper

syw-site adds `docs/` (an Astro site) to a showyourwork paper. The paper's own pipeline writes
`docs/public/generated/facts.json` (title, authors, abstract, figures with captions, every
`\variable` value), web images of its figures and its figpress-apps webapps; the site renders them inside
the nstarkman.space layout. **Facts come from the paper: never type a number, caption or author
into a page.** A name that does not exist stops the build.

## 1. Set up

1. Pin syw-site in the environment that runs showyourwork (showyourwork's main branch,
   `0.4.4.dev*`; the author's is the `showyourwork-main` conda env):
   `pip install "syw-site @ git+https://github.com/nstarman/syw-site@vYYYY.MM.DD"` (latest:
   `gh release list -R nstarman/syw-site --limit 1`).
2. In the repository root: `syw-site init` (or `--repo owner/name` if `origin` is not GitHub). It
   writes `docs/`, `docs/syw-site.yml` with `publish: false`, a guarded `include:` of syw-site's
   rules at the end of the `Snakefile` (the paper still builds where syw-site is not installed), and
   `.github/workflows/docs.yml`. Install syw-site in the same environment as showyourwork, or the docs
   rules stay off. It refuses to overwrite an existing file and says
   which: move that file aside (an old `docs/` becomes the content of the new pages) and rerun.
3. Fill in `docs/syw-site.yml` ([references/settings.md](references/settings.md)): `website_id`
   (the paper's record id on nstarkman.space), and `python:` if the paper runs scripts with e.g.
   `uv run --locked python`.
4. `syw-site card` (needs the network): fetches the paper's entry as nstarkman.space has it —
   `docs/card.json`, the card's images, the author's portrait — and commit them. Every page then
   opens with the website's own entry for the paper (the research card, without "Context"), and the
   `Card` workflow refreshes it weekly or by hand. Without a `website_id`, pages open with the
   paper's title and authors instead.

The site's tabs: **Overview** (`index.mdx`, your prose), **Explore** (webapps with `explore: true`),
**Figures** (every figure, one column, the author's portrait stamped top-right — place it per figure
with `figures:` in `syw-site.yml`; each is "Paper Figure N", to tell it from the site's interactive
figures), **Info** (the co-authors' map, the grants that funded it — the paper's `refs` on the website —
and your own pages in `src/pages/info/`), **Cite** (BibTeX, and the software the paper used with how to
cite it). A tab with nothing in it is hidden.

## 2. Write pages

Pages are MDX in `docs/src/pages/` (`index.mdx` is the overview). Use the components
([references/components.md](references/components.md)):

```mdx
import Var from '../components/Var.astro';
import Fig from '../components/Fig.astro';

The forecast gains a factor of <Var name="forecast/angular_gain" /> (<Fig label="fig:forecast" />).
```

`<Var name>` is the `\variable{output/<name>.tex}` path. `<Fig label>` is the figure's `\label`.
Inline math is `$…$`. Check names against `docs/public/generated/facts.json`
([references/facts-schema.md](references/facts-schema.md)).

## 3. Interactive figures

Build the app with the figpress-apps skill in `webapps/<name>/` (its `export.py` takes `--out DIR`). List
it with the data files it reads and the figure it belongs to:

```yaml
webapps:
  globe: { inputs: [src/data/directional.npz], figure: "fig:quadrupole" }
```

It is embedded on that figure's page; elsewhere use `<Webapp name="globe">Caption.</Webapp>` (the
caption is optional; the frame takes the app's height). In the overview, set a figure or an app apart
from the prose in a card:

```mdx
<div class="syw-card">
  <Webapp name="globe" height={650}>What to do with it, and what it shows.</Webapp>
</div>
```

## 4. Build and check

```bash
syw-site build --cores 4          # the paper, then the docs data, then the site; extra flags after --
syw-site serve                    # http://127.0.0.1:8000/<repo>/
```

`build` fails on an unknown `<Var>`, `<Fig>` or `<Webapp>` name, or a missing `facts.json`. `serve`
answers only under `/<repo>/`, so a link that forgets the base path fails here as it would live.
Open the overview, the figure gallery, each figure page and the cite page, and compare numbers
with the PDF.

## 5. Go public — at arXiv submission only

Until then, nothing leaves the machine or CI: never set `publish: true`, never make the repository
public, never paste the paper's content anywhere public. At submission, with the author:

1. Make the repository public.
2. In `docs/syw-site.yml`: `publish: true`, and `paper: { arxiv: … }` (later `doi`, `bibcode`).
3. Repository → Settings → Pages → Source: GitHub Actions.
4. Push to `main`; `docs.yml` deploys to `nstarkman.space/<repo>/`.
5. Link the paper's card on nstarkman.space to the site (the website's own skill).

The workflow refuses to deploy while the repository is private.

## Upgrading

To move to a newer syw-site, use the `syw-site-upgrade` skill.
