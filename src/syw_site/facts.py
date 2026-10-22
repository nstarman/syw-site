"""Read a showyourwork paper's facts from its files: `src/tex/ms.tex` and the `\\variable` files.

A small scanner, not a TeX parser: it knows the commands showyourwork papers use (AASTeX's
`\\author[...]{}` and `\\affiliation{}`, `figure`/`figure*`, `\\variable{}`). Text stays LaTeX; the
site renders its math.
"""

import re
import warnings
from pathlib import Path

TEX = Path("src/tex")
SCHEMA = 1


def strip_comments(text: str) -> str:
    """Drop everything from an unescaped `%` to the end of its line."""
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def _group(text: str, i: int, open_: str, close: str) -> tuple[str, int]:
    """The contents of the group opening at text[i], and the index after it."""
    assert text[i] == open_
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == open_:
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return text[i + 1 : j], j + 1
        j += 1
    raise ValueError(f"unbalanced {open_!r} at offset {i}")


def commands(text: str, name: str) -> list[tuple[str | None, str]]:
    """Every `\\name[opt]{arg}` in text, as (opt, arg)."""
    found = []
    for m in re.finditer(rf"\\{name}(?![A-Za-z])\s*", text):
        i, opt = m.end(), None
        if i < len(text) and text[i] == "[":
            opt, i = _group(text, i, "[", "]")
            while i < len(text) and text[i].isspace():
                i += 1
        if i < len(text) and text[i] == "{":
            arg, _ = _group(text, i, "{", "}")
            found.append((opt, arg))
    return found


def _first(text: str, name: str) -> str | None:
    found = commands(text, name)
    return found[0][1] if found else None


def clean(text: str) -> str:
    """`\\todo{x}` becomes x; whitespace runs become one space."""
    for _, arg in commands(text, "todo"):
        text = text.replace(f"\\todo{{{arg}}}", arg)
    return re.sub(r"\s+", " ", text).strip()


def _options(opt: str | None) -> dict[str, str]:
    return dict(p.split("=", 1) for p in (opt or "").split(",") if "=" in p)


def authors(text: str) -> tuple[list[dict], list[str]]:
    """Authors in order, each with the indices of its affiliations (AASTeX: they follow it)."""
    affiliations: list[str] = []
    found = []
    for m in re.finditer(r"\\author(?![A-Za-z])", text):
        found.append(m.start())
    result = []
    for k, start in enumerate(found):
        end = found[k + 1] if k + 1 < len(found) else len(text)
        chunk = text[start:end]
        (opt, name), *_ = commands(chunk, "author")
        opts = _options(opt)
        idx = []
        for _, aff in commands(chunk, "affiliation"):
            aff = clean(aff)
            if aff not in affiliations:
                affiliations.append(aff)
            idx.append(affiliations.index(aff))
        author = {"name": clean(name), "affiliations": idx}
        for key, field in (("gname", "given"), ("sname", "surname"), ("orcid", "orcid")):
            if opts.get(key):
                author[field] = opts[key].strip()
        result.append(author)
    return result, affiliations


def _image(path: str, root: Path) -> dict:
    src = TEX / path
    if not src.suffix:
        for ext in (".pdf", ".png"):
            if (root / src.with_suffix(ext)).exists():
                src = src.with_suffix(ext)
                break
    rel = src.relative_to(TEX)
    image = {"source": src.as_posix(), "file": rel.as_posix()}
    if src.suffix == ".pdf":
        image["png"] = rel.with_suffix(".png").as_posix()
    return image


def figures(text: str, root: Path) -> list[dict]:
    result = []
    for m in re.finditer(r"\\begin\{(figure\*?)\}(.*?)\\end\{\1\}", text, re.S):
        body = m.group(2)
        images = [_image(arg, root) for _, arg in commands(body, "includegraphics")]
        if not images:
            continue
        label = _first(body, "label")
        if label:
            slug = re.sub(r"^fig:", "", label)
        else:
            slug = Path(images[0]["file"]).stem
            warnings.warn(f"figure with {images[0]['file']} has no \\label; using {slug!r}", stacklevel=2)
        caption = _first(body, "caption")
        result.append({"label": label, "slug": slug, "caption": clean(caption or ""), "images": images})
    return result


def variable_paths(text: str) -> list[str]:
    """Each `\\variable{...}` path, relative to src/tex/, once, in order."""
    return list(dict.fromkeys(arg for _, arg in commands(text, "variable")))


def variable_value(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"\\variable file {path} does not exist (build the paper first)")
    return strip_comments(path.read_text(encoding="utf-8")).strip()


def variable_key(path: str) -> str:
    return re.sub(r"\.tex$", "", re.sub(r"^output/", "", path))


def extract(root: Path = Path("."), *, repo: str, paper: dict | None = None) -> dict:
    ms = root / TEX / "ms.tex"
    if not ms.exists():
        raise FileNotFoundError(f"{ms} not found; is this a showyourwork repository?")
    text = strip_comments(ms.read_text(encoding="utf-8"))
    author_list, affiliations = authors(text)
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.S)
    return {
        "schema": SCHEMA,
        "title": clean(_first(text, "title") or ""),
        "authors": author_list,
        "affiliations": affiliations,
        "abstract": clean(abstract.group(1)) if abstract else "",
        "figures": figures(text, root),
        "variables": {
            variable_key(p): variable_value(root / TEX / p) for p in variable_paths(text)
        },
        "paper": {k: (paper or {}).get(k) for k in ("arxiv", "doi", "bibcode")},
        "repo": repo,
    }
