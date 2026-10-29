"""syw-site: docs sites for showyourwork papers."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

from syw_site import __version__, facts, figures, init, settings, showyourwork

OUT = Path("docs/public/generated")


def cmd_init(args) -> int:
    for p in init.init(Path("."), args.repo):
        print(f"wrote {p}")
    print("Next: fill in docs/syw-site.yml, then `syw-site build` and `syw-site serve`.")
    return 0


def cmd_facts(args) -> int:
    cfg = settings.load()
    data = facts.extract(Path("."), repo=cfg.repo, paper=cfg.paper)
    data["website_id"] = cfg.website_id
    data["webapps"] = {
        w.name: {"figure": w.figure, "explore": w.explore, "title": w.title, "text": w.text} for w in cfg.webapps
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


def cmd_figures(args) -> int:
    cfg = settings.load()
    text = facts.strip_comments(Path("src/tex/ms.tex").read_text(encoding="utf-8"))
    portrait = Path("docs/portrait.jpg")
    if not portrait.exists():
        print("syw-site: no docs/portrait.jpg (run `syw-site card`): figures without the icon", file=sys.stderr)
    args.output.mkdir(parents=True, exist_ok=True)
    for figure in facts.figures(text, Path(".")):
        icon = cfg.icon(figure["label"], figure["slug"])
        for n, image in enumerate(figure["images"], start=1):
            places = icon.places if n == icon.image else ()
            figures.web_image(Path(image["source"]), args.output, image, portrait, places, icon.alpha)
    return 0


def cmd_card(args) -> int:
    from syw_site import card

    return card.run(Path("."), settings.load())


def cmd_webapp(args) -> int:
    from figpress_apps.cli import main as figpress_apps

    cfg = settings.load()
    app = {w.name: w for w in cfg.webapps}.get(args.name)
    if app is None:
        raise settings.SettingsError(f"no webapp {args.name!r} under webapps: in docs/syw-site.yml")
    data = Path("docs/.syw-site/webapps") / app.name / "data"
    out = OUT / "webapps" / app.name
    subprocess.run(
        [*shlex.split(cfg.python), f"webapps/{app.name}/export.py", "--out", str(data)], check=True
    )
    datasets = [a for d in sorted(p for p in data.iterdir() if p.is_dir()) for a in ("--data", str(d))]
    return figpress_apps(
        ["build", f"webapps/{app.name}", *datasets, "--out", str(out / "site"),
         "--single-file", str(out / f"{app.name}.html")]
    )


def cmd_build(args) -> int:
    showyourwork.build(Path("."), args.cores, args.conda_frontend, args.extra)
    docs = Path("docs")
    stamp = docs / "node_modules" / ".package-lock.json"
    if not stamp.exists() or stamp.stat().st_mtime < (docs / "package-lock.json").stat().st_mtime:
        subprocess.run(["npm", "ci"], cwd=docs, check=True)
    subprocess.run(["npx", "astro", "build"], cwd=docs, check=True)
    return 0


def cmd_serve(args) -> int:
    # Astro serves only under the site's base path, as nstarkman.space will.
    if not Path("docs/dist").is_dir():
        print("docs/dist/ not found; run `syw-site build` first", file=sys.stderr)
        return 1
    try:
        return subprocess.run(["npx", "astro", "preview", "--port", str(args.port)], cwd="docs").returncode
    except KeyboardInterrupt:
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="syw-site", description=__doc__)
    p.add_argument("--version", action="version", version=f"syw-site {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init", help="add the docs site to this showyourwork repository")
    s.add_argument("--repo", metavar="OWNER/NAME", help="default: from `git remote get-url origin`")
    s.set_defaults(func=cmd_init)
    s = sub.add_parser("facts", help="write facts.json from the paper")
    s.add_argument("-o", "--output", type=Path, default=OUT / "facts.json")
    s.set_defaults(func=cmd_facts)
    s = sub.add_parser("figures", help="write web images of the paper's figures")
    s.add_argument("-o", "--output", type=Path, default=OUT / "figures")
    s.set_defaults(func=cmd_figures)
    s = sub.add_parser("card", help="fetch the paper's card and the author's portrait from nstarkman.space's data")
    s.set_defaults(func=cmd_card)
    s = sub.add_parser("webapp", help="export and build one webapp listed in syw-site.yml")
    s.add_argument("name")
    s.set_defaults(func=cmd_webapp)
    s = sub.add_parser("build", help="build the paper, the docs data and the site")
    s.add_argument("-c", "--cores", type=int, default=1)
    s.add_argument("--conda-frontend", default="conda")
    s.add_argument("extra", nargs="*", help="passed to showyourwork / Snakemake (after --)")
    s.set_defaults(func=cmd_build)
    s = sub.add_parser("serve", help="serve docs/dist/ under its base path")
    s.add_argument("--port", type=int, default=8000)
    s.set_defaults(func=cmd_serve)
    args = p.parse_args(argv)
    try:
        return args.func(args)
    except (settings.SettingsError, init.InitError, showyourwork.ShowyourworkError, FileNotFoundError) as e:
        print(f"syw-site: {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        return e.returncode
