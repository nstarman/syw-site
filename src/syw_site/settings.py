"""Read and check `docs/syw-site.yml`, the per-paper settings."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SETTINGS = Path("docs/syw-site.yml")
_KEYS = {"repo", "website_id", "publish", "paper", "webapps"}
_PAPER_KEYS = {"arxiv", "doi", "bibcode"}
_WEBAPP_KEYS = {"inputs", "figure"}


class SettingsError(ValueError):
    pass


@dataclass(frozen=True)
class Webapp:
    name: str
    inputs: tuple[str, ...]
    figure: str | None = None


@dataclass(frozen=True)
class Settings:
    repo: str
    website_id: str | None = None
    publish: bool = False
    paper: dict = field(default_factory=dict)
    webapps: tuple[Webapp, ...] = ()


def load(root: Path = Path(".")) -> Settings:
    path = root / SETTINGS
    if not path.exists():
        raise SettingsError(f"{path} not found; run `syw-site init` first")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return parse(raw, root)


def parse(raw: dict, root: Path) -> Settings:
    if not isinstance(raw, dict):
        raise SettingsError("syw-site.yml must be a mapping")
    if unknown := set(raw) - _KEYS:
        raise SettingsError(f"syw-site.yml: unknown keys {sorted(unknown)}")
    repo = raw.get("repo")
    if not isinstance(repo, str) or not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise SettingsError("syw-site.yml: `repo` must be owner/name")
    publish = raw.get("publish", False)
    if not isinstance(publish, bool):
        raise SettingsError("syw-site.yml: `publish` must be true or false")
    paper = raw.get("paper") or {}
    if not isinstance(paper, dict) or set(paper) - _PAPER_KEYS:
        raise SettingsError(f"syw-site.yml: `paper` takes only {sorted(_PAPER_KEYS)}")
    paper = {k: (None if v is None else str(v)) for k, v in paper.items()}
    webapps = []
    for name, spec in (raw.get("webapps") or {}).items():
        if not re.fullmatch(r"[a-z0-9-]+", str(name)):
            raise SettingsError(f"syw-site.yml: webapp name {name!r} must be [a-z0-9-]+")
        spec = spec or {}
        if not isinstance(spec, dict) or set(spec) - _WEBAPP_KEYS:
            raise SettingsError(f"syw-site.yml: webapp {name!r} takes only {sorted(_WEBAPP_KEYS)}")
        if not (root / "webapps" / name).is_dir():
            raise SettingsError(f"syw-site.yml: webapp {name!r} has no webapps/{name}/")
        inputs = tuple(str(p) for p in spec.get("inputs") or ())
        for p in inputs:
            if not (root / p).exists():
                raise SettingsError(f"syw-site.yml: webapp {name!r} input {p} does not exist")
        webapps.append(Webapp(name, inputs, spec.get("figure")))
    website_id = raw.get("website_id")
    return Settings(repo, None if website_id is None else str(website_id), publish, paper, tuple(webapps))
