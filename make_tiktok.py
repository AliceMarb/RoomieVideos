import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from pipeline.card_gen import generate_card_pair
from pipeline.tts import render_transcript
from pipeline.transcript import Transcript

load_dotenv()

WIDTH = 1080
HEIGHT = 1920


def _run_ffmpeg(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-2000:]}")


def _audio_duration(audio: Path) -> float:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
        capture_output=True, text=True,
    )
    return float(probe.stdout.strip())


def _composite(
    gameplay: Path,
    fight_video: Path,
    cards_image: Path,
    audio: Path,
    output: Path,
) -> None:
    """
    Layout (1080x1920):
      - Full background: gameplay video looping
      - Top (y=50):  two persona cards, scaled to ~1000px wide
      - Middle (y=680): fight video looping, scaled to ~960px wide, centred
    """
    print("Compositing video...")
    duration = _audio_duration(audio)

    card_w = WIDTH - 80        # 40px padding each side
    card_x = 40
    card_y = 50

    fight_w = int(WIDTH * 0.9)
    fight_x = (WIDTH - fight_w) // 2
    fight_y = card_y + 580     # below cards

    filter_complex = (
        # background: scale gameplay to fill full frame, loop
        f"[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT}[bg];"

        # persona cards — scale to card_w wide (static image)
        f"[1:v]scale={card_w}:-1[cards];"

        # fight video — scale to fight_w wide, loop
        f"[2:v]scale={fight_w}:-1[fight];"

        # overlay cards on background
        f"[bg][cards]overlay={card_x}:{card_y}[v1];"

        # overlay fight video
        f"[v1][fight]overlay={fight_x}:{fight_y}[outv]"
    )

    _run_ffmpeg([
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(gameplay),    # 0: background video (loops)
        "-loop", "1", "-i", str(cards_image),          # 1: persona cards (static PNG)
        "-stream_loop", "-1", "-i", str(fight_video),  # 2: fight video (loops)
        "-i", str(audio),                              # 3: dialogue audio
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "3:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration + 0.5),
        "-shortest",
        str(output),
    ])


def make_tiktok(
    transcript_path: Path,
    fight_video: Path,
    gameplay_video: Path,
    output_path: Path,
) -> Path:
    if not fight_video.exists():
        raise FileNotFoundError(f"Fight video not found: {fight_video}")
    if not gameplay_video.exists():
        raise FileNotFoundError(f"Gameplay video not found: {gameplay_video}")

    data = json.loads(transcript_path.read_text())
    transcript = Transcript(
        persona_a=data["persona_a"],
        persona_b=data["persona_b"],
        lines=[],
    )
    # rebuild lines from JSON
    from pipeline.transcript import DialogueLine
    for line in data["lines"]:
        transcript.lines.append(DialogueLine(
            speaker=line["speaker"],
            persona_code=data["persona_a"] if line["speaker"] == "A" else data["persona_b"],
            persona_title="",
            text=line["text"],
        ))

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # Generate persona cards
        print("Generating persona cards...")
        cards_img = tmp_dir / "cards.png"
        generate_card_pair(transcript.persona_a, transcript.persona_b, cards_img)
        print(f"  Cards: {transcript.persona_a} vs {transcript.persona_b}")

        # Render TTS audio
        print("Rendering dialogue audio...")
        audio_path = tmp_dir / "dialogue.mp3"
        render_transcript(transcript, audio_path)

        # Composite final video
        _composite(gameplay_video, fight_video, cards_img, audio_path, output_path)

    print(f"Done → {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compose final TikTok video: persona cards + fight image over gameplay"
    )
    parser.add_argument("--transcript", type=Path, required=True,
                        help="Path to transcript.json (from pipeline output/<post_id>/)")
    parser.add_argument("--fight-video", type=Path, required=True,
                        help="Path to fight video (e.g. from animal_videos/)")
    parser.add_argument("--gameplay", type=Path, required=True,
                        help="Path to gameplay background video (e.g. Minecraft .mp4)")
    parser.add_argument("-o", "--output", type=Path, default=Path("output/tiktok.mp4"))

    args = parser.parse_args()

    try:
        make_tiktok(args.transcript, args.fight_video, args.gameplay, args.output)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
