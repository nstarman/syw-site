# Data model

`docs/syw-site.yml` additions:

```yaml
figures:
  "fig:rate":   { icon: top-left }        # top-right (default) | top-left | bottom-right | bottom-left | none | [x, y]
  "fig:shapes": { icon: [0.82, 0.12], image: 2 }
webapps:
  helix: { inputs: [...], explore: true, title: "The helix", text: "…" }   # or figure: "fig:…"
```

`docs/card.json`: the research-kit snapshot (schema 1; see the website's data-model). `facts.json` image
entries gain `webp` (and keep `png`, `file`).
