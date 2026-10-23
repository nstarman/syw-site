"""Web images of the paper's figures, made from the files showyourwork already produced."""

import shutil
from pathlib import Path

import pypdfium2

DPI = 200  # about 2x a column's CSS width for a 3.5 in figure


def web_image(source: Path, out_dir: Path, image: dict) -> None:
    """Copy the figure file into out_dir; for a PDF also render its first page to PNG."""
    target = out_dir / image["file"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    if "png" in image:
        pdf = pypdfium2.PdfDocument(source)
        try:
            pdf[0].render(scale=DPI / 72).to_pil().save(out_dir / image["png"], optimize=True)
        finally:
            pdf.close()
