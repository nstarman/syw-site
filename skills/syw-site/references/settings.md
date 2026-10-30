# `docs/syw-site.yml`

```yaml
repo: owner/name                 # required; written by init (sets the base path /name/)
website_id: 2026-...             # the paper's record id on nstarkman.space (its card); optional
publish: false                   # true only at arXiv submission, with the repo public
paper:                           # optional, filled in when known
  arxiv: 2610.12345
  doi: 10.3847/...
  bibcode: 2026ApJ...
python: uv run --locked python   # optional; how the paper runs Python (default: python)
webapps:                         # optional; figpress-apps apps, or figpress-plotly figure.py, in webapps/<name>/
  globe: { inputs: [src/data/directional.npz], figure: "fig:quadrupole" }   # a figure's counterpart
  rate: { inputs: [...], figure: "fig:rate", replaces: true }  # its page shows only this, not the image
  explorer: { inputs: [...], explore: true, title: "…", text: "…" }          # on the Explore tab
figures:                         # optional; where the portrait goes on each figure
  "fig:rate":   { icon: top-left }       # top-right (default) | top-left | bottom-right | bottom-left | none
  "fig:shapes": { icon: [0.82, 0.12] }   # or its centre, as fractions of width and height
  "fig:grid":   { image: 2 }             # on the figure's second image
  "fig:rate":   { icon: [top-right, [0.509, 0.134]], alpha: 0.8 }   # one per panel; opacity (default 0.8)
```

Unknown keys are errors. Webapp names are `[a-z0-9-]+` and `webapps/<name>/` must exist; inputs may
be files the pipeline makes; `figure` (optional) is a `\label` — quote it, since `fig:x` contains a colon.
`figures:` keys are labels (or slugs); `syw-site figures` re-stamps in seconds after a change.
