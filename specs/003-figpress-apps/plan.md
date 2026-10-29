# Implementation Plan: build webapps with figpress-apps

**Branch**: `003-figpress-apps` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

## Summary

Swap the dependency (`figkit @ git+…@v0.2.0` → `figpress-apps==2026.10.28`; the direct-reference
setting goes with it), the import in `cmd_webapp`, and the names in the example app, docs, skills and
constitution; relock; add the migration note.

## Constitution Check

| Principle | How this plan meets it |
|---|---|
| Bridge, not reimplementation | Still calls the webapp tool's CLI; nothing copied. |
| Technology Constraints | Amended wording: figpress-apps at a pinned version (PyPI). 1.0.0 → 1.0.1. |
| Releases and Upgrades | Breaking for papers with figkit apps: migration note; `syw-site` skill updated. |

## Complexity Tracking

| Deviation | Why |
|---|---|
| Released as `v2026.10.28.1`, though `.N` is for bug fixes | The maintainer chose a release the same day so the first paper (CP1) can move to figpress-apps now; the migration note is in the changelog as for any breaking release. |
