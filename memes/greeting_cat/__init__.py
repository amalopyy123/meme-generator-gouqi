import datetime
from pathlib import Path

from PIL import Image, ImageOps
from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.utils import Maker, make_gif_or_combined_gif

IMG_DIR = Path(__file__).parent / "images"
GREETING_CAT_GIF_PATH = IMG_DIR / "greeting_cat.gif"

CANVAS_SIZE = (300, 300)
USER_IMAGE_SIZE = (250, 250)

with Image.open(GREETING_CAT_GIF_PATH) as _greeting_cat_gif:
    FRAME_COUNT = getattr(_greeting_cat_gif, "n_frames", 1)
    FRAME_DURATION = _greeting_cat_gif.info.get("duration", 40) / 1000


def greeting_cat(images: list[BuildImage], texts, args):
    template = BuildImage.open(GREETING_CAT_GIF_PATH)

    def maker(i: int) -> Maker:
        def make(imgs: list[BuildImage]) -> BuildImage:
            user_image = ImageOps.exif_transpose(imgs[0].image).convert("RGBA")
            template_frame = imgs[1].image.convert("RGBA")

            user_image = user_image.resize(USER_IMAGE_SIZE, Image.Resampling.LANCZOS)
            user_w, user_h = user_image.size

            canvas = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 255))
            paste_x = 0
            paste_y = CANVAS_SIZE[1] - user_h
            canvas.paste(user_image, (paste_x, paste_y), user_image)
            canvas.paste(template_frame, (0, 0), template_frame)
            return BuildImage(canvas)

        return make

    return make_gif_or_combined_gif(
        [images[0], template],
        maker,
        FRAME_COUNT,
        FRAME_DURATION,
    )


add_meme(
    "greeting_cat",
    greeting_cat,
    max_images=1,
    min_images=1,
    keywords=["挥手猫"],
    date_created=datetime.datetime(2026, 6, 2),
    date_modified=datetime.datetime(2026, 6, 3),
)
