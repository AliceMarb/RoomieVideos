from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from openai import OpenAI

from .classifier import ClassificationResult
from .personas import PERSONAS, PersonaMeta


@dataclass
class DialogueLine:
    speaker: str        # "A" or "B"
    persona_code: str
    persona_title: str
    text: str


@dataclass
class Transcript:
    persona_a: str
    persona_b: str
    lines: list[DialogueLine]

    def to_json(self) -> str:
        return json.dumps(
            {
                "persona_a": self.persona_a,
                "persona_b": self.persona_b,
                "lines": [asdict(l) for l in self.lines],
            },
            indent=2,
        )

    def save(self, path: Path) -> None:
        path.write_text(self.to_json(), encoding="utf-8")


def generate_transcript(
    title: str,
    selftext: str,
    classification: ClassificationResult,
    vs_persona: str = "CODF",
    *,
    client: OpenAI | None = None,
) -> Transcript:
    client = client or OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    meta_a: PersonaMeta = classification.meta
    meta_b: PersonaMeta = PERSONAS[vs_persona]
    code_a = classification.code
    code_b = vs_persona

    prompt = f"""You are writing a TikTok/YouTube Shorts video script. Two roommates are in the middle of an argument — this is the fight itself, not a recap.

CHARACTER A — {code_a} "{meta_a.title}": {meta_a.tagline}
Personality: {meta_a.description}
Conflict style: {meta_a.character_direction}

CHARACTER B — {code_b} "{meta_b.title}": {meta_b.tagline}
Personality: {meta_b.description}
Conflict style: {meta_b.character_direction}

The situation:
{title}
{selftext or ""}

Write the live argument. 60–75 words, ~30 seconds when read aloud.
- This is the active dispute — they are fighting RIGHT NOW
- Dramatic and funny — think reality TV confrontation energy
- Lines are very short and snappy (1–2 sentences max), rapid fire
- Each character's personality makes their arguing style totally different and clash hilariously
- End with a killer line, a dramatic exit, or an absurd mic-drop moment

Return ONLY a JSON array — no markdown, no explanation:
[
  {{"speaker": "A", "text": "..."}},
  {{"speaker": "B", "text": "..."}},
  ...
]"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.85,
    )

    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)

    # model may wrap in a key or return array directly
    if isinstance(data, dict):
        data = next(iter(data.values()))

    lines = []
    for item in data:
        speaker = item["speaker"].upper()
        code = code_a if speaker == "A" else code_b
        meta = meta_a if speaker == "A" else meta_b
        lines.append(DialogueLine(
            speaker=speaker,
            persona_code=code,
            persona_title=meta.title,
            text=item["text"],
        ))

    return Transcript(persona_a=code_a, persona_b=code_b, lines=lines)
