import argparse
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

VEO_MODEL = "veo-3.1-generate-preview"
POLL_INTERVAL = 10


def _client() -> genai.Client:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)


def animate(
    image_path: str,
    prompt: str,
    output_path: str,
    *,
    duration: int = 8,
    aspect_ratio: str = "9:16",
) -> Path:
    image_file = Path(image_path)
    output = Path(output_path)

    if not image_file.exists():
        raise FileNotFoundError(f"Image not found: {image_file}")

    output.parent.mkdir(parents=True, exist_ok=True)

    client = _client()
    image = types.Image.from_file(location=str(image_file))

    print(f"Starting video generation ({duration}s, {aspect_ratio})...")
    operation = client.models.generate_videos(
        model=VEO_MODEL,
        prompt=prompt,
        image=image,
        config=types.GenerateVideosConfig(
            number_of_videos=1,
            duration_seconds=duration,
            aspect_ratio=aspect_ratio,
            enhance_prompt=True,
        ),
    )

    while not operation.done:
        print(f"  Generating... ({POLL_INTERVAL}s)")
        time.sleep(POLL_INTERVAL)
        operation = client.operations.get(operation)

    video = operation.response.generated_videos[0].video
    video.save(str(output))
    print(f"Done: {output}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Animate an image into a video using Veo 3.1")
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("prompt", help="Text prompt describing the animation")
    parser.add_argument("-o", "--output", default="output/animated.mp4", help="Output video path")
    parser.add_argument("--duration", type=int, choices=[4, 6, 8], default=8, help="Video duration in seconds (default: 8)")
    parser.add_argument("--aspect-ratio", choices=["16:9", "9:16"], default="9:16", help="Aspect ratio (default: 9:16)")

    args = parser.parse_args()

    try:
        animate(args.image, args.prompt, args.output, duration=args.duration, aspect_ratio=args.aspect_ratio)
    except (EnvironmentError, FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
