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
    assert re.findall(r">([\w ]+)</a>", tabs) == ["Overview", "Explore", "Paper Figures", "Cite", "Info"]
    assert 'aria-current="page"' in re.search(r'<a[^>]*>Overview</a>', tabs).group(0)
    assert 'aria-current="page"' in re.search(r'<a[^>]*>Paper Figures</a>', re.search(r'<div class="syw-tabs"[^>]*>(.*?)</div>', page(docs, "figures/a"), re.S).group(1)).group(0)


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


def js(docs, calls):
    """Each (function, *args) called in src/lib/tex.js, as Node runs it in the scaffold."""
    script = ("import * as t from './src/lib/tex.js';"
              f"console.log(JSON.stringify({json.dumps(calls)}.map(([f, ...a]) => t[f](...a))));")
    r = subprocess.run(["node", "--input-type=module", "-e", script], cwd=docs, env=ENV, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


SIUNITX = {  # siunitx → the LaTeX KaTeX renders
    r"\qty{3}{\kilo\parsec}": r"3\,\mathrm{kpc}",
    r"\qty{1.2e-10}{\meter\per\second\squared}": r"1.2\times10^{-10}\,\mathrm{m}\,{\mathrm{s}}^{-2}",
    r"\qty{2}{\per\square\centi\meter}": r"2\,{\mathrm{cm}}^{-2}",
    r"\qty{5}{\cubic\kilo\parsec}": r"5\,{\mathrm{kpc}}^{3}",
    r"\qty{4}{\giga\year}": r"4\,\mathrm{Gyr}",
    r"\qty{1}{\mega\parsec}": r"1\,\mathrm{Mpc}",
    r"\qty{7}{\milli\gram}": r"7\,\mathrm{mg}",
    r"\qty{9}{\micro\meter}": r"9\,\mu\mathrm{m}",
    r"\qty{50}{\percent}": r"50\,\%",
    r"\unit{\kilo\meter\per\second}": r"\mathrm{km}\,{\mathrm{s}}^{-1}",
    r"\num{e12}": r"10^{12}",
    r"\num{3e5}": r"3\times10^{5}",
    r"\numrange{1}{2e3}": r"1\text{--}2\times10^{3}",
    r"\qtyrange{25}{35}{\kpc}": r"25\text{--}35\,\mathrm{kpc}",
}

TEXT = [  # (tex, refs) → HTML
    (r"In \autoref{fig:a} and~\cref{fig:a}, \ref{fig:a}.", {"fig:a": "1"}, "In Figure&nbsp;1 and&nbsp;Figure&nbsp;1, 1."),
    (r"As in \cref{sec:x}. \Cref{app:y} too; (Appendix~\ref{app:y})", {}, "As in the paper. The paper too; (Appendix)"),
    (r"\autoref{sec:x} shows it.", {}, "The paper shows it."),
    (r"As \citet{Doe+:2023} and \citetalias{Roe:2020a,2019ApJ...1R} show.", {}, "As Doe et al. (2023) and Roe (2020) show."),
    (r"Known \citep[e.g.][]{Doe+:2023}, and~\citep{Roe:2020}.", {}, "Known, and."),
    (r"With \survey{} and \survey, in \kpcunit.", {}, None),  # checked below
]


def test_tex_conversion(docs):
    assert js(docs, [["siunitx", k] for k in SIUNITX]) == list(SIUNITX.values())
    *out, macro = js(docs, [["tex", s, refs] for s, refs, _ in TEXT])
    assert out == [html for _, _, html in TEXT[:-1]]
    assert macro.startswith("With <em>Survey</em> and <em>Survey</em>, in <span class=\"katex\">") and "kpc" in macro
    # In math: \ensuremath, paper macros with siunitx, an argument or \textsl in them, and siunitx.
    (html,) = js(docs, [["math", r"\ensuremath{x} + 1\,\kpcunit + \upr{d} + \qty{2}{\micro\meter} + \survey"]])
    assert 'class="katex"' in html and "kpc" in html and "Survey" in html


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
