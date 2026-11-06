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
    shutil.copy(HERE / "site/cards.mdx", docs / "src/pages/cards.mdx")
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
        "cards/index.html", "cite/index.html", "explore/index.html", "figures/a/index.html", "figures/b/index.html",
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
    assert re.findall(r">([\w ]+)</a>", tabs) == ["Overview", "Explore", "Figures", "Info", "Cite"]
    assert 'aria-current="page"' in re.search(r'<a[^>]*>Overview</a>', tabs).group(0)
    assert 'aria-current="page"' in re.search(r'<a[^>]*>Figures</a>', re.search(r'<div class="syw-tabs"[^>]*>(.*?)</div>', page(docs, "figures/a"), re.S).group(1)).group(0)


def test_figures_gallery(docs):
    """The Figures tab: a card per figure (image, number, the caption's short title) opening its page;
    Interactive only where a webapp names the figure; no full captions or downloads."""
    html = re.search(r'<div class="syw-gallery">(.*?)</div>', page(docs, "figures"), re.S).group(1)
    cards = re.findall(r'<a class="syw-gallery-item"[^>]*href="([^"]+)"(.*?)</a>', html, re.S)
    assert [href for href, _ in cards] == ["/demo/figures/a/", "/demo/figures/b/", "/demo/figures/fig_c/"]
    a, b, c = (body for _, body in cards)
    assert "/demo/generated/figures/figures/fig_a.thumb.webp" in a  # the small web image
    assert "A caption with" in a and "Paper Figure 1" in a
    assert "Two panels" in b and "side by side" not in b and "More text" not in b  # an emph title, cut
    assert "Mock view of" in c and "katex" in c and "the rest" not in c  # math kept whole, cut at the colon
    assert "Interactive" in b and "Interactive" not in a + c  # rate replaces Figure 2
    assert "fig_b2.webp" not in html and "<figcaption" not in html and "download" not in html


def test_figure_page_links_back(docs):
    for slug in ("a", "b", "fig_c"):
        html = page(docs, f"figures/{slug}")
        assert f'class="syw-back" href="/demo/figures/#{slug}"' in html  # back to its card
        assert f'class="syw-gallery-item" id="{slug}"' in page(docs, "figures")
        assert html.index("syw-back") < html.index('class="syw-heading"')  # above the title


def links(html):
    """Each `fig-links` row: (left links, right links), by their text."""
    rows = re.findall(r'<div class="fig-links"[^>]*>\s*<span[^>]*>(.*?)</span>\s*<span[^>]*>(.*?)</span>', html, re.S)
    return [tuple(re.findall(r">([\w .]+)</a>", side) for side in row) for row in rows]


def test_paper_figures_and_their_links(docs):
    html = page(docs, "figures/a")
    assert "<title>Paper Figure 1" in html and "<strong>Paper Figure 1.</strong>" in html
    assert 'alt="Paper Figure 1: A caption with nested braces and x^{2}."' in html  # the caption as text
    assert links(page(docs, "numbers")) == [(["Open"], ["PDF", "PNG"])]


def test_a_webapp_that_replaces_its_figure(docs):
    """`replaces: true`: the figure's page shows the webapp instead of the image, keeping the caption
    and downloads; another figure's page, and the gallery, keep their images."""
    html = page(docs, "figures/b")
    assert "/demo/generated/webapps/rate/site/" in html
    assert "fig_b1.webp" not in html and "fig_b2.webp" not in html
    assert "<strong>Paper Figure 2.</strong>" in html
    assert "fig_a.webp" in page(docs, "figures/a")
    assert "fig_b1.thumb.webp" in page(docs, "figures")  # its card in the gallery
    # One row of links, under the caption: the app's HTML with the figure's downloads, and no Open
    # (the page already shows the app).
    rows = links(html)
    assert len(rows) == 1 and rows[0][0] == [] and rows[0][1][0] == "HTML" and "fig_b1.pdf" in rows[0][1], rows
    assert 'href="/demo/generated/webapps/rate/rate.html" download>HTML</a>' in html


