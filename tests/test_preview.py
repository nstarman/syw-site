"""`syw-site preview PR`: the newest CI-built site of a pull request, served under its base path."""

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from syw_site import cli


@pytest.fixture
def paper(tmp_path, monkeypatch):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "syw-site.yml").write_text("repo: nstarman/paper-x\n")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def fake_run(runs, calls):
    def run(argv, **kw):
        calls.append(argv)
        if argv[:3] == ["gh", "pr", "view"]:
            return CompletedProcess(argv, 0, json.dumps({"headRefName": "feat"}))
        if argv[:3] == ["gh", "run", "list"]:
            return CompletedProcess(argv, 0, json.dumps(runs))
        if argv[:3] == ["gh", "run", "download"]:
            dest = Path(argv[argv.index("-D") + 1])
            dest.mkdir(parents=True)
            (dest / "index.html").write_text("hello")
        return CompletedProcess(argv, 0, "")

    return run


class Stop(Exception):
    pass


def test_preview_downloads_newest_successful_run(paper, monkeypatch):
    calls = []
    monkeypatch.setattr(cli.subprocess, "run", fake_run([{"databaseId": 42}], calls))
    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", lambda self: (_ for _ in ()).throw(Stop))
    with pytest.raises(Stop):
        cli.main(["preview", "7", "--port", "0"])
    dist = "docs/.syw-site/preview/42/dist"
    assert ["gh", "run", "download", "42", "-n", "docs-site", "-D", dist] in calls
    assert ["gh", "run", "list", "--branch", "feat", "--workflow", "docs.yml", "--status", "success",
            "--limit", "1", "--json", "databaseId"] in calls


def test_preview_serves_under_base_path(tmp_path):
    (tmp_path / "index.html").write_text("hello")
    srv = cli.preview_server(tmp_path, "paper-x", 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    page = urllib.request.urlopen(f"{base}/paper-x/")
    assert page.read() == b"hello" and page.headers["Cache-Control"] == "no-store"  # no stale build
    assert urllib.request.urlopen(base + "/").url.endswith("/paper-x/")  # / redirects
    head = urllib.request.urlopen(urllib.request.Request(f"{base}/paper-x/", method="HEAD"))
    assert head.headers["Content-Length"] == "5" and head.read() == b""  # headers only
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(f"{base}/index.html")
    srv.shutdown()
    srv.server_close()


def test_preview_without_runs_errors(paper, monkeypatch, capsys):
    monkeypatch.setattr(cli.subprocess, "run", fake_run([], []))
    assert cli.main(["preview", "7"]) == 1
    assert "PR 7" in capsys.readouterr().err
