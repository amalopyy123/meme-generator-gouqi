from datetime import datetime

from PIL import Image, ImageFilter, ImageOps
from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.utils import make_png_or_gif

BLUR_RADIUS = 1.2
THRESHOLD = 40


def to_line_art(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGBA")
    canvas = Image.new("RGBA", image.size, (255, 255, 255, 255))
    canvas.alpha_composite(image)

    grayscale = canvas.convert("L")
    softened = grayscale.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))
    edges = softened.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.autocontrast(edges, cutoff=2)
    mask = edges.point(lambda value: 255 if value >= THRESHOLD else 0, mode="L")
    return ImageOps.invert(mask).convert("RGBA")


def line_art(images: list[BuildImage], texts, args):
    def make(imgs: list[BuildImage]) -> BuildImage:
        return BuildImage(to_line_art(imgs[0].image))

    return make_png_or_gif(images, make)


add_meme(
    "line_art",
    line_art,
    min_images=1,
    max_images=1,
    keywords=["线稿化", "线稿", "素描线稿"],
    date_created=datetime(2026, 6, 8),
    date_modified=datetime(2026, 6, 8),
)
