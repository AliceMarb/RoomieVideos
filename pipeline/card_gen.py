"""Generate persona card images using Pillow, matching the RoomieScout ShareableAvatarCard design."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .personas import PERSONAS, PersonaMeta

AVATARS_DIR = Path(__file__).parent.parent / "avatars"

CARD_W = 480
CARD_H = 560
RADIUS = 48
FONT_PATH_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"


def _hex(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _gradient_bg(size: tuple[int, int], top_color: str, bottom_color: str) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", (w, h))
    t = _hex(top_color)
    b = _hex(bottom_color)
    for y in range(h):
        r = t[0] + int((b[0] - t[0]) * y / h)
        g = t[1] + int((b[1] - t[1]) * y / h)
        b_ = t[2] + int((b[2] - t[2]) * y / h)
        for x in range(w):
            img.putpixel((x, y), (r, g, b_, 255))
    return img


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255)
    return mask


def generate_card(persona_code: str, output_path: Path) -> Path:
    meta: PersonaMeta = PERSONAS[persona_code]
    p = meta.palette

    bg = _gradient_bg((CARD_W, CARD_H), p.bg_from, p.bg_to)
    card = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    card.paste(bg, mask=_rounded_mask((CARD_W, CARD_H), RADIUS))

    draw = ImageDraw.Draw(card)

    try:
        font_sm = ImageFont.truetype(FONT_PATH, 18)
        font_code = ImageFont.truetype(FONT_PATH_BOLD, 56)
        font_title = ImageFont.truetype(FONT_PATH_BOLD, 26)
        font_tag = ImageFont.truetype(FONT_PATH, 22)
    except OSError:
        font_sm = font_code = font_title = font_tag = ImageFont.load_default()

    badge_rgb = _hex(p.badge_text)

    # "HMTI" label
    draw.text((40, 36), "HMTI", font=font_sm, fill=(*_hex(p.accent), 180))

    # Code
    draw.text((40, 56), persona_code, font=font_code, fill=(*badge_rgb, 255))

    # Title
    draw.text((40, 120), meta.title, font=font_title, fill=(30, 30, 40, 255))

    # Avatar image
    avatar_path = AVATARS_DIR / f"{persona_code}.png"
    if avatar_path.exists():
        avatar = Image.open(avatar_path).convert("RGBA")
        avatar.thumbnail((280, 220), Image.LANCZOS)
        ax = (CARD_W - avatar.width) // 2
        card.paste(avatar, (ax, 158), avatar)

    # Tagline
    tagline = f'"{meta.tagline}"'
    draw.text((CARD_W // 2, 400), tagline, font=font_tag, fill=(*badge_rgb, 220),
              anchor="mm", align="center")

    # Trait badges
    badge_bg = _hex(p.badge)
    bx = 32
    by = 450
    for trait in meta.trait_badges[:3]:
        tw = draw.textlength(trait, font=font_sm) + 28
        draw.rounded_rectangle([(bx, by), (bx + tw, by + 32)], radius=16,
                                fill=(*badge_bg, 255))
        draw.text((bx + tw // 2, by + 16), trait, font=font_sm,
                  fill=(*badge_rgb, 255), anchor="mm")
        bx += int(tw) + 10

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(output_path, "PNG")
    return output_path


def generate_card_pair(code_a: str, code_b: str, output_path: Path) -> Path:
    """Two cards side by side as a single wide PNG."""
    gap = 24
    pair_w = CARD_W * 2 + gap
    pair_h = CARD_H

    pair = Image.new("RGBA", (pair_w, pair_h), (0, 0, 0, 0))

    card_a_path = output_path.parent / f"card_{code_a}.png"
    card_b_path = output_path.parent / f"card_{code_b}.png"
    generate_card(code_a, card_a_path)
    generate_card(code_b, card_b_path)

    pair.paste(Image.open(card_a_path).convert("RGBA"), (0, 0))
    pair.paste(Image.open(card_b_path).convert("RGBA"), (CARD_W + gap, 0))

    pair.save(output_path, "PNG")
    return output_path
