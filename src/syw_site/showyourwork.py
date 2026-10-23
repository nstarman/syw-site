"""The one place syw-site depends on how showyourwork runs.

`showyourwork build <target>` hands <target> to its preprocessing step too, which does not load
the paper's Snakefile, so a target defined there fails (showyourwork 0.4.3 and main;
https://github.com/showyourwork/showyourwork/issues/769). So syw-site runs
`showyourwork build` (preprocess and the PDF), then showyourwork's build step once more with the
docs target, with the command line and environment showyourwork itself uses
(`showyourwork/cli/commands/run_snakemake.py`). showyourwork is never imported here; a subprocess
asks its interpreter where it is installed. A new showyourwork version is supported by checking
that file against docs_command and widening `supported`.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

# showyourwork's main branch (0.4.4.dev, Snakemake 9), as papers install it from git; CI pins
# commit 44d15103f. 0.4.3 runs on Python 3.10, which figkit (3.11+) cannot join.
SUPPORTED = "0.4.4.dev"
TARGET = "syw_site_all"


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


def interpreter(exe: str) -> str:
    """The Python of showyourwork's environment: console scripts sit beside it."""
    return str(Path(exe).resolve().parent / "python")


def build_snakefile(python: str) -> str:
    code = "import showyourwork, pathlib; print(pathlib.Path(showyourwork.__file__).parent / 'workflow' / 'build.smk')"
    return subprocess.run([python, "-c", code], capture_output=True, text=True, check=True).stdout.strip()


def docs_command(python: str, snakefile: str, cores: int, conda_frontend: str, extra: list[str]) -> list[str]:
    # showyourwork runs `snakemake` from PATH; running it with showyourwork's own interpreter is the
    # same program when showyourwork's environment is active, and still right when it is not.
    return [
        python, "-m", "snakemake", "--cores", str(cores), "--use-conda", "--conda-frontend", conda_frontend,
        "--cache", "-s", snakefile, *extra, TARGET,
    ]


def docs_env(repo: Path) -> dict[str, str]:
    cache = repo / ".showyourwork" / "cache"
    return {**os.environ, "SNAKEMAKE_RUN_TYPE": "build", "SNAKEMAKE_OUTPUT_CACHE": str(cache)}


def build(repo: Path, cores: int = 1, conda_frontend: str = "conda", extra: list[str] = ()) -> None:
    """Build the paper, then the docs data."""
    exe = executable()
    v = version(exe)
    if not v.startswith(SUPPORTED):
        raise ShowyourworkError(f"showyourwork {v} is not supported by this syw-site (supported: {SUPPORTED}*)")
    common = ["--cores", str(cores), "--conda-frontend", conda_frontend]
    subprocess.run([exe, "build", *common, *extra], cwd=repo, check=True)
    python = interpreter(exe)
    command = docs_command(python, build_snakefile(python), cores, conda_frontend, list(extra))
    subprocess.run(command, cwd=repo, env=docs_env(repo), check=True)
