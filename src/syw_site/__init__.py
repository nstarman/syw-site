"""Docs sites for showyourwork papers."""

from pathlib import Path

__version__ = "2026.10.23"


def rules_path() -> str:
    """The Snakemake rules a paper's Snakefile includes."""
    return str(Path(__file__).with_name("rules.smk"))
