import argparse
import json
import subprocess
import sys
from pathlib import Path


def _get_video_duration(video_path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def add_soundtrack(
    video_path: str,
    audio_path: str,
    output_path: str,
    *,
    audio_volume: float = 1.0,
) -> Path:
    video = Path(video_path)
    audio = Path(audio_path)
    output = Path(output_path)

    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")
    if not audio.exists():
        raise FileNotFoundError(f"Audio not found: {audio}")

    output.parent.mkdir(parents=True, exist_ok=True)

    duration = _get_video_duration(str(video))

    cmd = [
        "ffmpeg",
        "-i", str(video),
        "-stream_loop", "-1",
        "-i", str(audio),
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac",
        "-af", f"volume={audio_volume}",
        "-t", str(duration),
        "-shortest",
        "-y",
        str(output),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a soundtrack to a video")
    parser.add_argument("video", help="Path to the input video file")
    parser.add_argument("audio", help="Path to the audio/soundtrack file")
    parser.add_argument("output", help="Path for the output video file")
    parser.add_argument(
        "--volume",
        type=float,
        default=1.0,
        help="Audio volume multiplier (default: 1.0)",
    )
    args = parser.parse_args()

    try:
        out = add_soundtrack(args.video, args.audio, args.output, audio_volume=args.volume)
        print(f"Done: {out}")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
