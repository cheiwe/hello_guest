"""
Stylised textures that PolyHaven does not have, painted from code to match the concepts:
wallpaper, rug runner, and pictures cut out of the concept art.

Needs Pillow and numpy (the Hunyuan3D environment has both):
    D:\\AI\\Hunyuan3D-2\\.venv\\Scripts\\python.exe Scripts/Tools/make_textures.py

Output: SourceArt/Textures/Stylized/T_<Name>_D.png
"""

import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONCEPT = os.path.join(ROOT, "SourceArt", "Concept")
OUT = os.path.join(ROOT, "SourceArt", "Textures", "Stylized")


def smooth_noise(size, scale, seed):
    """Low-frequency noise in 0..1 (upscaled random grid), tileable by wrapping."""
    rnd = np.random.default_rng(seed)
    cells = max(2, size // scale)
    grid = rnd.random((cells, cells))
    grid = np.tile(grid, (2, 2))[: cells + 1, : cells + 1]
    img = Image.fromarray((grid * 255).astype(np.uint8)).resize((size + scale, size + scale), Image.BICUBIC)
    return np.asarray(img.crop((0, 0, size, size)), dtype=np.float32) / 255.0


def age(image, seed, strength=0.18):
    """Uneven fading and grime so the surface does not look new."""
    arr = np.asarray(image, dtype=np.float32)
    side = max(image.width, image.height)
    n = smooth_noise(side, 128, seed) * 0.6 + smooth_noise(side, 32, seed + 1) * 0.4
    shade = 1.0 - strength * n[: image.height, : image.width]
    return Image.fromarray(np.clip(arr * shade[..., None], 0, 255).astype(np.uint8))


def flower(draw, cx, cy, s, petal, centre, leaf):
    """Small damask flower: four petals, a centre and two leaves."""
    for a in range(4):
        ang = math.pi / 2 * a + math.pi / 4
        px, py = cx + math.cos(ang) * s * 0.45, cy + math.sin(ang) * s * 0.45
        draw.ellipse((px - s * 0.32, py - s * 0.32, px + s * 0.32, py + s * 0.32), fill=petal)
    draw.ellipse((cx - s * 0.2, cy - s * 0.2, cx + s * 0.2, cy + s * 0.2), fill=centre)
    for side in (-1, 1):
        lx = cx + side * s * 0.9
        draw.ellipse((lx - s * 0.35, cy + s * 0.5 - s * 0.15, lx + s * 0.35, cy + s * 0.5 + s * 0.15), fill=leaf)


def wallpaper(size=1024):
    """Cream striped wallpaper with rows of small roses (Hallway, Safe_Room, Apple_Room)."""
    img = Image.new("RGB", (size, size), (214, 192, 150))
    d = ImageDraw.Draw(img)
    stripe = size // 8
    for i in range(8):
        x = i * stripe
        d.rectangle((x, 0, x + stripe // 2 - 1, size), fill=(205, 181, 138))
        d.line((x, 0, x, size), fill=(188, 160, 118), width=3)
    # Small muted roses in columns: in the darker stripes, offset every other row.
    rows = 14
    for r in range(rows):
        for c in range(8):
            cx = c * stripe + stripe * 0.25
            cy = (r + (0.5 if c % 2 else 0.0)) * size / rows
            flower(d, cx, cy % size, stripe * 0.17, (165, 104, 86), (125, 72, 58), (128, 122, 88))
            # Thin vine between the roses.
            d.line((cx, cy % size + stripe * 0.2, cx, (cy + size / rows) % size - stripe * 0.2), fill=(150, 130, 95), width=2)
    img = img.filter(ImageFilter.GaussianBlur(0.9))
    return age(img, 11)


def rug(width=1024, height=512):
    """Faded runner: border, inner band and a medallion pattern (planar UVs 0..1 on the rug)."""
    img = Image.new("RGB", (width, height), (120, 52, 40))
    d = ImageDraw.Draw(img)
    b = height // 10
    d.rectangle((b // 2, b // 2, width - b // 2, height - b // 2), outline=(200, 170, 110), width=b // 3)
    d.rectangle((b, b, width - b, height - b), fill=(60, 70, 85))
    d.rectangle((b * 1.4, b * 1.4, width - b * 1.4, height - b * 1.4), outline=(190, 150, 90), width=6)
    for i in range(5):
        cx = width * (i + 0.5) / 5
        cy = height / 2
        r = height * 0.22
        d.polygon([(cx - r, cy), (cx, cy - r), (cx + r, cy), (cx, cy + r)], fill=(140, 60, 45), outline=(200, 170, 110))
        d.ellipse((cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35), fill=(200, 170, 110))
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    return age(img, 21, 0.3)


def cardboard(size=1024):
    """Brown corrugated cardboard: flutes as faint stripes, darker stains (Workshop, Bulb_room boxes)."""
    img = Image.new("RGB", (size, size), (168, 124, 80))
    d = ImageDraw.Draw(img)
    for y in range(0, size, 12):
        d.line((0, y, size, y), fill=(160, 117, 75), width=4)
    rnd = random.Random(31)
    for _ in range(14):
        x, y, r = rnd.randrange(size), rnd.randrange(size), rnd.randrange(30, 120)
        d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=(150, 108, 68))
    img = img.filter(ImageFilter.GaussianBlur(2.0))
    return age(img, 33, 0.22)


def chain_link(size=512, cells=4):
    """Diamond wire mesh with alpha (opacity mask): one tile = 0.5 m of fence."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    step = size // cells
    for i in range(-cells, cells * 2 + 1):
        x = i * step
        d.line((x, 0, x + size, size), fill=(150, 150, 145, 255), width=5)
        d.line((x, size, x + size, 0), fill=(150, 150, 145, 255), width=5)
    return img


def globe_map(width=1024, height=512):
    """Old globe: faded blue-green sea, ochre continents from thresholded noise, a grid of meridians."""
    n = smooth_noise(width, 96, 41)[:height, :] * 0.65 + smooth_noise(width, 40, 42)[:height, :] * 0.35
    land = n > 0.55
    sea = np.array((92, 140, 140), dtype=np.float32)
    ground = np.array((196, 168, 100), dtype=np.float32)
    arr = np.where(land[..., None], ground, sea)
    img = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(img)
    for i in range(1, 12):
        d.line((i * width / 12, 0, i * width / 12, height), fill=(70, 100, 100), width=1)
    for i in range(1, 6):
        d.line((0, i * height / 6, width, i * height / 6), fill=(70, 100, 100), width=1)
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    return age(img, 43, 0.25)


def caution_tape(width=2048, height=128):
    """Yellow police tape with black stripes and CAUTION lettering (Safe_Room concept)."""
    from PIL import ImageFont
    img = Image.new("RGB", (width, height), (238, 200, 40))
    d = ImageDraw.Draw(img)
    stripe = height
    for x in range(-height, width + height, stripe * 2):
        d.polygon([(x, height), (x + stripe * 0.6, 0), (x + stripe * 1.1, 0), (x + stripe * 0.5, height)], fill=(25, 22, 18))
    try:
        font = ImageFont.truetype("arialbd.ttf", int(height * 0.62))
    except OSError:
        font = ImageFont.load_default()
    for i in range(4):
        cx = width * (i + 0.5) / 4
        box = (cx - height * 2.2, height * 0.08, cx + height * 2.2, height * 0.92)
        d.rectangle(box, fill=(238, 200, 40))
        d.text((cx, height / 2), "CAUTION", font=font, fill=(25, 22, 18), anchor="mm")
    return age(img, 51, 0.15)


def blood_trail(width=1024, height=256):
    """Smeared dark red drag trail with alpha (decal on the upstairs floor)."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(61)
    for k in range(5):
        y = height / 2 + rnd.uniform(-30, 30)
        pts = []
        for x in range(0, width + 64, 64):
            y += rnd.uniform(-10, 10)
            pts.append((x, y))
        d.line(pts, fill=(90, 8, 6, 230), width=int(rnd.uniform(18, 46)))
    for _ in range(25):
        x, y, r = rnd.uniform(0, width), height / 2 + rnd.uniform(-90, 90), rnd.uniform(4, 16)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(80, 6, 4, 220))
    return img.filter(ImageFilter.GaussianBlur(3))


def portrait_clue():
    """
    The puzzle painting: the man at his desk with an inkwell, a book and a globe, left to right
    (Docs/PLAN.md). The concept portrait only has the inkwell, so the book and the globe are taken from
    the table in the same concept and painted onto the desk.
    """
    base = crop_concept("Safe_Room.jpg", (345, 255, 675, 760), (512, 768))
    src = Image.open(os.path.join(CONCEPT, "Safe_Room.jpg")).convert("RGB")

    def cutout(box, size):
        part = src.crop(box).resize(size, Image.LANCZOS)
        # Soft oval mask so the pasted object blends into the painting.
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).ellipse((2, 2, size[0] - 2, size[1] - 2), fill=255)
        return part, mask.filter(ImageFilter.GaussianBlur(4))

    book, book_mask = cutout((372, 950, 612, 1032), (150, 52))
    globe, globe_mask = cutout((640, 743, 833, 1011), (112, 156))
    base.paste(book, (150, 655), book_mask)
    base.paste(globe, (392, 540), globe_mask)
    return base.filter(ImageFilter.GaussianBlur(0.4))


def bleed_figures(name, threshold=40, iterations=35):
    """
    A character sheet with the background replaced by the figures' own colours grown outwards. Faces of a
    3D model projected onto the sheet near the silhouette then pick up clothing colour instead of the
    grey background.
    """
    import cv2

    img = np.asarray(Image.open(os.path.join(CONCEPT, name)).convert("RGB"))
    # Background colour per row from the left margin (the sheet has a vertical gradient).
    bg_row = np.median(img[:, :12].astype(np.float32), axis=1)
    diff = np.linalg.norm(img.astype(np.float32) - bg_row[:, None, :], axis=2)
    figure = (diff > threshold).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    figure = cv2.morphologyEx(figure, cv2.MORPH_OPEN, kernel)
    figure = cv2.morphologyEx(figure, cv2.MORPH_CLOSE, kernel)
    # Drop the drawn outline (a few pixels at the silhouette) so it is not smeared onto the sides.
    inner = cv2.erode(figure, kernel, iterations=1)
    band = cv2.dilate(figure, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * iterations + 1, 2 * iterations + 1))) & (1 - inner)
    out = cv2.inpaint(np.ascontiguousarray(img[..., ::-1]), band * 255, 6, cv2.INPAINT_TELEA)[..., ::-1]
    return Image.fromarray(out)


