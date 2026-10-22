"""`syw-site init`: add the docs scaffold, the rules include and the workflow to a paper repo."""

import re
import subprocess
from importlib import resources
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
    template = resources.files("syw_site") / "template"
    files: dict[Path, bytes] = {}

    def walk(node, rel: Path):
        for child in node.iterdir():
            if child.is_dir():
                walk(child, rel / child.name)
            else:
                data = child.read_bytes()
                if child.name.endswith((".mjs", ".yml", ".json", ".mdx", ".astro", ".md", ".js")):
                    data = (
                        data.replace(b"{{REPO}}", repo.encode())
                        .replace(b"{{NAME}}", name.encode())
                        .replace(b"{{VERSION}}", __version__.encode())
                    )
                files[rel / child.name] = data

    walk(template / "docs", Path("docs"))
    walk(template / "workflows", Path(".github/workflows"))
    gitignore = template / "docs" / "gitignore"
    if gitignore.is_file():  # stored without its dot so packaging keeps it
        files[Path("docs/.gitignore")] = files.pop(Path("docs/gitignore"))
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
