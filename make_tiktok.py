import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from elevenlabs import text_to_speech
from soundtrack import _get_video_duration

load_dotenv()

WIDTH = 1080
HEIGHT = 1920
HALF = HEIGHT // 2


def _run_ffmpeg(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")


def _tts(script: str, output: Path, speed: float) -> float:
    print("Generating voiceover...")
    audio = text_to_speech(script, speed=speed)
    output.write_bytes(audio)
    duration = _get_video_duration(str(output))
    print(f"  Audio: {duration:.1f}s")
    return duration


def _loop_video_with_audio(
    video: Path, audio: Path, output: Path, duration: float, volume: float
) -> None:
    print("Adding voiceover to content video...")
    _run_ffmpeg([
        "ffmpeg",
        "-stream_loop", "-1", "-i", str(video),
        "-i", str(audio),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-c:a", "aac",
        "-af", f"volume={volume}",
        "-t", str(duration),
        "-shortest",
        "-y", str(output),
    ])


def _composite_tiktok(
    gameplay: Path, content: Path, output: Path, duration: float
) -> None:
    print("Compositing TikTok split-screen...")
    _run_ffmpeg([
        "ffmpeg",
        "-i", str(gameplay),
        "-stream_loop", "-1", "-i", str(content),
        "-filter_complex",
        (
            f"[1:v]scale={WIDTH}:-1,pad={WIDTH}:{HALF}:(ow-iw)/2:(oh-ih)/2:black[top];"
            f"[0:v]crop=ih*{WIDTH}/{HALF}:ih,scale={WIDTH}:{HALF}[bot];"
            f"[top][bot]vstack=inputs=2[outv]"
        ),
        "-map", "[outv]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac",
        "-t", str(duration),
        "-y", str(output),
    ])


def make_tiktok(
    script: str,
    content_video: str,
    gameplay_video: str,
    output_path: str,
    *,
    speed: float = 1.3,
    volume: float = 1.0,
) -> Path:
    content = Path(content_video)
    gameplay = Path(gameplay_video)
    output = Path(output_path)

    if not content.exists():
        raise FileNotFoundError(f"Content video not found: {content}")
    if not gameplay.exists():
        raise FileNotFoundError(f"Gameplay video not found: {gameplay}")

    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        voice_mp3 = tmp_dir / "voice.mp3"
        content_with_audio = tmp_dir / "content_voiced.mp4"

        duration = _tts(script, voice_mp3, speed)
        _loop_video_with_audio(content, voice_mp3, content_with_audio, duration, volume)
        _composite_tiktok(gameplay, content_with_audio, output, duration)

    print(f"Done: {output}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a TikTok-style split-screen video with AI voiceover"
    )

    script_group = parser.add_mutually_exclusive_group(required=True)
    script_group.add_argument("--script", type=Path, help="Path to script text file")
    script_group.add_argument("--script-text", help="Inline script text")

    parser.add_argument("--content-video", required=True, help="Path to content/top video")
    parser.add_argument("--gameplay-video", required=True, help="Path to gameplay/bottom video")
    parser.add_argument("-o", "--output", default="output/tiktok.mp4", help="Output path (default: output/tiktok.mp4)")
    parser.add_argument("--speed", type=float, default=1.3, help="TTS speed (default: 1.3)")
    parser.add_argument("--volume", type=float, default=1.0, help="Voice volume (default: 1.0)")

    args = parser.parse_args()

    if args.script:
        if not args.script.exists():
            print(f"Error: Script file not found: {args.script}", file=sys.stderr)
            sys.exit(1)
        script = args.script.read_text().strip()
    else:
        script = args.script_text

    try:
        make_tiktok(
            script,
            args.content_video,
            args.gameplay_video,
            args.output,
            speed=args.speed,
            volume=args.volume,
        )
    except (FileNotFoundError, RuntimeError, EnvironmentError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