def crop_concept(name, box, size=(512, 640)):
    """A region of a concept picture as a texture (old photos, paintings)."""
    img = Image.open(os.path.join(CONCEPT, name)).convert("RGB").crop(box)
    return img.resize(size, Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    outputs = {
        "T_Wallpaper_Rose_D": wallpaper(),
        "T_Rug_Runner_D": rug(),
        "T_Cardboard_D": cardboard(),
        "T_ChainLink_D": chain_link(),
        "T_Globe_D": globe_map(),
        "T_CautionTape_D": caution_tape(),
        "T_BloodTrail_D": blood_trail(),
        # Golden apple paintings from Apple_Room (canvas only, without the painted frames).
        "T_Painting_Apple1_D": crop_concept("Apple_Room.jpg", (830, 360, 995, 555), (512, 512)),
        "T_Painting_Apple2_D": crop_concept("Apple_Room.jpg", (1090, 295, 1270, 525), (512, 640)),
        "T_Painting_Apple3_D": crop_concept("Apple_Room.jpg", (1375, 270, 1525, 460), (512, 640)),
        "T_Painting_Apple4_D": crop_concept("Apple_Room.jpg", (1640, 260, 1840, 455), (512, 512)),
        "T_Painting_Apple5_D": crop_concept("Apple_Room.jpg", (1520, 575, 1835, 925), (640, 640)),
        "T_Painting_Apple6_D": crop_concept("Apple_Room.jpg", (785, 690, 865, 830), (384, 640)),
        # The puzzle clue: the mustached man at his desk with an inkwell, a book and a globe (Safe_Room).
        "T_Painting_Portrait_D": portrait_clue(),
        # Vitec's colour texture: the concept sheet with the figures' colours bled into the background.
        "T_Vitec_Sheet_D": bleed_figures("Vitec_Play.jpg"),
        # Old photos from Hallway_01 (pixel boxes in the original 2752x1536 image).
        "T_Photo_Couple_D": crop_concept("Hallway_01.jpg", (160, 318, 328, 716)),
        "T_Photo_Woman_D": crop_concept("Hallway_01.jpg", (2485, 350, 2628, 742)),
        # Linear white: default roughness map of the master material (imported without sRGB).
        "T_Default_Linear": Image.new("RGB", (8, 8), (255, 255, 255)),
    }
    for name, img in outputs.items():
        path = os.path.join(OUT, name + ".png")
        img.save(path)
        print("saved", path, img.size)


if __name__ == "__main__":
    main()
