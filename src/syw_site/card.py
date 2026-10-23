"""`syw-site card`: snapshot what nstarkman.space knows about the paper (its record, what
its refs reach, its co-authors' places), the images the card draws and the author's
portrait — by running the docs site's scripts/card.mjs, which uses the website's own
collector (@nstarkman/research-kit) on its GitHub data. Needs the network; builds do not."""

import subprocess
from pathlib import Path

from syw_site.settings import Settings, SettingsError


def command(cfg: Settings) -> list[str]:
    if not cfg.website_id:
        raise SettingsError("syw-site.yml: set website_id (the paper's record id on nstarkman.space) first")
    return ["node", "scripts/card.mjs", cfg.website_id]


def run(root: Path, cfg: Settings) -> int:
    docs = root / "docs"
    cmd = command(cfg)
    if not (docs / "node_modules").exists():
        subprocess.run(["npm", "ci"], cwd=docs, check=True)
    return subprocess.run(cmd, cwd=docs).returncode
