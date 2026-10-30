# Components (`docs/src/components/`)

| component | props | renders | stops the build when |
|---|---|---|---|
| `<Var name="p" />` | `name`: the `\variable{output/p.tex}` path | the value as the PDF prints it (math via KaTeX; `\qty`, `\qtyrange`, `\num` understood) | `p` is not in `facts.variables` |
| `<Fig label="fig:x" />` | `label` (or the slug, `x`); `link` (default true) | images, "Paper Figure N." and the caption, then a row of links: Interactive · More (its page) on the left, PDF · PNG on the right | the label is not in `facts.figures` |
| `<Webapp name="n">Caption.</Webapp>` | `name`; `height` (px until the app loads, default 640); the caption as content (optional) | the built app in an iframe sized to the app, the caption, then More (the full page) on the left and Download HTML (one file) on the right | `n` is not under `webapps:` in `syw-site.yml` |
| `<Abstract />` | — | the abstract | — |
| `<Authors />` | — | authors (ORCID links) and numbered affiliations | — |
| `<PaperLinks />` | — | arXiv, journal, ADS (when known), code and data | — |
| `<Card />` | — | the paper's card from nstarkman.space, when `website_id` is set | — |

Pages: `index.mdx` (overview), `figures/` (gallery: a card per figure with its short title), `figures/<slug>/` (one figure, with its webapp),
`cite/` (BibTeX once the arXiv id or DOI is known). MDX pages start with
`layout: ../components/Page.astro` (and an optional `title:`); `.astro` pages wrap themselves in
`<Page title="…">`. `Page` puts every page in the website's `<SiteLayout section="/research/">`.

LaTeX outside math is converted by `src/lib/tex.js`: `\emph`, `\textit`, `\textsl`, `\textbf`,
`\url`, dashes, `~`; `\ref` to a figure is its number and `\autoref`/`\cref` "Figure N" (to anything
else: `\ref` goes, `\autoref`/`\cref` read "the paper"); `\citet{Surname+:2023}` reads "Surname et
al. (2023)", other citations are dropped; siunitx (`\qty`, `\unit`, `\num`, their ranges) and
`\ensuremath` render as math; the paper's macros without arguments are expanded; other commands keep
their argument. Extend it there when a paper needs more.
