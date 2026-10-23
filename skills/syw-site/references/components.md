# Components (`docs/src/components/`)

| component | props | renders | stops the build when |
|---|---|---|---|
| `<Var name="p" />` | `name`: the `\variable{output/p.tex}` path | the value as the PDF prints it (math via KaTeX; `\qty`, `\qtyrange`, `\num` understood) | `p` is not in `facts.variables` |
| `<Fig label="fig:x" />` | `label` (or the slug, `x`); `link` (default true) | images, "Figure N." and the caption, PDF links, a link to its page | the label is not in `facts.figures` |
| `<Webapp name="n" />` | `name`; `height` (px, default 640) | the built app in an iframe, links to the full page and the single-file download | `n` is not under `webapps:` in `syw-site.yml` |
| `<Abstract />` | — | the abstract | — |
| `<Authors />` | — | authors (ORCID links) and numbered affiliations | — |
| `<PaperLinks />` | — | arXiv, journal, ADS (when known), code and data | — |
| `<Card />` | — | the paper's card from nstarkman.space, when `website_id` is set | — |

Pages: `index.mdx` (overview), `figures/` (gallery), `figures/<slug>/` (one figure, with its webapp),
`cite/` (BibTeX once the arXiv id or DOI is known). MDX pages start with
`layout: ../components/Page.astro` (and an optional `title:`); `.astro` pages wrap themselves in
`<Page title="…">`. `Page` puts every page in the website's `<SiteLayout section="/research/">`.

LaTeX outside math is converted by `src/lib/tex.js`: `\emph`, `\textbf`, `\url`, `\ref` (to figure
numbers), dashes, `~`; citations are dropped; other commands keep their argument. Extend it there
when a paper needs more.
