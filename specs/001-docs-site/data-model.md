# Data model

## `docs/syw-site.yml` (settings, author-written)

```yaml
website_id: 2026-xx-spatial-correlations   # the paper's record id on nstarkman.space (for /embed/<id>/)
publish: false                             # true only at arXiv submission (Principle IV)
paper:                                     # filled in when known; all optional
  arxiv: 2610.12345
  doi: 10.3847/...
  bibcode: 2026ApJ...
webapps:                                   # optional
  globe: { inputs: [src/data/directional.npz], figure: fig:quadrupole }   # figure: optional
```
Validation: unknown keys fail; `publish` boolean; webapp names `[a-z0-9-]+` with `webapps/<name>/`
present, each input a path in the repo, and `figure` (optional) a label in the paper.

## `docs/public/generated/facts.json` (generated; schema 1)

```json
{
  "schema": 1,
  "title": "LaTeX string",
  "authors": [{ "name": "…", "given": "…", "surname": "…", "orcid": "0000-…", "affiliations": [0] }],
  "affiliations": ["…"],
  "abstract": "LaTeX string",
  "figures": [{ "label": "fig:quadrupole", "slug": "quadrupole", "caption": "LaTeX",
                "images": [{ "pdf": "figures/fig_quadrupole.pdf", "png": "figures/fig_quadrupole.png" }] }],
  "variables": { "forecast/angular_gain": "14" },
  "paper": { "arxiv": null, "doi": null, "bibcode": null },
  "repo": "owner/name"
}
```
Rules: variable keys are the `\variable` path under `output/` without `.tex`; figure `slug` is the
label without `fig:` (or the file stem when unlabelled, with a warning); image paths are relative
to `generated/`. Adding an optional field keeps `schema: 1`.
