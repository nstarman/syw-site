"""Web images of the paper's figures, made from the files showyourwork already produced, each
with the author's portrait stamped in a corner (or where syw-site.yml says)."""

import shutil
from pathlib import Path

import pypdfium2
from PIL import Image, ImageDraw

DPI = 200  # about 2x a column's CSS width for a 3.5 in figure
MIN_ICON = 48  # px: the portrait never smaller than this


def raster(source: Path) -> Image.Image:
    """The figure as an RGBA image: a PDF's first page at DPI, or the image file itself."""
    if source.suffix == ".pdf":
        pdf = pypdfium2.PdfDocument(source)
        try:
            return pdf[0].render(scale=DPI / 72).to_pil().convert("RGBA")
        finally:
            pdf.close()
    with Image.open(source) as im:
        return im.convert("RGBA")


def badge(portrait: Path, d: int) -> Image.Image:
    """The portrait as a round badge d px across, with a thin white ring."""
    with Image.open(portrait) as p:
        p = p.convert("RGB")
        side = min(p.size)
        left, top = (p.width - side) // 2, (p.height - side) // 2
        face = p.crop((left, top, left + side, top + side)).resize((d, d), Image.LANCZOS)
    ring = max(2, d // 24)
    out = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    mask = Image.new("L", (d, d), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
    white = Image.new("RGBA", (d, d), (255, 255, 255, 255))
    out.paste(white, (0, 0), mask)
    inner = Image.new("L", (d, d), 0)
    ImageDraw.Draw(inner).ellipse((ring, ring, d - 1 - ring, d - 1 - ring), fill=255)
    out.paste(face.convert("RGBA"), (0, 0), inner)
    return out


def place(size: tuple[int, int], d: int, where) -> tuple[int, int]:
    """The badge's top-left corner: in a corner, a margin in, or centred on [x, y] (fractions
    of the width and height), kept inside the image."""
    w, h = size
    margin = round(0.02 * w)
    if isinstance(where, tuple):
        x, y = round(where[0] * w - d / 2), round(where[1] * h - d / 2)
    else:
        vert, horiz = where.split("-")
        x = margin if horiz == "left" else w - margin - d
        y = margin if vert == "top" else h - margin - d
    return min(max(x, 0), max(w - d, 0)), min(max(y, 0), max(h - d, 0))


def stamp(im: Image.Image, portrait: Path, places, alpha: float = 1.0) -> Image.Image:
    """The figure with the portrait stamped at each place (a corner or [x, y]), at opacity
    `alpha`; no places, no portrait."""
    if not places:
        return im
    d = max(MIN_ICON, round(0.07 * im.width))
    b = badge(portrait, d)
    if alpha < 1:
        b.putalpha(b.getchannel("A").point(lambda a: round(a * alpha)))
    out = im.copy()
    for where in places:
        out.alpha_composite(b, place(im.size, d, where))
    return out


def web_image(source: Path, out_dir: Path, image: dict, portrait: Path | None = None, places=("top-right",), alpha: float = 1.0) -> None:
    """Copy the figure file into out_dir, and write its web images — lossless WebP for the
    page, PNG to download — with the portrait stamped at each place (none without a portrait)."""
    target = out_dir / image["file"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    im = raster(source)
    if portrait is not None and portrait.exists():
        im = stamp(im, portrait, places, alpha)
    im.save(out_dir / image["png"], optimize=True)
    im.save(out_dir / image["webp"], lossless=True, method=6)
