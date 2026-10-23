# syw-site's Snakemake rules. A paper's Snakefile includes them (`syw-site init` writes it, guarded
# by an import so the paper still builds where syw-site is not installed) with
#     include: syw_site.rules_path()
# showyourwork runs them in its build step; `syw-site build` asks for `syw_site_all`.
#
# Nothing here reads the paper or the settings at include time: that happens in input functions,
# which Snakemake calls only when a docs target is requested, so a problem in docs/ can never
# break the paper's own build. Rules call syw-site through the interpreter that included them
# (showyourwork forbids `run:` and gives each rule the paper's conda env).

import sys as _syw_site_sys
from pathlib import Path as _SywSitePath

_SYW_SITE = f'"{_syw_site_sys.executable}" -m syw_site'
_SYW_SITE_OUT = "docs/public/generated"


def _syw_site_ms():
    from syw_site import facts

    return facts.strip_comments(_SywSitePath("src/tex/ms.tex").read_text(encoding="utf-8"))


def _syw_site_variable_files(wildcards):
    from syw_site import facts

    return ["src/tex/" + p for p in facts.variable_paths(_syw_site_ms())]


def _syw_site_figure_files(wildcards):
    from syw_site import facts

    return [i["source"] for f in facts.figures(_syw_site_ms(), _SywSitePath(".")) for i in f["images"]]


def _syw_site_webapp_inputs(wildcards):
    from syw_site import settings

    app = {w.name: w for w in settings.load().webapps}[wildcards.name]
    files = [str(p) for p in _SywSitePath("webapps", app.name).rglob("*") if p.is_file()]
    return [*app.inputs, *files, "docs/syw-site.yml"]


def _syw_site_all(wildcards):
    from syw_site import settings

    webapps = [f"{_SYW_SITE_OUT}/webapps/{w.name}" for w in settings.load().webapps]
    return [f"{_SYW_SITE_OUT}/facts.json", f"{_SYW_SITE_OUT}/figures", *webapps]


rule syw_site_facts:
    input:
        "src/tex/ms.tex",
        "docs/syw-site.yml",
        _syw_site_variable_files,
    output:
        f"{_SYW_SITE_OUT}/facts.json",
    shell:
        f"{_SYW_SITE} facts -o {{output}}"


rule syw_site_figures:
    input:
        "src/tex/ms.tex",
        _syw_site_figure_files,
    output:
        directory(f"{_SYW_SITE_OUT}/figures"),
    shell:
        f"{_SYW_SITE} figures -o {{output}}"


rule syw_site_webapp:
    input:
        _syw_site_webapp_inputs,
    output:
        directory(f"{_SYW_SITE_OUT}/webapps/{{name}}"),
    shell:
        f"{_SYW_SITE} webapp {{wildcards.name}}"


rule syw_site_all:
    input:
        _syw_site_all,
