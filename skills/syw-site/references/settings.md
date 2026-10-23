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
webapps:                         # optional; figkit apps in webapps/<name>/
  globe: { inputs: [src/data/directional.npz], figure: "fig:quadrupole" }
```

Unknown keys are errors. Webapp names are `[a-z0-9-]+` and `webapps/<name>/` must exist; inputs may
be files the pipeline makes; `figure` (optional) is a `\label` — quote it, since `fig:x` contains a colon.
