import argparse
import base64
import sys
from pathlib import Path

import requests


def animate_wan(
    image_path: str,
    prompt: str,
    output_path: str,
    *,
    endpoint_url: str,
    num_frames: int = 81,
    seed: int = 42,
) -> Path:
    image = Path(image_path)
    output = Path(output_path)

    if not image.exists():
        raise FileNotFoundError(f"Image not found: {image}")

    output.parent.mkdir(parents=True, exist_ok=True)

    image_b64 = base64.b64encode(image.read_bytes()).decode()

    print(f"Sending to Wan2.2 ({endpoint_url})...")
    resp = requests.post(
        endpoint_url,
        json={
            "image_b64": image_b64,
            "prompt": prompt,
            "num_frames": num_frames,
            "seed": seed,
        },
        timeout=900,
    )

    if not resp.ok:
        raise RuntimeError(f"Wan2.2 API error {resp.status_code}: {resp.text}")

    video_b64 = resp.json()["video_b64"]
    video_bytes = base64.b64decode(video_b64)
    output.write_bytes(video_bytes)
    print(f"Done: {output} ({len(video_bytes) / 1024 / 1024:.1f} MB)")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Animate an image using Wan2.2 on Modal")
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("prompt", help="Animation prompt")
    parser.add_argument("-o", "--output", default="output/wan_animated.mp4", help="Output path")
    parser.add_argument("--endpoint", required=True, help="Modal endpoint URL")
    parser.add_argument("--num-frames", type=int, default=81, help="Number of frames (default: 81, ~5s at 16fps)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    try:
        animate_wan(
            args.image, args.prompt, args.output,
            endpoint_url=args.endpoint,
            num_frames=args.num_frames,
            seed=args.seed,
        )
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