def test_captioned_webapp_in_a_card(docs):
    html = page(docs, "cards")
    assert html.count('class="syw-card"') == 3
    assert "A helix to turn." in html and "data-fit" in html
    # Open: the item's own page, once. Full: `full="explore/"` on the Webapp. Figure 2 (two panels)
    # shows rate, the webapp that replaces it, in place of its images, with its HTML in the downloads.
    assert links(html) == [(["Open", "Full"], ["HTML"]), (["Open"], ["PDF", "PNG"]), (["Open"], ["HTML", "fig_b1.pdf", "fig_b2.pdf", "fig_b1.png", "fig_b2.png"])]
    assert "/demo/generated/webapps/rate/site/" in html and "fig_b1.webp" not in html
    assert 'href="/demo/explore/">Full</a>' in html
    assert html.count(">Download <a") == 3  # the word once per row, each format its own link


def test_cite_lists_the_software_and_how_to_cite_it(docs):
    html = page(docs, "cite")
    assert "demopkg" in html and "Draws curves." in html
    assert "https://doi.org/10.21105/joss.00001" in html


def test_cite_links_and_bibtex(docs):
    """The paper's links as buttons, each its mark and its name; the BibTeX on a panel with Copy."""
    html = page(docs, "cite")
    row = re.search(r'<p class="syw-links"[^>]*>(.*?)</p>', html, re.S).group(1)
    buttons = re.findall(r'<a class="syw-linkbtn"[^>]*href="([^"]+)"[^>]*>.*?<use href="#i-(\w+)".*?</svg>([^<]+)</a>', row, re.S)
    assert buttons == [("https://arxiv.org/abs/2610.00001", "arxiv", "arXiv")]  # showyourwork's is on Info
    assert re.search(r'<div class="bibtex syw-bibtex"[^>]*><button type="button" class="bibcopy"[^>]*>Copy</button><pre[^>]*>@article\{', html)


def test_cite_copies_each_packages_bibtex(docs):
    """Software: a Copy BibTeX on each package's Cite line; the entries are kept in data-bib,
    without their abstracts, not shown."""
    html = page(docs, "cite")
    assert "This paper used these software packages." in html
    bibs = re.findall(r'<button type="button" class="syw-copybib[^"]*" data-bib="([^"]*)"', html)
    assert re.search(r"Cite: .*?joss\.00001</a>\)\s*<button[^>]*syw-copybib--sm", html, re.S)  # on the Cite line
    assert len(bibs) == 1 and bibs[0].startswith("@article{") and "joss.00001" in bibs[0] and "abstract" not in bibs[0]


def test_the_card_drops_the_link_to_this_site(docs):
    """The paper's entry keeps its showyourwork button but not its link to this very site."""
    html = page(docs, "")
    assert 'href="https://github.com/nstarman/demo"' in html and 'href="#i-syw"' in html
    assert not re.search(r'<a [^>]*href="https://nstarkman.space/demo/"', html)  # (the page's canonical <link> keeps it)


def test_info_has_reproduce_the_map_and_the_funding(docs):
    """Info: the showyourwork button, then the collaborator map, then the paper's funding."""
    html = page(docs, "info")
    assert 'href="https://github.com/nstarman/demo"' in html and 'href="#i-syw"' in html
    assert "Jane Doe" in html  # on the collaborator map
    funders = re.findall(r'<li class="syw-funder"[^>]*>(.*?)</li>', html, re.S)
    text = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", f)).strip() for f in funders]
    assert text == ["Example Foundation Example Fellowship EX-1 N. Starkman", "Other Council Big Grant"], text
    assert html.index("Reproduce this paper") < html.index("Collaborators") < html.index("Funding")


def test_explore_shows_its_webapps(docs):
    html = page(docs, "explore")
    assert "The helix" in html and "/demo/generated/webapps/helix/site/" in html


def test_without_a_website_record(docs):
    """No website_id yet: the paper's title as the header, no card; Info has only the showyourwork button."""
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
        info = page(docs, "info")
        assert "Reproduce this paper" in info and "Funding" not in info and "Collaborators" not in info
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
    r"\qty{50}{\unit{\kilo\parsec}}": r"50\,\mathrm{kpc}",  # a unit macro, expanded in running text
}

