"""`syw-site webapp` for a figpress-plotly figure: webapps/<name>/figure.py, written where the site looks."""

import argparse
import json
import shlex
import sys

from syw_site import cli

# A stand-in for figpress-plotly: `load` gives an object whose write_web records its arguments.
FAKE = '''
from pathlib import Path
class Figure:
    def __init__(self, spec): self.spec = spec
    def write_web(self, out, single_file=None):
        Path(out).mkdir(parents=True); (Path(out) / "index.html").write_text(self.spec)
        Path(single_file).write_text(self.spec)
def load(spec): return Figure(spec)
'''


def test_a_figure_py_is_written_as_page_and_single_file(tmp_path, monkeypatch):
    (tmp_path / "fake" / "figpress_plotly").mkdir(parents=True)
    (tmp_path / "fake" / "figpress_plotly" / "__init__.py").write_text("")
    (tmp_path / "fake" / "figpress_plotly" / "cli.py").write_text(FAKE)
    (tmp_path / "webapps" / "rate").mkdir(parents=True)
    (tmp_path / "webapps" / "rate" / "figure.py").write_text("")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "syw-site.yml").write_text(
        f"repo: a/b\npython: {json.dumps(shlex.quote(sys.executable))}\nwebapps:\n  rate: {{ figure: 'fig:rate' }}\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "fake"))
    assert cli.cmd_webapp(argparse.Namespace(name="rate")) == 0
    out = tmp_path / "docs" / "public" / "generated" / "webapps" / "rate"
    assert (out / "site" / "index.html").read_text() == "webapps/rate/figure.py:figure"
    assert (out / "rate.html").exists()


# A stand-in for figpress-apps: `python -m figpress_apps.cli build …` records its arguments and which python ran it.
FAKE_APPS = '''
import json, sys
from pathlib import Path
args = sys.argv[1:]
out = Path(args[args.index("--out") + 1]); out.mkdir(parents=True)
(out / "index.html").write_text(json.dumps({"args": args, "python": sys.executable}))
'''


def test_an_app_is_built_by_the_papers_python(tmp_path, monkeypatch):
    """The paper's python, which pins its figpress-apps, builds the app — not syw-site's own install."""
    (tmp_path / "fake" / "figpress_apps").mkdir(parents=True)
    (tmp_path / "fake" / "figpress_apps" / "__init__.py").write_text("")
    (tmp_path / "fake" / "figpress_apps" / "cli.py").write_text(FAKE_APPS)
    (tmp_path / "webapps" / "globe").mkdir(parents=True)
    (tmp_path / "webapps" / "globe" / "export.py").write_text(
        "import sys; from pathlib import Path; Path(sys.argv[2], 'globe').mkdir(parents=True)\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "syw-site.yml").write_text(
        f"repo: a/b\npython: {json.dumps(shlex.quote(sys.executable))}\nwebapps:\n  globe: {{ explore: true, title: G, text: g }}\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "fake"))
    assert cli.cmd_webapp(argparse.Namespace(name="globe")) == 0
    got = json.loads((tmp_path / "docs" / "public" / "generated" / "webapps" / "globe" / "site" / "index.html").read_text())
    assert got["python"] == sys.executable
    assert got["args"][:2] == ["build", "webapps/globe"]
    assert got["args"][2:4] == ["--data", "docs/.syw-site/webapps/globe/data/globe"]
