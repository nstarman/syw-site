import threading
import urllib.error
import urllib.request

import pytest

from syw_site.serve import make_server


@pytest.fixture
def server(tmp_path):
    (tmp_path / "index.html").write_text("home")
    (tmp_path / "figures").mkdir()
    (tmp_path / "figures" / "index.html").write_text("figs")
    srv = make_server(tmp_path, "demo", port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def get(url):
    with urllib.request.urlopen(url) as r:
        return r.read().decode()


def test_serves_under_the_base(server):
    assert get(f"{server}/demo/") == "home"
    assert get(f"{server}/demo/figures/") == "figs"


@pytest.mark.parametrize("path", ["/", "/figures/", "/index.html", "/demox/"])
def test_404_outside_the_base(server, path):
    with pytest.raises(urllib.error.HTTPError) as e:
        get(server + path)
    assert e.value.code == 404
