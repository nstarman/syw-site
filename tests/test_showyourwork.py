import re
from pathlib import Path

import pytest

from syw_site import showyourwork


def test_docs_command_matches_showyourwork_run_snakemake():
    cmd = showyourwork.docs_command("/env/bin/python", "/x/build.smk", 2, "mamba", ["--conda-not-block-search-path-envvars"])
    assert cmd == [
        "/env/bin/python", "-m", "snakemake", "--cores", "2", "--use-conda", "--conda-frontend", "mamba", "--cache",
        "-s", "/x/build.smk", "--conda-not-block-search-path-envvars", "syw_site_all",
    ]


def test_docs_env(tmp_path):
    env = showyourwork.docs_env(tmp_path)
    assert env["SNAKEMAKE_RUN_TYPE"] == "build"
    assert env["SNAKEMAKE_OUTPUT_CACHE"] == str(tmp_path / ".showyourwork" / "cache")


def test_interpreter_beside_the_script(tmp_path):
    (tmp_path / "env/bin").mkdir(parents=True)
    (tmp_path / "env/bin/showyourwork").touch()
    (tmp_path / "tool").symlink_to(tmp_path / "env/bin/showyourwork")  # as pipx / uv tool link it
    assert showyourwork.interpreter(str(tmp_path / "tool")) == str((tmp_path / "env/bin/python").resolve())


def test_unsupported_version_is_refused(monkeypatch, tmp_path):
    monkeypatch.setattr(showyourwork, "executable", lambda: "showyourwork")
    monkeypatch.setattr(showyourwork, "version", lambda exe: "0.5.0")
    with pytest.raises(showyourwork.ShowyourworkError, match="0.5.0 is not supported"):
        showyourwork.build(tmp_path)


def test_rules_file_is_packaged():
    from syw_site import rules_path

    text = Path(rules_path()).read_text()
    for rule in ("syw_site_facts", "syw_site_figures", "syw_site_webapp", "syw_site_all"):
        assert f"rule {rule}:" in text
    assert not re.search(r"^\s+run:", text, re.M)  # showyourwork rejects run: in user rules
