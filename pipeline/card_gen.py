"""Generate persona card images using Pillow, matching the RoomieScout ShareableAvatarCard design."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .personas import PERSONAS, PersonaMeta

AVATARS_DIR = Path(__file__).parent.parent / "avatars"

CARD_W = 400
CARD_H = 520
RADIUS = 40
FONT_PATH_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

# What each axis letter means
_AXIS_TRAITS: dict[str, str] = {
    "N": "Neat",       "C": "Casual",
    "P": "Private",    "O": "Open",
    "D": "Direct",     "H": "Harmonious",
    "S": "Structured", "F": "Flexible",
}


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
        font_hmti  = ImageFont.truetype(FONT_PATH_BOLD, 28)
        font_code  = ImageFont.truetype(FONT_PATH_BOLD, 52)
        font_title = ImageFont.truetype(FONT_PATH_BOLD, 22)
        font_tag   = ImageFont.truetype(FONT_PATH, 17)
        font_pill  = ImageFont.truetype(FONT_PATH_BOLD, 15)
    except OSError:
        font_hmti = font_code = font_title = font_tag = font_pill = ImageFont.load_default()

    badge_rgb = _hex(p.badge_text)
    badge_bg  = _hex(p.badge)
    accent    = _hex(p.accent)

    # "HMTI" label — bigger
    draw.text((32, 28), "HMTI", font=font_hmti, fill=(*accent, 220))

    # Code
    draw.text((32, 58), persona_code, font=font_code, fill=(*badge_rgb, 255))

    # Title
    draw.text((32, 116), meta.title, font=font_title, fill=(30, 30, 40, 255))

    # Avatar
    avatar_path = AVATARS_DIR / f"{persona_code}.png"
    avatar_y = 148
    avatar_h = 220
    if avatar_path.exists():
        avatar = Image.open(avatar_path).convert("RGBA")
        avatar.thumbnail((CARD_W - 40, avatar_h), Image.LANCZOS)
        ax = (CARD_W - avatar.width) // 2
        card.paste(avatar, (ax, avatar_y), avatar)

    # Tagline
    tagline = f'"{meta.tagline}"'
    draw.text((CARD_W // 2, avatar_y + avatar_h + 16), tagline, font=font_tag,
              fill=(*badge_rgb, 200), anchor="mm")

    # Axis trait pills — one per letter of the code
    pill_y = avatar_y + avatar_h + 46
    pills = [_AXIS_TRAITS[ch] for ch in persona_code if ch in _AXIS_TRAITS]

    pill_pad_x, pill_pad_y = 14, 7
    pill_h = font_pill.size + pill_pad_y * 2
    gaps = 8
    widths = [int(draw.textlength(t, font=font_pill)) + pill_pad_x * 2 for t in pills]
    total_w = sum(widths) + gaps * (len(pills) - 1)
    px = (CARD_W - total_w) // 2

    for trait, tw in zip(pills, widths):
        draw.rounded_rectangle(
            [(px, pill_y), (px + tw, pill_y + pill_h)],
            radius=pill_h // 2,
            fill=(*badge_bg, 255),
        )
        draw.text(
            (px + tw // 2, pill_y + pill_h // 2),
            trait, font=font_pill, fill=(*badge_rgb, 255), anchor="mm",
        )
        px += tw + gaps

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(output_path, "PNG")
    return output_path


def generate_card_pair(code_a: str, code_b: str, output_path: Path) -> Path:
    """Two cards side by side as a single wide PNG."""
    gap = 24
    pair = Image.new("RGBA", (CARD_W * 2 + gap, CARD_H), (0, 0, 0, 0))

    card_a_path = output_path.parent / f"card_{code_a}.png"
    card_b_path = output_path.parent / f"card_{code_b}.png"
    generate_card(code_a, card_a_path)
    generate_card(code_b, card_b_path)

    pair.paste(Image.open(card_a_path).convert("RGBA"), (0, 0))
    pair.paste(Image.open(card_b_path).convert("RGBA"), (CARD_W + gap, 0))

    pair.save(output_path, "PNG")
    return output_path
