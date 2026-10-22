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
    assert f["abstract"] == r"We find $\sim\variable{output/forecast/gain.tex}$ times more signal. Fully 50\% of it."


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
    assert a["images"] == [{"source": "src/tex/figures/fig_a.pdf", "file": "figures/fig_a.pdf", "png": "figures/fig_a.png"}]
    assert b["caption"] == "Two panels.finish"
    assert [i["file"] for i in b["images"]] == ["figures/fig_b1.pdf", "figures/fig_b2.pdf"]
    assert (c["label"], c["slug"], c["images"][0]) == (None, "fig_c", {"source": "src/tex/figures/fig_c.png", "file": "figures/fig_c.png"})


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
