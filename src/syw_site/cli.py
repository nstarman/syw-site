"""syw-site: docs sites for showyourwork papers."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

from syw_site import __version__, facts, figures, init, serve, settings, showyourwork

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
    data["webapps"] = {w.name: {"figure": w.figure} for w in cfg.webapps}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


def cmd_figures(args) -> int:
    text = facts.strip_comments(Path("src/tex/ms.tex").read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for figure in facts.figures(text, Path(".")):
        for image in figure["images"]:
            figures.web_image(Path(image["source"]), args.output, image)
    return 0


def cmd_webapp(args) -> int:
    from figkit.cli import main as figkit

    cfg = settings.load()
    app = {w.name: w for w in cfg.webapps}[args.name]
    data = Path("docs/.syw-site/webapps") / app.name / "data"
    out = OUT / "webapps" / app.name
    subprocess.run(
        [*shlex.split(cfg.python), f"webapps/{app.name}/export.py", "--out", str(data)], check=True
    )
    datasets = [a for d in sorted(p for p in data.iterdir() if p.is_dir()) for a in ("--data", str(d))]
    return figkit(
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
    dist = Path("docs/dist")
    if not dist.is_dir():
        print("docs/dist/ not found; run `syw-site build` first", file=sys.stderr)
        return 1
    name = settings.load().repo.split("/")[1]
    server = serve.make_server(dist, name, args.port)
    print(f"Serving http://127.0.0.1:{args.port}/{name}/  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
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
