from __future__ import annotations

import base64
import os
from pathlib import Path

from openai import OpenAI

from .personas import PERSONAS

AVATARS_DIR = Path(__file__).parent.parent / "avatars"

STYLE = (
    "Style: rounded animal mascot (no humans), soft 3D clay / polished vector sticker, "
    "Spotify Wrapped card vibe, bold pastel colors."
)


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

    prompt = (
        f"{STYLE} "
        f"A chaotic pillow fight between two cartoon roommate animals in a destroyed apartment. "
        f"Character 1 is a {animal_a} ({persona_a}) looking furious, wild-eyed, mid-swing with a pillow. "
        f"Character 2 is a {animal_b} ({persona_b}), equally angry, feathers and stuffing flying. "
        f"The room is a mess: clothes everywhere, overturned furniture, burst pillows, feathers in the air. "
        f"Expressive, slightly comic illustration. Keep the same character design as their avatar — "
        f"same animal, same cozy-mascot style, but angry and in battle mode. No text."
    )

    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="medium",
    )

    item = response.data[0]
    b64 = item.b64_json
    if not b64:
        raise RuntimeError("No image data in response")

    image_data = base64.b64decode(b64)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_data)

    return output_path
