# `docs/public/generated/facts.json` (schema 1)

Written by `syw-site facts` (Snakemake rule `syw_site_facts`) from `src/tex/ms.tex`, the
`\variable` files and `docs/syw-site.yml`. Never edit it; change the paper.

```json
{
  "schema": 1,
  "title": "LaTeX",
  "authors": [{ "name": "…", "given": "…", "surname": "…", "orcid": "0000-…", "affiliations": [0] }],
  "affiliations": ["…"],
  "abstract": "LaTeX, with \\variable values filled in",
  "figures": [{ "label": "fig:x", "slug": "x", "caption": "LaTeX",
                "images": [{ "source": "src/tex/figures/x.pdf", "file": "figures/x.pdf", "png": "figures/x.png" }] }],
  "variables": { "forecast/angular_gain": "14" },
  "paper": { "arxiv": null, "doi": null, "bibcode": null },
  "repo": "owner/name",
  "website_id": null,
  "webapps": { "globe": { "figure": "fig:x" } }
}
```

- Authors: AASTeX 7 `\author[orcid=…,sname=…,gname=…]{…}` or AASTeX 6 `\author[ORCID]{…}`, each
  followed by its `\affiliation{}`s. `\todo{x}` becomes `x`.
- Figures: every `figure`/`figure*` with an `\includegraphics`; all its images; the first
  `\caption` and `\label`. Unlabelled figures get their first file's stem as slug (with a warning).
- Variables: key = the `\variable{output/<key>.tex}` path; value = the file without `%` comments.
- Adding an optional field keeps `schema: 1`.
