# Implementation Plan: private CI preview

**Branch**: `006-ci-preview` | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md)

## Summary

`template/workflows/docs.yml` gains the upload step; `cli.py` gains `preview` (`gh pr view`,
`gh run list`, `gh run download`) and `preview_server`, a `ThreadingHTTPServer` whose handler strips
the `/<repo>` prefix. `gh` is the only new requirement, and only for `preview`.

## Constitution Check

| Principle | How this plan meets it |
|---|---|
| Nothing leaves before arXiv | The upload is private-only, mutually exclusive with publishing; artifacts expire in 14 days. |
| Releases and Upgrades | Template change: migration note (copy the step), `syw-site` skill updated. |

## Complexity Tracking

None.
