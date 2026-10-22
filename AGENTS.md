# AGENTS.md

syw-site turns a showyourwork paper repository into a docs site for the paper, published at
`nstarkman.space/<repo>/` with the website's layout. Read `.specify/memory/constitution.md` first;
it overrides everything here.

## How work is done here

This repo uses [Spec Kit](https://github.com/github/spec-kit) v1.1.3 (`.specify/`, commands as
`.claude/skills/speckit-*`). A feature goes `/speckit-specify` → `/speckit-plan` → `/speckit-tasks`
→ `/speckit-implement`, in `specs/NNN-name/`. Small fixes that change no public interface go
straight to a pull request. Squash merges only.

## Boundaries

- showyourwork owns the paper's pipeline; syw-site reads its files and adds Snakemake rules, never
  imports it.
- figkit owns webapps; syw-site runs `figkit build` on them.
- The website (`nstarman/nstarman.github.io`) owns the look, released as `@nstarkman/site-layout`.

## Never

- Never put a real, unpublished paper's content in this repository, its tests, its CI logs or its
  previews. `examples/` is synthetic.

## Releasing

As figkit: dated releases `vYYYY.MM.DD`, fixes `vYYYY.MM.DD.N`, every fix backported to every
released version that has it on `versions/<tag>.x` branches created on demand; see the constitution.
