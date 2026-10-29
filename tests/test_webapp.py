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
