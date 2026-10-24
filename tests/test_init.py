import shutil
from pathlib import Path

import pytest

from syw_site.init import INCLUDE, InitError, init, repo_from_git

PAPER = Path(__file__).parent / "fixtures" / "paper"


@pytest.fixture
def paper(tmp_path):
    shutil.copytree(PAPER, tmp_path / "p")
    (tmp_path / "p" / "showyourwork.yml").write_text("version: 0.4.3\n")
    (tmp_path / "p" / "Snakefile").write_text("rule x:\n    output: 'a'")
    return tmp_path / "p"


def test_init_writes_the_scaffold(paper):
    written = init(paper, "nstarman/demo")
    assert Path("docs/astro.config.mjs") in written and Path(".github/workflows/docs.yml") in written
    assert Path(".github/workflows/card.yml") in written and Path("docs/scripts/card.mjs") in written
    assert "base: '/demo'" in (paper / "docs/astro.config.mjs").read_text()
    assert "repo: nstarman/demo" in (paper / "docs/syw-site.yml").read_text()
    assert "publish: false" in (paper / "docs/syw-site.yml").read_text()
    assert "public/generated/" in (paper / "docs/.gitignore").read_text()
    assert not (paper / "docs/gitignore").exists()
    assert "{{" not in (paper / ".github/workflows/docs.yml").read_text().replace("${{", "")
    snakefile = (paper / "Snakefile").read_text()
    assert snakefile.startswith("rule x:\n    output: 'a'\n") and snakefile.count(INCLUDE) == 1


def test_init_twice_changes_nothing(paper):
    init(paper, "nstarman/demo")
    before = {p: p.read_bytes() for p in paper.rglob("*") if p.is_file()}
    assert init(paper, "nstarman/demo") == []
    assert {p: p.read_bytes() for p in paper.rglob("*") if p.is_file()} == before


def test_init_refuses_to_overwrite(paper):
    (paper / "docs").mkdir()
    (paper / "docs/syw-site.yml").write_text("mine\n")
    with pytest.raises(InitError, match="docs/syw-site.yml"):
        init(paper, "nstarman/demo")
    assert (paper / "docs/syw-site.yml").read_text() == "mine\n"
    assert not (paper / "docs/astro.config.mjs").exists()  # nothing written


def test_init_needs_a_showyourwork_repo(tmp_path):
    with pytest.raises(InitError, match="not a showyourwork repository"):
        init(tmp_path, "a/b")


@pytest.mark.parametrize(
    "url", ["git@github.com:nstarman/demo.git", "https://github.com/nstarman/demo", "https://github.com/nstarman/demo.git"]
)
def test_repo_from_git(tmp_path, url):
    import subprocess

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "remote", "add", "origin", url], check=True)
    assert repo_from_git(tmp_path) == "nstarman/demo"
