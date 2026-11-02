# Feature Specification: private CI preview

**Feature Branch**: `006-ci-preview`

**Created**: 2026-11-02

**Status**: Done

**Input**: A paper's docs site cannot be previewed from CI: GitHub Pages from a private personal
repository would be public. Workflow artifacts of a private repository are visible only to its
collaborators (public repositories' are public).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See a pull request's site (Priority: P1)

`syw-site preview PR [--port 8000]` downloads the site CI built for the pull request and serves it
under `/<repo>/`, as the published site will be.

**Independent Test**: with `gh` mocked: the newest successful `Docs site` run of the PR's head branch
is downloaded (`gh run download <id> -n docs-site -D docs/.syw-site/preview/<id>/dist`); the server
maps `/<repo>/` to it; no successful run gives exit 1 naming the PR.

### User Story 2 - Only private repositories upload (Priority: P1)

The workflow step `Upload a private preview` uploads `docs/dist` as `docs-site` (14 days) only when
`github.event.repository.private && steps.settings.outputs.publish != 'true'`.

**Independent Test**: workflow tests (step, condition, name, path, retention; still one Pages upload).

## Requirements *(mandatory)*

- **FR-001**: The step never runs in a public repository or when publishing.
- **FR-002**: `actions/upload-artifact` is pinned to a commit SHA.
- **FR-003**: `/` redirects to `/<repo>/`; other paths outside the base path are 404.

## Success Criteria *(mandatory)*

- **SC-001**: A private paper's pull request is viewable locally with one command.
