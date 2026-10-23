"""`syw-site init`: add the docs scaffold, the rules include and the workflow to a paper repo."""

import re
import subprocess
from pathlib import Path

from syw_site import __version__

INCLUDE = 'include: __import__("syw_site").rules_path()'


class InitError(RuntimeError):
    pass


def repo_from_git(root: Path) -> str:
    url = subprocess.run(
        ["git", "remote", "get-url", "origin"], cwd=root, capture_output=True, text=True
    ).stdout.strip()
    m = re.search(r"github\.com[:/]([\w.-]+/[\w.-]+?)(?:\.git)?$", url)
    if not m:
        raise InitError("cannot tell the GitHub repository from `git remote`; pass --repo owner/name")
    return m.group(1)


def planned(repo: str) -> dict[Path, bytes]:
    """Every file init writes, by path relative to the paper repo."""
    name = repo.split("/")[1]
    template = Path(__file__).with_name("template")
    files: dict[Path, bytes] = {}
    for src in sorted(p for p in template.rglob("*") if p.is_file()):
        rel = src.relative_to(template)
        rel = Path(".github", *rel.parts) if rel.parts[0] == "workflows" else rel
        # gitignore is stored without its dot so packaging keeps it
        rel = rel.with_name(".gitignore") if rel.name == "gitignore" else rel
        data = src.read_bytes()
        if src.suffix in {".mjs", ".yml", ".json", ".mdx", ".astro", ".md", ".js"}:
            for key, value in (("{{REPO}}", repo), ("{{NAME}}", name), ("{{VERSION}}", __version__)):
                data = data.replace(key.encode(), value.encode())
        files[rel] = data
    return files


def init(root: Path, repo: str | None = None) -> list[Path]:
    if not (root / "showyourwork.yml").exists() or not (root / "src/tex/ms.tex").exists():
        raise InitError("not a showyourwork repository (no showyourwork.yml or src/tex/ms.tex)")
    files = planned(repo or repo_from_git(root))
    clashes = [p for p, data in files.items() if (root / p).exists() and (root / p).read_bytes() != data]
    if clashes:
        listed = "\n  ".join(str(p) for p in clashes)
        raise InitError(f"these files exist and differ from the scaffold; move them aside first:\n  {listed}")
    written = []
    for p, data in files.items():
        if not (root / p).exists():
            (root / p).parent.mkdir(parents=True, exist_ok=True)
            (root / p).write_bytes(data)
            written.append(p)
    snakefile = root / "Snakefile"
    text = snakefile.read_text(encoding="utf-8") if snakefile.exists() else ""
    if INCLUDE not in text:
        sep = "" if not text or text.endswith("\n") else "\n"
        snakefile.write_text(f"{text}{sep}\n# The paper's docs site (syw-site).\n{INCLUDE}\n", encoding="utf-8")
        written.append(Path("Snakefile"))
    return written
