"""The docs scaffold builds with a fixture facts.json, renders the paper's numbers, and stops on a
name that is not in it (FR-005). Needs Node and the network for `npm ci`; run with `-m site`."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from syw_site.init import planned

pytestmark = pytest.mark.site
HERE = Path(__file__).parent
ENV = {**os.environ, "ASTRO_TELEMETRY_DISABLED": "1"}


@pytest.fixture(scope="module")
def docs(tmp_path_factory):
    root = tmp_path_factory.mktemp("paper")
    for path, data in planned("nstarman/demo").items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(data)
    docs = root / "docs"
    (docs / "public/generated").mkdir(parents=True)
    shutil.copy(HERE / "fixtures/facts.json", docs / "public/generated/facts.json")
    shutil.copy(HERE / "site/numbers.mdx", docs / "src/pages/numbers.mdx")
    subprocess.run(["npm", "ci", "--no-audit", "--no-fund"], cwd=docs, check=True, env=ENV)
    return docs


def build(docs):
    return subprocess.run(["npx", "astro", "build"], cwd=docs, env=ENV, capture_output=True, text=True)


def test_builds_every_page(docs):
    r = build(docs)
    assert r.returncode == 0, r.stdout + r.stderr
    pages = sorted(str(p.relative_to(docs / "dist")) for p in (docs / "dist").rglob("index.html"))
    assert pages == [
        "cite/index.html", "figures/a/index.html", "figures/b/index.html", "figures/fig_c/index.html",
        "figures/index.html", "index.html", "numbers/index.html",
    ]
    html = (docs / "dist/numbers/index.html").read_text()
    assert 'href="/demo/figures/a/"' in html and 'href="/research/"' in html
    facts = json.loads((HERE / "fixtures/facts.json").read_text())
    assert facts["variables"]["forecast/gain"] == "14" and ">14<" in html
    assert "16–24" in html and "Au-1" in html  # text values; math ones go through KaTeX
    assert 'aria-current="page"' in html  # Research marked in the website's nav
    assert "λ" in html and "sgn" in html  # the paper's own macros, one with an argument, via KaTeX


def test_unknown_name_stops_the_build(docs):
    bad = docs / "src/pages/bad.mdx"
    bad.write_text("---\nlayout: ../components/Page.astro\n---\nimport Var from '../components/Var.astro';\n\n<Var name=\"nope\" />\n")
    try:
        r = build(docs)
    finally:
        bad.unlink()
    assert r.returncode != 0
    assert 'no variable "nope"' in r.stdout + r.stderr
