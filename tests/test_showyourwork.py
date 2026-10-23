import re
from pathlib import Path

import pytest

from syw_site import showyourwork


def test_one_showyourwork_build_for_the_paper_and_the_docs():
    cmd = showyourwork.command("/env/bin/showyourwork", 2, "mamba", ["--scheduler", "greedy"])
    assert cmd == [
        "/env/bin/showyourwork", "build", "--cores", "2", "--conda-frontend", "mamba",
        "--scheduler", "greedy", "syw__main", "syw_site_all",
    ]


def test_unsupported_version_is_refused(monkeypatch, tmp_path):
    monkeypatch.setattr(showyourwork, "executable", lambda: "showyourwork")
    monkeypatch.setattr(showyourwork, "version", lambda exe: "0.4.3")
    with pytest.raises(showyourwork.ShowyourworkError, match="0.4.3 is not supported"):
        showyourwork.build(tmp_path)


def test_rules_file_is_packaged():
    from syw_site import rules_path

    text = Path(rules_path()).read_text()
    for rule in ("syw_site_facts", "syw_site_figures", "syw_site_webapp", "syw_site_all"):
        assert f"rule {rule}:" in text
    assert not re.search(r"^\s+run:", text, re.M)  # showyourwork rejects run: in user rules
