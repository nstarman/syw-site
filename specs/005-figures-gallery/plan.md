# Implementation Plan: the Figures tab as a gallery

**Branch**: `005-figures-gallery` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

## Summary

`figures/index.astro` renders cards instead of `<Fig>`s; `short()` in `lib/tex.js` finds a caption's
title (FR-001); `figures/[slug].astro` gains a back link; `Page.astro` styles the grid, cards, badge
and back link (the website's tokens). Site tests replace the one-column test.

## Constitution Check

| Principle | How this plan meets it |
|---|---|
| Bridge, not reimplementation | The website's tokens and type; no new image step (cards use the web images). |
| Tested on real-shaped papers | Site tests on the example; checked on CP1 at desktop and phone widths. |
| Releases and Upgrades | Scaffold change: migration note (copy four files), `syw-site` skill updated. |

## Complexity Tracking

None.
