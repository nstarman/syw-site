import pypdfium2
import pytest
from PIL import Image

from syw_site.figures import DPI, MIN_ICON, place, web_image


@pytest.fixture
def portrait(tmp_path):
    p = tmp_path / "portrait.png"  # lossless, so its colour is exact
    Image.new("RGB", (300, 400), (200, 30, 30)).save(p)  # red, not square
    return p


def make_pdf(path, w=252, h=180):  # 3.5 x 2.5 in
    pdf = pypdfium2.PdfDocument.new()
    pdf.new_page(w, h)
    pdf.save(path)


def test_pdf_becomes_stamped_webp_and_png_and_is_kept(tmp_path, portrait):
    src = tmp_path / "fig.pdf"
    make_pdf(src)
    out = tmp_path / "out"
    image = {"file": "figures/fig.pdf", "png": "figures/fig.png", "webp": "figures/fig.webp"}
    web_image(src, out, image, portrait)
    assert (out / "figures/fig.pdf").read_bytes() == src.read_bytes()
    for name in ("fig.png", "fig.webp"):
        with Image.open(out / "figures" / name) as im:
            assert im.size == (round(3.5 * DPI), round(2.5 * DPI))
            w = im.width
            d = max(MIN_ICON, round(0.07 * w))
            m = round(0.02 * w)
            cx, cy = w - m - d // 2, m + d // 2  # top-right by default
            assert im.convert("RGB").getpixel((cx, cy)) == (200, 30, 30)  # the portrait
            assert im.convert("RGB").getpixel((m + d // 2, m + d // 2)) != (200, 30, 30)  # not top-left


@pytest.mark.parametrize(
    "where, expect",
    [
        ("top-right", (1000 - 20 - 70, 20)),
        ("top-left", (20, 20)),
        ("bottom-right", (1000 - 20 - 70, 500 - 20 - 70)),
        ("bottom-left", (20, 500 - 20 - 70)),
        ((0.5, 0.5), (500 - 35, 250 - 35)),
        ((1.0, 0.0), (1000 - 70, 0)),  # kept inside the image
    ],
)
def test_place(where, expect):
    assert place((1000, 500), 70, where) == expect


def test_small_figures_keep_the_minimum(tmp_path, portrait):
    src = tmp_path / "small.png"
    Image.new("RGB", (300, 200), "white").save(src)
    web_image(src, tmp_path / "out", {"file": "f/small.png", "png": "f/small.png", "webp": "f/small.webp"}, portrait, "top-left")
    with Image.open(tmp_path / "out/f/small.png") as im:
        assert im.convert("RGB").getpixel((6 + MIN_ICON // 2, 6 + MIN_ICON // 2)) == (200, 30, 30)


def test_none_and_no_portrait_leave_it_clean(tmp_path, portrait):
    src = tmp_path / "f.png"
    Image.new("RGB", (400, 300), "white").save(src)
    for p, where in ((portrait, None), (None, "top-right")):
        out = tmp_path / f"out-{where}"
        web_image(src, out, {"file": "f.png", "png": "f.png", "webp": "f.webp"}, p, where)
        with Image.open(out / "f.webp") as im:
            assert im.convert("RGB").getextrema() == ((255, 255),) * 3  # all white