TEXT = [  # (tex, refs) → HTML
    (r"In \autoref{fig:a} and~\cref{fig:a}, \ref{fig:a}.", {"fig:a": "1"}, "In Figure&nbsp;1 and&nbsp;Figure&nbsp;1, 1."),
    (r"As in \cref{sec:x}. \Cref{app:y} too; (Appendix~\ref{app:y})", {}, "As in the paper. The paper too; (Appendix)"),
    (r"\autoref{sec:x} shows it.", {}, "The paper shows it."),
    (r"Not the amplitude (\cref{app:y}).", {}, "Not the amplitude (see the paper)."),
    (r"Macros satisfy \eqref{eq:x}.", {}, "Macros satisfy an equation in the paper."),
    (r"A bound (\eqref{eq:x}).", {}, "A bound (see the paper)."),
    (r"From Eq.~\eqref{eq:x} and Eqs.~\eqref{eq:x}", {}, "From an equation in the paper and an equation in the paper"),
    (r"Equation \eqref{eq:x}. Then", {}, "An equation in the paper. Then"),
    (r"Bounded by~\eqref{eq:x}.", {}, "Bounded by an equation in the paper."),
    (r"As \citet{Doe+:2023} and \citetalias{Roe:2020a,2019ApJ...1R} show.", {}, "As Doe et al. (2023) and Roe (2020) show."),
    (r"Known \citep[e.g.][]{Doe+:2023}, and~\citep{Roe:2020}.", {}, "Known (e.g. Doe et al. 2023), and&nbsp;(Roe 2020)."),
    # Keys from the paper's .bib (facts.citations), in natbib's forms.
    (r"Figure 1 of \citet{smith2020} with", {}, "Figure 1 of Smith et al. (2020) with"),
    (r"(\citet{lee2018} as revised in \citet{smith2020})", {}, "(Lee et al. (2018) as revised in Smith et al. (2020))"),
    (r"Known \citep{solo2019}. Two \citep{solo2019,pair2017}.", {}, "Known (Solo 2019). Two (Solo 2019; Doe and Roe 2017)."),
    (r"Notes \citep[see][p.~3]{solo2019}; post \citep[ch.~2]{solo2019}.", {}, "Notes (see Solo 2019, p.&nbsp;3); post (Solo 2019, ch.&nbsp;2)."),
    (r"Bare \cite{solo2019} and \citealp{pair2017}; by \citeauthor{pair2017}.", {}, "Bare Solo 2019 and Doe and Roe 2017; by Doe and Roe."),
    (r"No year \citet{noyear}. Gone \citep{nowhere}, kept.", {}, "No year Nobody. Gone, kept."),
    (r"By \citet{amp2021}.", {}, "By Smith &amp; &lt;Co&gt; (2021)."),  # a .bib label is escaped
    # Colour names and line breaks read as text.
    (r"The {\color{gray} solid gray} region and \textcolor{cyan}{light blue}.", {}, "The solid gray region and light blue."),
    (r"Regions.\\ Objects", {}, "Regions. Objects"),
    (r"With \survey{} and \survey, in \kpcunit.", {}, None),  # checked below
]


def test_tex_conversion(docs):
    assert js(docs, [["siunitx", k] for k in SIUNITX]) == list(SIUNITX.values())
    *out, macro = js(docs, [["tex", s, refs] for s, refs, _ in TEXT])
    assert out == [html for _, _, html in TEXT[:-1]]
    assert macro.startswith("With <em>Survey</em> and <em>Survey</em>, in <span class=\"katex\">") and "kpc" in macro
    (q,) = js(docs, [["tex", r"At \qty{50}{\kpcunit}."]])  # \kpcunit is \unit{\kilo\parsec}
    assert "kpc" in q and "unit" not in q
    # An image's alt: the caption as the page reads it, as plain text.
    (alt,) = js(docs, [["plain", r"Seen from above, $r = 1$, \$5, \qty{50}{\kpcunit} \& more, as in Figure~\ref{fig:a} and \eqref{eq:x} (\citet{Doe+:2023}).", {"fig:a": "1"}]])
    assert alt == "Seen from above, r = 1, $5, 50 kpc & more, as in Figure 1 and an equation in the paper (Doe et al. (2023)).", alt
    assert js(docs, [["plain", r"$a$$b$ and $$c$$."]]) == ["ab and c."]  # each $ or $$ closes its own
    assert js(docs, [["plain", r"Costs $x = \$5$."]]) == [r"Costs x = \$5."]  # \$ inside math
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
