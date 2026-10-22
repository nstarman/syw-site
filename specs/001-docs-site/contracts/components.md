# Contract: scaffold components (`docs/src/components/`)

| component | props | renders | fails the build when |
|---|---|---|---|
| `<Var>` | `name` | the value, math via KaTeX | `name` not in `facts.variables` |
| `<Fig>` | `label`, `size?` | image(s), caption, PDF link, link to its page | `label` not in `facts.figures` |
| `<Webapp>` | `name`, `height?` | iframe of `generated/webapps/<name>/site/`, links to full page and single file | not built / not in settings |
| `<Abstract />`, `<Authors />`, `<PaperLinks />` | — | from facts / settings | — |

Pages: `index.mdx`, `figures/index.astro`, `figures/[slug].astro`, `cite.astro`; every page uses
`<SiteLayout section="/research/" repo={facts.repo}>`.
