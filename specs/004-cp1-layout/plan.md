# Implementation Plan: what the first paper's site taught the scaffold

**Branch**: `004-cp1-layout` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

## Summary

Copy CP1's `Fig.astro`, `Webapp.astro`, `Page.astro`, `tabs.js` and `figures/[slug].astro` into the
template (they are generic: no paper-specific text); show captions and cards in the overview
template and in a site-test page; pin research-kit 20261028.0.0 and relock; update the tests, the
`syw-site` skill and the changelog.

## Constitution Check

| Principle | How this plan meets it |
|---|---|
| Bridge, not reimplementation | The layout's look stays the website's; only the scaffold's own components change. |
| Tested on real-shaped papers | Site tests assert the new tabs, labels and link rows; CI builds the example. |
| Releases and Upgrades | Scaffold change: migration note (copy the five files), `syw-site` skill updated. |

## Complexity Tracking

None.
