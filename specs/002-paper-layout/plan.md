# Implementation Plan: paper layout

**Branch**: `002-paper-layout` | **Date**: 2026-10-23 | **Spec**: [spec.md](spec.md)

## Summary

Snapshot the paper's card data with `syw-site card` (the website's resolver, run in Node, reading GitHub);
render the Research-page entry as the header from it through `@nstarkman/research-kit`; five tab pages;
figures in one column, stamped with the portrait as WebP + PNG; Cite with software citations; Info with the
map and funding; a weekly/manual refresh workflow. See [research](research.md).

## Technical Context

**Language/Version**: Python ≥ 3.11; Astro 7 scaffold; Node for `syw-site card`
**Primary Dependencies**: Pillow (WebP), `@nstarkman/research-kit` (pinned)
**Testing**: pytest (unit, `-m site`), e2e on the example
**Constraints**: build offline; examples synthetic (Principle IV); facts never retyped (Principle II)
**Depends on**: research-kit released (website 002)

## Constitution Check

| Principle | Check | Status |
|---|---|---|
| I Bridge | the card and map come from the website's packages, not reimplemented | ✅ |
| II Facts from the paper | figures/captions/numbers still from facts.json; card facts from the website's data | ✅ |
| III SYW output | stamping in the figures rule | ✅ |
| IV Private | `syw-site card` only reads public website data; example synthetic | ✅ |
| V Looks like the website | header is the website's own component | ✅ |
| VI Small | tabs are pages; no client JS | ✅ |
| VII Tested | stamping, tabs, snapshot loading tested | ✅ |

## Structure

```text
src/syw_site/card.py          syw-site card (runs docs/scripts/card.mjs, downloads images)
src/syw_site/figures.py       + stamp(), WebP
src/syw_site/settings.py      + figures:, explore/title/text
template/docs/src/lib/store.js, scripts/card.mjs, components/{Page,TabBar,Header}.astro
template/docs/src/pages/{index.mdx, explore.astro, figures/, cite.astro, info/index.astro}
template/workflows/card.yml
examples/paper/docs/card.json (fixture), portrait
```

## Complexity Tracking

None.
