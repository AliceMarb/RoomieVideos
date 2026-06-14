from __future__ import annotations

import base64
import os
from pathlib import Path

from openai import OpenAI

from .personas import PERSONAS

AVATARS_DIR = Path(__file__).parent.parent / "avatars"


def generate_pillow_fight_image(
    persona_a: str,
    persona_b: str,
    output_path: Path,
    *,
    client: OpenAI | None = None,
) -> Path:
    if output_path.exists():
        return output_path

    client = client or OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    animal_a = PERSONAS[persona_a].animal if persona_a in PERSONAS else "cartoon animal"
    animal_b = PERSONAS[persona_b].animal if persona_b in PERSONAS else "cartoon animal"

    avatar_a = AVATARS_DIR / f"{persona_a}.png"
    avatar_b = AVATARS_DIR / f"{persona_b}.png"

    prompt = (
        f"Using these two characters exactly as they appear in the reference images, "
        f"draw them in a chaotic pillow fight inside a destroyed apartment. "
        f"Character 1 (the {animal_a}) is furious, wild-eyed, mid-swing with a pillow. "
        f"Character 2 (the {animal_b}) is equally angry, arms up, feathers and stuffing flying everywhere. "
        f"The room is trashed: clothes on the floor, overturned furniture, burst pillows, feathers in the air. "
        f"Preserve the exact art style, character proportions, colors, and design from the reference images — "
        f"same soft 3D clay / pastel sticker look, same faces, just angry and mid-battle. No text."
    )

    # Both avatar files must exist — never generate without style references
    for avatar_path in (avatar_a, avatar_b):
        if not avatar_path.exists():
            raise FileNotFoundError(
                f"Avatar not found: {avatar_path}. "
                f"Cannot generate image without reference — copy the avatar PNGs into avatars/."
            )

    print(f"  Reference images: {avatar_a.name}, {avatar_b.name}")

    import httpx

    api_key = os.environ["OPENAI_API_KEY"]
    files = [
        ("image[]", (avatar_a.name, avatar_a.read_bytes(), "image/png")),
        ("image[]", (avatar_b.name, avatar_b.read_bytes(), "image/png")),
        ("prompt", (None, prompt)),
        ("model", (None, "gpt-image-1")),
        ("size", (None, "1024x1024")),
        ("quality", (None, "medium")),
    ]
    resp = httpx.post(
        "https://api.openai.com/v1/images/edits",
        headers={"Authorization": f"Bearer {api_key}"},
        files=files,
        timeout=120,
    )
    resp.raise_for_status()
    b64 = resp.json()["data"][0]["b64_json"]

    if not b64:
        raise RuntimeError("No image data in response")

    image_data = base64.b64decode(b64)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_data)

    return output_path
