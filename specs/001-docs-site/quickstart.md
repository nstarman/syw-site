# Quickstart: validating syw-site

1. **Unit**: `uv run pytest` — facts over TeX fixtures (AASTeX authors, `figure*`, subfigures,
   unlabelled figure, `\todo`, `\variable` values with math), settings validation, init idempotence
   and refusal to overwrite, serve's base-path mapping, adapter command line.
2. **Site**: `cd tests/site && npm ci && npx astro build` with `tests/fixtures/facts.json` — passes;
   with a page using `<Var name="nope">` — fails naming `nope`.
3. **End to end** (CI job `e2e`, or locally with showyourwork 0.4.3 + TeX):
   ```bash
   cd examples/paper && syw-site init --repo nstarman/syw-site-example && syw-site build && syw-site serve
   ```
   Open `http://127.0.0.1:8000/syw-site-example/`: title, abstract, gallery with captions, the
   webapp on its figure page; every number equals the `\variable` file (a test asserts it).
4. **Publish guard**: `docs.yml` with `publish: false` uploads nothing; with `publish: true` in a
   private repo the publish job fails (exercised by a workflow test with `act`-free shell checks of
   its conditions).
5. **Skills**: `python scripts/build_index.py --check --remote` in nstarman/skills after registering.
6. **Testbed** (local only): PR on the paper repo; `syw-site build && syw-site serve`; a page with
   `<Var>` and `<Fig>` shows the PDF's values.
