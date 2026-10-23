"""How syw-site runs showyourwork: `showyourwork build syw__main syw_site_all` builds the paper (the
PDF, showyourwork's default target) and the docs data in one run.

This needs showyourwork's main branch (0.4.4.dev), whose `showyourwork build <targets>` builds targets
defined in the paper's Snakefile (showyourwork#690; the 0.4.3 release passes them to its
preprocessing step too, where they are unknown). CI pins commit 44d15103f.
"""

import re
import shutil
import subprocess
from pathlib import Path

SUPPORTED = "0.4.4.dev"
TARGETS = ["syw__main", "syw_site_all"]


class ShowyourworkError(RuntimeError):
    pass


def executable() -> str:
    exe = shutil.which("showyourwork")
    if not exe:
        raise ShowyourworkError("showyourwork is not on PATH; activate the paper's showyourwork environment")
    return exe


def version(exe: str) -> str:
    out = subprocess.run([exe, "--version"], capture_output=True, text=True, check=True).stdout
    m = re.search(r"(\d+\.\d+\.\d+\S*)", out)
    if not m:
        raise ShowyourworkError(f"cannot read the showyourwork version from {out!r}")
    return m.group(1)


def command(exe: str, cores: int, conda_frontend: str, extra: list[str]) -> list[str]:
    return [exe, "build", "--cores", str(cores), "--conda-frontend", conda_frontend, *extra, *TARGETS]


def build(repo: Path, cores: int = 1, conda_frontend: str = "conda", extra: list[str] = ()) -> None:
    """Build the paper and the docs data."""
    exe = executable()
    v = version(exe)
    if not v.startswith(SUPPORTED):
        raise ShowyourworkError(
            f"showyourwork {v} is not supported (needs showyourwork's main branch, {SUPPORTED}*)"
        )
    subprocess.run(command(exe, cores, conda_frontend, list(extra)), cwd=repo, check=True)
