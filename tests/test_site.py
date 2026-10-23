"""The docs scaffold builds with a fixture facts.json, renders the paper's numbers, and stops on a
name that is not in it (FR-005). Needs Node and the network for `npm ci`; run with `-m site`."""

import json
import re
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
    shutil.copy(HERE / "fixtures/card.json", docs / "card.json")  # a synthetic snapshot of the website's data
    subprocess.run(["npm", "ci", "--no-audit", "--no-fund"], cwd=docs, check=True, env=ENV)
    return docs


def build(docs):
    return subprocess.run(["npx", "astro", "build"], cwd=docs, env=ENV, capture_output=True, text=True)


def test_builds_every_page(docs):
    r = build(docs)
    assert r.returncode == 0, r.stdout + r.stderr
    pages = sorted(str(p.relative_to(docs / "dist")) for p in (docs / "dist").rglob("index.html"))
    assert pages == [
        "cite/index.html", "explore/index.html", "figures/a/index.html", "figures/b/index.html",
        "figures/fig_c/index.html", "figures/index.html", "index.html", "info/index.html", "numbers/index.html",
    ]
    html = (docs / "dist/numbers/index.html").read_text()
    assert 'href="/demo/figures/a/"' in html and 'href="/research/"' in html
    facts = json.loads((HERE / "fixtures/facts.json").read_text())
    assert facts["variables"]["forecast/gain"] == "14" and ">14<" in html
    assert "16–24" in html and "Au-1" in html  # text values; math ones go through KaTeX
    assert 'aria-current="page"' in html  # Research marked in the website's nav
    assert "λ" in html and "sgn" in html  # the paper's own macros, one with an argument, via KaTeX


def page(docs, p):
    return (docs / "dist" / p / "index.html").read_text()


def test_the_card_header_and_tabs(docs):
    html = page(docs, "")
    # The website's own entry for the paper, its card without the context link.
    assert 'id="pub-demo-paper"' in html and "Curved Things II" in html
    card = re.search(r'<article class="card"[^>]*>', html).group(0)
    assert "data-context" not in card
    assert 'src="/demo/card/demo.png"' in html  # the card's image, the site's own copy
    tabs = re.search(r'<div class="syw-tabs"[^>]*>(.*?)</div>', html, re.S).group(1)
    assert re.findall(r">(\w+)</a>", tabs) == ["Overview", "Explore", "Figures", "Cite", "Info"]
    assert 'aria-current="page"' in re.search(r'<a[^>]*>Overview</a>', tabs).group(0)
    assert 'aria-current="page"' in re.search(r'<a[^>]*>Figures</a>', re.search(r'<div class="syw-tabs"[^>]*>(.*?)</div>', page(docs, "figures/a"), re.S).group(1)).group(0)


def test_figures_one_column_with_web_images(docs):
    html = page(docs, "figures")
    assert 'class="syw-figures"' in html and "syw-gallery" not in html
    assert "/demo/generated/figures/figures/fig_a.webp" in html  # shown: lossless WebP, stamped
    assert 'href="/demo/generated/figures/figures/fig_a.png" download' in html  # offered: PNG


def test_cite_lists_the_software_and_how_to_cite_it(docs):
    html = page(docs, "cite")
    assert "demopkg" in html and "Draws curves." in html
    assert "https://doi.org/10.21105/joss.00001" in html


def test_info_has_the_map_and_the_funding(docs):
    html = page(docs, "info")
    assert "Example Fellowship" in html and "Example Foundation" in html
    assert "Jane Doe" in html  # on the collaborator map


def test_explore_shows_its_webapps(docs):
    html = page(docs, "explore")
    assert "The helix" in html and "/demo/generated/webapps/helix/site/" in html


def test_without_a_website_record(docs):
    """No website_id yet: the paper's title as the header, no card, no empty Info tab."""
    facts = json.loads((HERE / "fixtures/facts.json").read_text())
    facts["website_id"] = None
    (docs / "public/generated/facts.json").write_text(json.dumps(facts))
    card = docs / "card.json"
    card.rename(docs / "card.json.off")
    try:
        r = build(docs)
        assert r.returncode == 0, r.stdout + r.stderr
        html = page(docs, "")
        assert 'class="syw-title"' in html and "pub-demo-paper" not in html
        assert ">Info</a>" not in html and not (docs / "dist/info/index.html").exists() or ">Info</a>" not in html
    finally:
        (docs / "card.json.off").rename(card)
        shutil.copy(HERE / "fixtures/facts.json", docs / "public/generated/facts.json")


# Last: a failed build leaves no dist/ for the tests above.
def test_unknown_name_stops_the_build(docs):
    bad = docs / "src/pages/bad.mdx"
    bad.write_text("---\nlayout: ../components/Page.astro\n---\nimport Var from '../components/Var.astro';\n\n<Var name=\"nope\" />\n")
    try:
        r = build(docs)
    finally:
        bad.unlink()
    assert r.returncode != 0
    assert 'no variable "nope"' in r.stdout + r.stderr
