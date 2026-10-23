---
name: syw-site-upgrade
description: Upgrade a showyourwork paper's docs site to a newer syw-site release, applying the changelog's migration notes in order, refreshing the scaffold files it owns, rebuilding and checking that the site still shows the paper's numbers. Use when asked to upgrade, bump or update syw-site, when a docs site was made with an older syw-site tag, or when `syw-site build` fails after a version change.
---

# Upgrading a syw-site docs site

A paper pins syw-site to a git tag of `nstarman/syw-site`. Versions are dates, `vYYYY.MM.DD`, with
bug-fix releases `vYYYY.MM.DD.N`; a bug-fix release of the pinned version never needs migration
notes. Every breaking change ships a **migration note** (What changed, Find, Edit). Apply them;
never guess.

## 1. Versions and a baseline

- **Current**: the `syw-site @ git+…@vX` pin in the paper's environment, or the version in the
  header of `.github/workflows/docs.yml` (`syw-site X`).
- **Target**: what the user asked for, else `gh release list -R nstarman/syw-site --limit 1`.
- Equal → report and stop.
- **Baseline**: `syw-site build && syw-site serve`; note the overview's numbers and the figure
  pages. They must be unchanged afterwards.

## 2. Read the migration notes

Install the target (`pip install "syw-site @ git+https://github.com/nstarman/syw-site@vTARGET"`),
then read its changelog, which contains every earlier release:

```bash
python -c "import syw_site, pathlib; print((pathlib.Path(syw_site.__file__).parent / 'CHANGELOG.md').read_text())"
```

Take every section after the current version up to the target, oldest first. **Stop** and report
to the user if a breaking change has no migration note.

## 3. Apply them, oldest first

For each note: run its **Find**, make its **Edit** only where it matches, re-run **Find** to
confirm. The author's pages (`docs/src/pages/`, their own components) change only as a note says.

## 4. Refresh the scaffold

Files `syw-site init` wrote and the author has not changed (compare with the old tag's
`src/syw_site/template/`) are replaced by the target's; `docs/package.json` and
`docs/package-lock.json` move to the target's pins (then `npm ci` in `docs/`); the workflow's
pinned version in `.github/workflows/docs.yml` becomes the target. A file the author changed is
merged by hand.

## 5. Rebuild and compare

`syw-site build && syw-site serve`; compare with the baseline. Report what changed, the notes
applied, and anything left for the author.
