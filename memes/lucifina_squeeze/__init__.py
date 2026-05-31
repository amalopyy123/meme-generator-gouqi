import datetime
import random
from pathlib import Path

from PIL import Image, ImageDraw
from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.utils import Maker, make_gif_or_combined_gif

IMG_DIR = Path(__file__).parent / "images"
BACKGROUND_PATH = IMG_DIR / "ct_rucyfina1.png"
ELLIPSE_CENTER = (460, 360)
ELLIPSE_RX = 150
ELLIPSE_RY = 100


class Dot:
    def __init__(self, positon: tuple[int, int], direction: tuple[float, float]):
        self.px = positon[0]
        self.py = positon[1]
        self.vx = 0
        self.vy = 0
        self.dx = direction[0]
        self.dy = direction[1]
        self.radius = random.randint(1, 3)

    def move(self, step: int):
        a = 0.02 * step / self.radius
        self.vx += a * self.dx
        self.vy += a * self.dy
        self.px += round(self.vx)
        self.py += round(self.vy)
        if random.random() < 0.25:
            self.radius -= 1

    def draw_on(self, img: Image.Image):
        ImageDraw.Draw(img).ellipse(
            (
                self.px - self.radius,
                self.py - self.radius,
                self.px + self.radius,
                self.py + self.radius,
            ),
            fill=(0, 0, 0, 255),
        )

    def out_of_img(self, img: Image.Image) -> bool:
        w, h = img.size
        if (
            self.radius <= 0
            or self.px + self.radius < 0
            or self.px - self.radius > w
            or self.py + self.radius < 0
            or self.py - self.radius > h
        ):
            return True
        return False


def make_dust(dusts: list[Dot], step: int, size: tuple[int, int]) -> Image.Image:
    dust_mask = Image.new("RGBA", size)
    remove_list = []
    for dot in dusts:
        dot.move(step)
        if dot.out_of_img(dust_mask):
            remove_list.append(dot)
        else:
            dot.draw_on(dust_mask)
    for dot in remove_list:
        dusts.remove(dot)
    return dust_mask


def lucifina_squeeze(images: list[BuildImage], texts, args):
    image = images[0]
    src_w, src_h = image.size
    target_w = ELLIPSE_RX * 2
    target_h = ELLIPSE_RY * 2
    scale = min(target_w / src_w, target_h / src_h)
    width = max(1, round(src_w * scale))
    height = max(1, round(src_h * scale))

    bg_template = BuildImage.open(BACKGROUND_PATH).image.convert("RGBA")
    bg_w, bg_h = bg_template.size
    paste_x = ELLIPSE_CENTER[0] - width // 2
    paste_y = ELLIPSE_CENTER[1] - height // 2
    paste_x = min(max(paste_x, 0), max(0, bg_w - width))
    paste_y = min(max(paste_y, 0), max(0, bg_h - height))

    mask_rx = min(ELLIPSE_RX, width // 2)
    mask_ry = min(ELLIPSE_RY, height // 2)
    mask_center = (width // 2, height // 2)
    ellipse_mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(ellipse_mask).ellipse(
        (
            mask_center[0] - mask_rx,
            mask_center[1] - mask_ry,
            mask_center[0] + mask_rx,
            mask_center[1] + mask_ry,
        ),
        fill=255,
    )

    o = (width * 2 // 3, height * 3 // 2)
    step = (o[0] ** 2 + o[1] ** 2) ** 0.5 / 24
    dusts = []

    def maker(i: int) -> Maker:
        def compose_frame(foreground: Image.Image) -> BuildImage:
            canvas = bg_template.copy()
            canvas.paste(foreground, (paste_x, paste_y), foreground)
            return BuildImage(canvas)

        def make(imgs: list[BuildImage]) -> BuildImage:
            img = imgs[0].image.convert("RGBA").resize((width, height))
            img.putalpha(ellipse_mask)
            if i <= 9:
                return compose_frame(img)
            elif 9 < i < 28:
                new_img = img.copy()
                for x in range(width):
                    for y in range(
                        max(0, min(height, height - round(step * (i + 11)))), height
                    ):
                        pixel = (x, y)
                        if img.getpixel(pixel)[3] == 0:  # type: ignore
                            continue
                        distance = ((x - o[0]) ** 2 + (y - o[1]) ** 2) ** 0.5
                        if distance <= step * (i - 5):
                            new_img.putpixel(pixel, (0, 0, 0, 0))
                        elif distance <= step * (i - 4):
                            new_img.putpixel(pixel, (0, 0, 0, 255))
                            if random.random() <= 0.06:
                                direction = (
                                    (x - o[0]) / distance,
                                    (y - o[1] * 1.5) / distance,
                                )
                                dusts.append(Dot((x, y), direction))
                        elif distance <= step * (i + 2):
                            factor = (distance - step * (i - 11)) / (step * 12)
                            factor = max(0, min(1, factor))
                            factor *= 0.9 + 0.2 * random.random()
                            value = img.getpixel(pixel)
                            gray = (value[0] + value[1] + value[2]) / 3  # type: ignore
                            gray = round(gray * factor)
                            new_color = (gray, gray, gray, value[3])  # type: ignore
                            new_img.putpixel(pixel, new_color)
                        else:
                            continue
                dust_mask = make_dust(dusts, step, img.size)
                new_img.paste(dust_mask, (0, 0), dust_mask)
                return compose_frame(new_img)
            else:
                return compose_frame(make_dust(dusts, step, img.size))

        return make

    return make_gif_or_combined_gif(images, maker, 35, 0.08)


add_meme(
    "lucifina_squeeze",
    lucifina_squeeze,
    max_images=1,
    min_images=1,
    keywords=["路西菲娜捏"],
    date_created=datetime.datetime(2026, 6, 1),
    date_modified=datetime.datetime(2026, 6, 1),
)
