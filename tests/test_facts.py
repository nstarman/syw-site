from pathlib import Path

import pytest

from syw_site import facts

PAPER = Path(__file__).parent / "fixtures" / "paper"


@pytest.fixture(scope="module")
def f():
    with pytest.warns(UserWarning, match="no \\\\label"):
        return facts.extract(PAPER, repo="nstarman/example", paper={"arxiv": "2610.00001"})


def test_title_and_abstract(f):
    assert f["schema"] == 1
    assert f["title"] == "Curved Things II: Angles {Distinguish} Models"
    assert f["abstract"] == r"We find $\sim14$ times more signal. Fully 50\% of it."


def test_authors_and_affiliations(f):
    assert f["affiliations"] == ["Institute of Examples, Somewhere", "Second Place"]
    assert f["authors"] == [
        {"name": "Jane Doe", "given": "Jane", "surname": "Doe", "orcid": "0000-0001-2345-6789", "affiliations": [0, 1]},
        {"name": "Richard Roe", "given": "Richard", "surname": "Roe", "affiliations": [0]},
        {"name": "And Friends", "affiliations": []},
    ]


def test_figures(f):
    a, b, c = f["figures"]
    assert (a["label"], a["slug"]) == ("fig:a", "a")
    assert a["caption"] == "A caption with {nested} braces and $x^{2}$."
    assert a["images"] == [{"source": "src/tex/figures/fig_a.pdf", "file": "figures/fig_a.pdf", "webp": "figures/fig_a.webp", "png": "figures/fig_a.png"}]
    assert b["caption"] == "Two panels.finish"
    assert [i["file"] for i in b["images"]] == ["figures/fig_b1.pdf", "figures/fig_b2.pdf"]
    assert (c["label"], c["slug"], c["images"][0]) == (None, "fig_c", {"source": "src/tex/figures/fig_c.png", "file": "figures/fig_c.png", "webp": "figures/fig_c.webp", "png": "figures/fig_c.png"})


def test_variables(f):
    assert f["variables"] == {"forecast/gain": "14", "rate": r"$3.2 \times 10^{-4}$"}


def test_paper_and_repo(f):
    assert f["paper"] == {"arxiv": "2610.00001", "doi": None, "bibcode": None}
    assert f["repo"] == "nstarman/example"


def test_missing_variable_file_is_named(tmp_path):
    tex = tmp_path / "src" / "tex"
    tex.mkdir(parents=True)
    (tex / "ms.tex").write_text(r"\title{T}\variable{output/missing.tex}")
    with pytest.raises(FileNotFoundError, match="output/missing.tex"):
        facts.extract(tmp_path, repo="a/b")


def test_not_a_paper(tmp_path):
    with pytest.raises(FileNotFoundError, match="showyourwork"):
        facts.extract(tmp_path, repo="a/b")


def test_escaped_percent_is_not_a_comment():
    assert facts.strip_comments("50\\% done % gone") == "50\\% done "


def test_aastex6_bare_orcid():
    found, _ = facts.authors(r"\author[0000-0002-1825-009X]{Josiah Carberry}\affiliation{Brown}")
    assert found == [{"name": "Josiah Carberry", "orcid": "0000-0002-1825-009X", "affiliations": [0]}]


def test_label_and_footnote_never_show(tmp_path):
    assert facts.clean(r"A plot\footnote{aside} of $x$.\label{fig:p}") == "A plot of $x$."


def test_aastex_figure_macros(tmp_path):
    text = r"""
\begin{figure}\plotone{figures/one.pdf}\caption{One.\label{fig:one}}\end{figure}
\begin{figure}\plottwo{figures/a.pdf}{figures/b.pdf}\caption{Two.}\label{fig:two}\end{figure}
\begin{figure*}\gridline{\fig{figures/g1.pdf}{0.3\textwidth}{(a)}\fig{figures/g2.pdf}{0.3\textwidth}{(b)}}
\caption{Grid.}\label{fig:grid}\end{figure*}
\begin{figure}\caption{Nothing.}\end{figure}
"""
    with pytest.warns(UserWarning, match="no image"):
        found = facts.figures(text, tmp_path)
    assert [(f["label"], f["caption"], [i["file"] for i in f["images"]]) for f in found] == [
        ("fig:one", "One.", ["figures/one.pdf"]),
        ("fig:two", "Two.", ["figures/a.pdf", "figures/b.pdf"]),
        ("fig:grid", "Grid.", ["figures/g1.pdf", "figures/g2.pdf"]),
    ]


def test_comment_after_a_line_break():
    assert facts.strip_comments(r"a \\% gone") == r"a \\"
    assert facts.strip_comments(r"5\% kept % gone") == r"5\% kept "


def test_a_papers_own_label_command(tmp_path):
    text = r"\begin{figure}\includegraphics{figures/r.pdf}\caption{Rate.}\figlabel{fig:rate}\end{figure}"
    (f,) = facts.figures(text, tmp_path)
    assert (f["label"], f["slug"], f["caption"]) == ("fig:rate", "rate", "Rate.")
    assert facts.clean(r"See \seclabel{sec:x}this.") == "See this."


def test_macros():
    text = r"""
\newcommand{\qbarpot}{\bar{q}_\Phi}
\renewcommand{\todo}[1]{{\color{red} #1}}
\DeclareMathOperator{\sgn}{sgn}
\newcommand{\figlabel}[1]{\@bsphack x}
"""
    assert facts.macros(text) == {
        r"\qbarpot": r"\bar{q}_\Phi", r"\todo": r"{\color{red} #1}", r"\sgn": r"\operatorname{sgn}",
    }


def test_macros_from_the_papers_own_packages(tmp_path):
    """`\\usepackage{dir/name}` from src/tex/, and the modules it loads by bare name (as an
    `\\input@path` finds them); ms.tex's own definitions win."""
    tex = tmp_path / "src" / "tex"
    (tex / "preamble").mkdir(parents=True)
    (tex / "preamble" / "mine.sty").write_text("\\RequirePackage{amsmath,mine-math}\n\\newcommand{\\survey}{\\textsl{Survey}}\n")
    (tex / "preamble" / "mine-math.sty").write_text("\\RequirePackage{mine}\n\\newcommand{\\mrm}[1]{\\mathrm{#1}} % upright\n\\newcommand{\\kept}{a}\n")
    (tex / "unused.sty").write_text("\\newcommand{\\unused}{x}\n")
    (tex / "ms.tex").write_text("\\usepackage{xcolor}\n\\usepackage[opt]{preamble/mine}\n\\newcommand{\\kept}{b}\n\\title{T}\n")
    assert facts.extract(tmp_path, repo="a/b")["macros"] == {
        r"\mrm": r"\mathrm{#1}", r"\kept": "b", r"\survey": r"\textsl{Survey}",
    }


def test_slug_is_a_path_segment(tmp_path):
    text = r"\begin{figure}\includegraphics{figures/z.pdf}\caption{Z.}\label{fig:cosmology:zlr}\end{figure}"
    (f,) = facts.figures(text, tmp_path)
    assert (f["label"], f["slug"]) == ("fig:cosmology:zlr", "cosmology-zlr")
