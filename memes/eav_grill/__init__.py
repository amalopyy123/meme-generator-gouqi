import datetime
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.utils import Maker, make_gif_or_combined_gif

IMG_DIR = Path(__file__).parent / "images"
BACKGROUND_PATH = IMG_DIR / "background.png"

FRAME_COUNT = 24
FRAME_DURATION = 0.05
FOOD_MAX_SIZE = (100, 100)
ANCHOR_DEBUG_RADIUS = 8

# These values define the swing geometry and can be tuned later when the rope
# rendering is added.
ROPE_ANCHOR = (55, -60)
ROPE_LENGTH = 60
REST_ANGLE_DEG = 8
SWING_AMPLITUDE_DEG = 45
FOOD_ATTACHMENT_RATIO = (0.5, 0.08)


def contain_size(
    src_size: tuple[int, int], max_size: tuple[int, int]
) -> tuple[int, int]:
    src_w, src_h = src_size
    max_w, max_h = max_size
    scale = min(max_w / src_w, max_h / src_h)
    return max(1, round(src_w * scale)), max(1, round(src_h * scale))


def prepare_food_image(image: Image.Image) -> Image.Image:
    food = ImageOps.flip(ImageOps.exif_transpose(image).convert("RGBA"))
    diameter = min(food.size)
    left = (food.width - diameter) // 2
    top = (food.height - diameter) // 2
    food = food.crop((left, top, left + diameter, top + diameter))

    mask = Image.new("L", food.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, food.width - 1, food.height - 1), fill=255)
    food.putalpha(mask)

    target_size = contain_size(food.size, FOOD_MAX_SIZE)
    return food.resize(target_size, Image.Resampling.LANCZOS)


def calculate_swing_angle(frame_index: int) -> float:
    # Small-angle pendulum approximation:
    # theta(t) = theta0 + amplitude * sin(omega * t)
    progress = frame_index / FRAME_COUNT
    phase = progress * 2 * math.pi
    angle_deg = REST_ANGLE_DEG + SWING_AMPLITUDE_DEG * math.sin(phase)
    return math.radians(angle_deg)


def calculate_rope_end(
    anchor: tuple[int, int], rope_length: float, angle: float
) -> tuple[float, float]:
    return (
        anchor[0] + rope_length * math.sin(angle),
        anchor[1] + rope_length * math.cos(angle),
    )


def calculate_food_position(
    rope_end: tuple[float, float],
    food_size: tuple[int, int],
    attachment_ratio: tuple[float, float] = FOOD_ATTACHMENT_RATIO,
) -> tuple[int, int]:
    attachment_x = food_size[0] * attachment_ratio[0]
    attachment_y = food_size[1] * attachment_ratio[1]
    return (
        round(rope_end[0] - attachment_x),
        round(rope_end[1] - attachment_y),
    )


def eav_grill(images: list[BuildImage], texts, args):
    background = BuildImage.open(BACKGROUND_PATH)

    def maker(i: int) -> Maker:
        def make(imgs: list[BuildImage]) -> BuildImage:
            frame = imgs[1].image.convert("RGBA").copy()
            food = prepare_food_image(imgs[0].image)
            angle = calculate_swing_angle(i)
            rope_end = calculate_rope_end(ROPE_ANCHOR, ROPE_LENGTH, angle)
            food_position = calculate_food_position(rope_end, food.size)
            # draw ROPE_ANCHOR for debugging, sometimes has no effect if ROPE_ANCHOR.x <0 or ROPE_ANCHOR.y <0
            # draw.ellipse(
            #     (
            #         ROPE_ANCHOR[0] - ANCHOR_DEBUG_RADIUS,
            #         ROPE_ANCHOR[1] - ANCHOR_DEBUG_RADIUS,
            #         ROPE_ANCHOR[0] + ANCHOR_DEBUG_RADIUS,
            #         ROPE_ANCHOR[1] + ANCHOR_DEBUG_RADIUS,
            #     ),
            #     outline=(255, 0, 0, 255),
            #     width=3,
            # )
            frame.paste(food, food_position, food)
            return BuildImage(frame)

        return make

    return make_gif_or_combined_gif(
        [images[0], background],
        maker,
        FRAME_COUNT,
        FRAME_DURATION,
    )


add_meme(
    "eav_grill",
    eav_grill,
    max_images=1,
    min_images=1,
    keywords=["伊娃烧"],
    date_created=datetime.datetime(2026, 6, 4),
    date_modified=datetime.datetime(2026, 6, 4),
)
