"""Serve docs/dist/ under its real base path, /<repo-name>/, and nothing else — so a link that
forgets the base fails here as it would at nstarkman.space/<repo-name>/."""

import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class BaseHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, base: str, **kwargs):
        self.base = base
        super().__init__(*args, **kwargs)

    def send_head(self):
        if not self.path.startswith(self.base):
            self.send_error(404, f"not under {self.base}")
            return None
        return super().send_head()

    def translate_path(self, path: str) -> str:
        return super().translate_path("/" + path[len(self.base):])


def make_server(dist: Path, name: str, port: int = 8000) -> ThreadingHTTPServer:
    handler = functools.partial(BaseHandler, directory=str(dist), base=f"/{name}/")
    return ThreadingHTTPServer(("127.0.0.1", port), handler)
