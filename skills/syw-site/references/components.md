# Components (`docs/src/components/`)

| component | props | renders | stops the build when |
|---|---|---|---|
| `<Var name="p" />` | `name`: the `\variable{output/p.tex}` path | the value as the PDF prints it (math via KaTeX; `\qty`, `\qtyrange`, `\num` understood) | `p` is not in `facts.variables` |
| `<Fig label="fig:x" />` | `label` (or the slug, `x`); `link` (default true) | images (or the webapp with `replaces: true` that names the figure), "Paper Figure N." and the caption, then a row of links: Open (its page, which also shows its interactive version) on the left, PDF · PNG (each named by its file when the figure has several panels; and HTML, for a replacing webapp) on the right | the label is not in `facts.figures` |
| `<Webapp name="n">Caption.</Webapp>` | `name`; `height` (px until the app loads, default 640); `full` (a site path, e.g. `"explore/"`, optional); the caption as content (optional) | the built app in an iframe sized to the app, the caption, then Open (the app's own page) and, with `full`, Full (that path) on the left, and Download HTML (one file) on the right | `n` is not under `webapps:` in `syw-site.yml` |
| `<Abstract />` | — | the abstract | — |
| `<Authors />` | — | authors (ORCID links) and numbered affiliations | — |
| `<PaperLinks />` | — | ADS, arXiv and the journal (when known), as buttons with each one's mark (the showyourwork button is on Info) | — |
| `<Card />` | — | the paper's card from nstarkman.space, when `website_id` is set | — |

Pages: `index.mdx` (overview), `figures/` (gallery: a card per figure with its short title), `figures/<slug>/` (one figure, with its webapp),
`cite/` (BibTeX once the arXiv id or DOI is known). MDX pages start with
`layout: ../components/Page.astro` (and an optional `title:`); `.astro` pages wrap themselves in
`<Page title="…">`. `Page` puts every page in the website's `<SiteLayout section="/research/">`.

LaTeX outside math is converted by `src/lib/tex.js`: `\emph`, `\textit`, `\textsl`, `\textbf`,
`\url`, dashes, `~`; `\ref` to a figure is its number and `\autoref`/`\cref` "Figure N" (to anything
else: `\ref` goes, `\autoref`/`\cref` read "the paper"; `\eqref` reads "an equation in the paper");
citations read from the paper's `.bib` (`facts.citations`): `\citet` "Doe et al. (2023)", `\citep`
"(see Doe et al. 2023, p. 3)", `\cite`/`\citealp` without the parentheses, `\citeauthor` "Doe et al.";
a key the `.bib` lacks reads from a `Surname:2023`/`Surname+:2023` key, or is dropped with no empty
parentheses; `{\color{c} text}` and `\textcolor{c}{text}` keep the text, `\\` reads as a space; siunitx (`\qty`, `\unit`, `\num`, their ranges) and
`\ensuremath` render as math; the paper's macros without arguments are expanded; other commands keep
their argument. Extend it there when a paper needs more.
