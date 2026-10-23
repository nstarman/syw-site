import pypdfium2
from PIL import Image

from syw_site.figures import DPI, web_image


def test_pdf_becomes_png_and_is_kept(tmp_path):
    src = tmp_path / "fig.pdf"
    pdf = pypdfium2.PdfDocument.new()
    pdf.new_page(252, 180)  # 3.5 x 2.5 in
    pdf.save(src)
    out = tmp_path / "out"
    web_image(src, out, {"file": "figures/fig.pdf", "png": "figures/fig.png"})
    assert (out / "figures/fig.pdf").read_bytes() == src.read_bytes()
    with Image.open(out / "figures/fig.png") as im:
        assert im.size == (round(3.5 * DPI), round(2.5 * DPI))


def test_png_is_copied(tmp_path):
    src = tmp_path / "fig.png"
    Image.new("RGB", (10, 10)).save(src)
    web_image(src, tmp_path / "out", {"file": "figures/fig.png"})
    assert (tmp_path / "out/figures/fig.png").read_bytes() == src.read_bytes()
