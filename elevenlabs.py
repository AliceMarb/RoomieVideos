import argparse
import mimetypes
import os
import sys
from pathlib import Path

import requests

API_BASE = "https://api.elevenlabs.io/v1"
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George
TTS_MODEL = "eleven_multilingual_v2"
STT_MODEL = "scribe_v1"


def _api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise EnvironmentError("ELEVENLABS_API_KEY environment variable is not set")
    return key


def _voice_id() -> str:
    return os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)


def text_to_speech(
    text: str,
    *,
    voice_id: str | None = None,
    speed: float = 1.2,
    stability: float = 0.5,
    similarity_boost: float = 0.75,
) -> bytes:
    vid = voice_id or _voice_id()
    resp = requests.post(
        f"{API_BASE}/text-to-speech/{vid}",
        headers={
            "xi-api-key": _api_key(),
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": text,
            "model_id": TTS_MODEL,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
            },
            "speed": speed,
        },
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"ElevenLabs TTS error {resp.status_code}: {resp.text}")
    return resp.content


def speech_to_text(
    audio_path: str,
    *,
    mime_type: str | None = None,
) -> str:
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    if mime_type is None:
        mime_type = mimetypes.guess_type(str(path))[0] or "audio/mpeg"

    with open(path, "rb") as f:
        resp = requests.post(
            f"{API_BASE}/speech-to-text",
            headers={"xi-api-key": _api_key()},
            files={"file": (path.name, f, mime_type)},
            data={"model_id": STT_MODEL, "tag_audio_events": "false"},
            timeout=60,
        )

    if not resp.ok:
        raise RuntimeError(f"ElevenLabs STT error {resp.status_code}: {resp.text}")
    return resp.json()["text"]


def main() -> None:
    parser = argparse.ArgumentParser(description="ElevenLabs TTS and STT")
    sub = parser.add_subparsers(dest="command", required=True)

    tts = sub.add_parser("tts", help="Text to speech")
    tts.add_argument("text", help="Text to synthesize")
    tts.add_argument("-o", "--output", default="output.mp3", help="Output file (default: output.mp3)")
    tts.add_argument("--speed", type=float, default=1.2, help="Speech speed (default: 1.2)")
    tts.add_argument("--voice-id", help="ElevenLabs voice ID override")

    stt = sub.add_parser("stt", help="Speech to text")
    stt.add_argument("audio", help="Path to audio file")

    args = parser.parse_args()

    try:
        if args.command == "tts":
            audio = text_to_speech(args.text, speed=args.speed, voice_id=args.voice_id)
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(audio)
            print(f"Saved: {out}")
        elif args.command == "stt":
            text = speech_to_text(args.audio)
            print(text)
    except (EnvironmentError, FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
