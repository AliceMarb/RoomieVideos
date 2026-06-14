from __future__ import annotations

import io
import os
import sys
from pathlib import Path

from pydub import AudioSegment

sys.path.insert(0, str(Path(__file__).parent.parent))
from elevenlabs import text_to_speech

from .transcript import Transcript

# Configure two voices via env vars, with ElevenLabs defaults as fallback.
# ELEVENLABS_VOICE_A — speaker A (the classified persona)
# ELEVENLABS_VOICE_B — speaker B (the opponent persona)
_DEFAULT_VOICE_A = "pNInz6obpgDQGcFmaJgB"  # Adam (pre-made, free tier)
_DEFAULT_VOICE_B = "EXAVITQu4vr4xnSDxMaL"  # Bella (pre-made, free tier)

_PAUSE_MS = 300  # silence between lines


def _voice(speaker: str) -> str:
    if speaker == "A":
        return os.environ.get("ELEVENLABS_VOICE_A", _DEFAULT_VOICE_A)
    return os.environ.get("ELEVENLABS_VOICE_B", _DEFAULT_VOICE_B)


def render_transcript(
    transcript: Transcript,
    output_path: Path,
    *,
    pause_ms: int = _PAUSE_MS,
) -> Path:
    silence = AudioSegment.silent(duration=pause_ms)
    combined = AudioSegment.empty()

    for i, line in enumerate(transcript.lines):
        print(f"  [{i + 1}/{len(transcript.lines)}] {line.speaker} ({line.persona_code}): {line.text[:60]}")
        audio_bytes = text_to_speech(line.text, voice_id=_voice(line.speaker))
        segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        if i > 0:
            combined += silence
        combined += segment

    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.export(str(output_path), format="mp3")
    return output_path
