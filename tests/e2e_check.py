"""Checks a built example site (CI job e2e): every page, every number as the paper has it (SC-002),
and the webapp. Usage: python tests/e2e_check.py <paper repo>"""

import json
import re
import sys
from pathlib import Path

paper = Path(sys.argv[1])
dist = paper / "docs/dist"
facts = json.loads((paper / "docs/public/generated/facts.json").read_text())

pages = {str(p.relative_to(dist)) for p in dist.rglob("index.html")}
expected = {"index.html", "cite/index.html", "figures/index.html", "figures/helix/index.html", "figures/sides/index.html"}
assert expected <= pages, f"missing pages: {expected - pages}"

home = (dist / "index.html").read_text()
assert "A Helix Seen From Every Side" in home
assert "Ada Example" in home and "0000-0002-1825-009X" in home

# Every \variable value, as its file has it, is in facts.json (SC-002) ...
for key, value in facts["variables"].items():
    on_disk = (paper / "src/tex/output" / f"{key}.tex").read_text()
    assert value == re.sub(r"(?<!\\)%.*", "", on_disk).strip(), key
# ... and the abstract shows them.
assert f">{facts['variables']['radius']}" in home or facts["variables"]["radius"] in home

for figure in facts["figures"]:
    for image in figure["images"]:
        assert (dist / "generated/figures" / image["file"]).exists(), image
        assert (dist / "generated/figures" / image["png"]).exists(), image

helix = (dist / "figures/helix/index.html").read_text()
assert 'src="/syw-site-example/generated/webapps/helix/site/"' in helix
assert (dist / "generated/webapps/helix/site/index.html").exists()
assert (dist / "generated/webapps/helix/helix.html").exists()
print(f"ok: {len(pages)} pages, {len(facts['variables'])} numbers, {len(facts['figures'])} figures, 1 webapp")
