import datetime
from pathlib import Path

from PIL import Image, ImageOps
from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.utils import Maker, make_gif_or_combined_gif

IMG_DIR = Path(__file__).parent / "images"
GREETING_CAT_GIF_PATH = IMG_DIR / "greeting_cat.gif"

CANVAS_SIZE = (300, 300)
MAX_USER_IMAGE_SIZE = (180, 180)

with Image.open(GREETING_CAT_GIF_PATH) as _greeting_cat_gif:
    FRAME_COUNT = getattr(_greeting_cat_gif, "n_frames", 1)
    FRAME_DURATION = _greeting_cat_gif.info.get("duration", 40) / 1000


def greeting_cat(images: list[BuildImage], texts, args):
    template = BuildImage.open(GREETING_CAT_GIF_PATH)

    def maker(i: int) -> Maker:
        def make(imgs: list[BuildImage]) -> BuildImage:
            user_image = ImageOps.exif_transpose(imgs[0].image).convert("RGBA")
            template_frame = imgs[1].image.convert("RGBA")

            src_w, src_h = user_image.size
            max_w, max_h = MAX_USER_IMAGE_SIZE
            scale = min(max_w / src_w, max_h / src_h)
            user_w = max(1, round(src_w * scale))
            user_h = max(1, round(src_h * scale))
            user_image = user_image.resize((user_w, user_h), Image.Resampling.LANCZOS)

            canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
            paste_x = (CANVAS_SIZE[0] - user_w) // 2
            paste_y = (CANVAS_SIZE[1] - user_h) // 2
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
    date_modified=datetime.datetime(2026, 6, 2),
)
