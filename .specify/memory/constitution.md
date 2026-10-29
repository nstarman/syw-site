# syw-site Constitution

syw-site turns a [showyourwork](https://github.com/showyourwork/showyourwork) paper repository into
a documentation site for the paper — its prose, numbers, figures and interactive figpress-apps webapps —
published at `nstarkman.space/<repo>/` and looking like that website.

## Core Principles

### I. A bridge, never a reimplementation

- syw-site connects three things it does not own: showyourwork (the paper's pipeline), figpress-apps (its
  webapps) and the website's layout (the npm package `@nstarkman/site-layout`). It MUST NOT copy or
  reimplement any of them.
- It reads a showyourwork repository's files (`showyourwork.yml`, `src/tex/ms.tex`, the generated
  `\variable` files) and MUST NOT import showyourwork as a Python package, so showyourwork's
  internals can change without breaking it.
- Rationale: each piece has one owner; syw-site stays small enough to keep working.

### II. Facts come from the paper

- Every number, caption, title, author and abstract on a docs site comes from the paper, through
  `facts.json`, which syw-site generates. Docs pages refer to facts by name and MUST NOT retype them.
- A reference to a fact, figure or webapp that does not exist MUST fail the build, never render as a
  gap.
- Rationale: the site and the PDF must never disagree.

### III. The docs are a showyourwork output

- The data a docs site needs (facts, web figures, built webapps) is produced by Snakemake rules the
  paper's Snakefile includes, so it is cached, rebuilt and archived exactly as the paper is. No
  figure script runs twice: web figures are converted from the PDFs showyourwork already made.
- Rationale: one pipeline, one source of truth, no drift.

### IV. Private until the author publishes

- A paper's docs site is local-only until the author sets `publish: true`. Nothing derived from an
  unpublished paper may be deployed, uploaded or committed to a public place before then. The
  generated workflow MUST refuse to deploy from a private repository.
- Examples and tests in this repository MUST use synthetic papers only, never a real unpublished one.
- Rationale: papers are confidential until submission.

### V. Looks like the website

- Docs sites wrap every page in `<SiteLayout>` from `@nstarkman/site-layout`, pinned to an exact
  release, with `site: 'https://nstarkman.space'` and `base: '/<repo>'`. Local preview serves under
  the same base path.
- Rationale: a reader moves between the website and a paper's site without noticing the seam.

### VI. Small, generic, earned

- syw-site contains only what is generic to showyourwork papers. Anything specific to one paper
  lives in that paper's `docs/`. Code enters syw-site only when a real paper needs it (YAGNI).

### VII. Tested on a paper's shape

- The facts extraction MUST have unit tests over real-shaped LaTeX and `\variable` files.
- `examples/` holds a minimal synthetic showyourwork paper; CI builds its docs site end to end,
  without the network beyond installing pinned dependencies.
- Rationale: a site that fails on the next paper is not a tool.

## Technology Constraints

- Python package `syw-site`, installed from git tags of `nstarman/syw-site` (not PyPI); Python ≥ 3.11;
  depends on figpress-apps at a pinned version (PyPI). The docs scaffold it installs is an Astro project with its own
  pinned `package.json` and lockfile.
- Licence: MIT.
- Agent guidance lives in `AGENTS.md` (with `CLAUDE.md` pointing to it); the skills that teach
  agents to use and upgrade syw-site live in `skills/` and are versioned with the code.

## Releases and Upgrades

- Versions are dates: a release is tagged `vYYYY.MM.DD` (Python version `YYYY.MM.DD`); a bug-fix
  release of it is `vYYYY.MM.DD.N` (N = 1, 2, …). The version number does not signal breaking
  changes; migration notes do.
- Every bug fix MUST be backported to every released version that has the bug, each on its
  `versions/<tag>.x` branch (created from the release tag when first needed) and released as that
  version's next `.N`. Bug-fix releases MUST NOT contain breaking changes or new features.
- Every release MUST have a `CHANGELOG.md` section; every breaking change a migration note (what
  changed, how to find it, the exact edit). A change to the public interface (CLI, `syw-site.yml`,
  components, facts schema, scaffold) MUST update the `syw-site` and `syw-site-upgrade` skills in
  the same pull request.

## Governance

- This constitution overrides other practices in this repository. Specs and plans MUST include a
  constitution check; any deviation MUST be justified in the plan's complexity tracking.
- Amendments are made by pull request with a version bump: MAJOR for removing or redefining a
  principle, MINOR for adding or materially expanding one, PATCH for wording.

**Version**: 1.0.1 | **Ratified**: 2026-10-22 | **Last Amended**: 2026-10-28
