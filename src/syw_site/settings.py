"""Read and check `docs/syw-site.yml`, the per-paper settings."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SETTINGS = Path("docs/syw-site.yml")
_KEYS = {"repo", "website_id", "publish", "paper", "python", "webapps", "figures"}
_PAPER_KEYS = {"arxiv", "doi", "bibcode"}
_WEBAPP_KEYS = {"inputs", "figure", "explore", "title", "text", "replaces"}
_FIGURE_KEYS = {"icon", "image", "alpha"}
ALPHA = 0.8  # the portrait is a quiet mark, not a feature of the figure
CORNERS = ("top-right", "top-left", "bottom-right", "bottom-left")


class SettingsError(ValueError):
    pass


@dataclass(frozen=True)
class Webapp:
    name: str
    inputs: tuple[str, ...]
    figure: str | None = None
    explore: bool = False
    title: str | None = None
    text: str | None = None
    replaces: bool = False  # on its figure's page, in place of the static image


@dataclass(frozen=True)
class FigureIcon:
    """Where the author's portrait goes on a figure — one place per panel: each a corner, or a
    centre as fractions of the image's width and height; none for no portrait — on its
    `image`-th image (1-based), at opacity `alpha`."""

    places: tuple = ("top-right",)
    image: int = 1
    alpha: float = ALPHA


@dataclass(frozen=True)
class Settings:
    repo: str
    website_id: str | None = None
    publish: bool = False
    paper: dict = field(default_factory=dict)
    python: str = "python"
    webapps: tuple[Webapp, ...] = ()
    figures: dict = field(default_factory=dict)  # label -> FigureIcon

    def icon(self, label: str | None, slug: str) -> FigureIcon:
        return self.figures.get(label) or self.figures.get(slug) or FigureIcon()


def _place(label, p):
    if p in CORNERS:
        return p
    if isinstance(p, list) and len(p) == 2 and all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in p):
        return (float(p[0]), float(p[1]))
    raise SettingsError(f"syw-site.yml: figure {label!r} icon: each place is one of {list(CORNERS)} or [x, y] in 0–1")


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
        # Inputs may be outputs of the paper's pipeline; Snakemake reports one nothing makes.
        inputs = tuple(str(p) for p in spec.get("inputs") or ())
        explore = spec.get("explore", False)
        if not isinstance(explore, bool):
            raise SettingsError(f"syw-site.yml: webapp {name!r} explore must be true or false")
        replaces = spec.get("replaces", False)
        if not isinstance(replaces, bool) or (replaces and not spec.get("figure")):
            raise SettingsError(f"syw-site.yml: webapp {name!r} replaces must be true or false, and needs `figure`")
        webapps.append(Webapp(name, inputs, spec.get("figure"), explore, spec.get("title"), spec.get("text"), replaces))
    figures = {}
    for label, spec in (raw.get("figures") or {}).items():
        spec = spec or {}
        if not isinstance(spec, dict) or set(spec) - _FIGURE_KEYS:
            raise SettingsError(f"syw-site.yml: figure {label!r} takes only {sorted(_FIGURE_KEYS)}")
        icon = spec.get("icon", "top-right")
        if icon == "none" or icon is None:
            places = ()
        else:
            # One place, or a list of them (one per panel); a place is a corner or [x, y].
            single = icon in CORNERS or (isinstance(icon, list) and len(icon) == 2 and all(isinstance(v, (int, float)) for v in icon))
            places = tuple(_place(label, p) for p in ([icon] if single else icon if isinstance(icon, list) else [icon]))
        image = spec.get("image", 1)
        if not isinstance(image, int) or image < 1:
            raise SettingsError(f"syw-site.yml: figure {label!r} image must be 1, 2, …")
        alpha = spec.get("alpha", ALPHA)
        if not isinstance(alpha, (int, float)) or not 0 < alpha <= 1:
            raise SettingsError(f"syw-site.yml: figure {label!r} alpha must be in (0, 1]")
        figures[str(label)] = FigureIcon(places, image, float(alpha))
    python = raw.get("python", "python")
    if not isinstance(python, str) or not python.strip():
        raise SettingsError("syw-site.yml: `python` must be a command, e.g. `uv run --locked python`")
    website_id = raw.get("website_id")
    return Settings(
        repo, None if website_id is None else str(website_id), publish, paper, python, tuple(webapps), figures
    )
