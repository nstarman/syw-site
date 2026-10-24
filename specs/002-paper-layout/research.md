# Research: paper layout

## R1 `syw-site card` runs the resolver in Node
- **Decision**: `@nstarkman/data-resolver` is JS, so `syw-site card` runs a small script shipped in the
  scaffold (`docs/scripts/card.mjs`) with `node`, in `docs/` (where `node_modules` has research-kit):
  `collect(website_id, fromGitHub({repo: "nstarman/nstarman.github.io", ref: "main"}))` → `docs/card.json`;
  then it downloads the root's highlight image and `cv/assets/portrait.jpg` from the same commit
  (`raw.githubusercontent.com/<repo>/<sha>/…`) into `docs/public/card/` and `docs/portrait.jpg`.
- **Rationale**: one resolver; the build stays offline (it reads only the committed snapshot).

## R2 The store alias on a paper site
- **Decision**: `astro.config.mjs` aliases `@nstarkman/research-store` → `docs/src/lib/store.js`, which is
  `createStore(card.json)`; missing `card.json` throws "run `syw-site card`". Highlight image paths in the
  snapshot (`highlights/…`) are served from `docs/public/card/` (the store gets the base-path prefix).

## R3 Tabs
- **Decision**: pages `index.mdx`, `explore.astro`, `figures/index.astro`, `figures/[slug].astro`,
  `cite.astro`, `info/index.astro` (+ `info/*.mdx|astro`, the author's); `Page.astro` gets `tab` and renders
  the bar from what exists (explore: webapps with `explore: true`; info: map/funding/pages present).
  Pill style: the site's `.toolsbtn`-like classes from `site.css` (no new CSS beyond layout).

## R4 Stamping the icon
- **Decision**: Pillow: circle mask of the portrait at `d = max(48, round(0.07·W))` px, 2-px white ring,
  margin `0.02·W`; corners or fractional centre `[x, y]`; written as lossless WebP (`method=6`) and PNG.
  The rule's inputs gain `docs/portrait.jpg` and `docs/syw-site.yml`, so changing a position re-stamps.
  `facts.json` images gain `webp`.

## R5 Example and CI without the website
- **Decision**: `examples/paper` ships a fixture `docs/card.json` (a synthetic item, not a real record)
  and a synthetic portrait; CI never runs `syw-site card` against GitHub; a unit test runs `card.mjs` with a
  fake reader.

## R6 Release
- **Decision**: a feature release, the next date (`vYYYY.MM.DD`); pins `@nstarkman/research-kit` exactly;
  upgrade note for initialised papers (add `card.json`, move extra pages to `info/`, add `card.yml`).
