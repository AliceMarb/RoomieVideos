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
                "lines": [{"speaker": l.speaker, "text": l.text} for l in self.lines],
            },
            indent=2,
        )

    def save(self, path: Path) -> None:
        path.write_text(self.to_json(), encoding="utf-8")


def generate_transcript(
    title: str,
    story: str,
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
{(title + ". " + story).strip() if story else title}

Write the live argument. 60–75 words, ~30 seconds when read aloud.
- This is the active dispute — they are fighting RIGHT NOW
- Lines are very short and snappy (1–2 sentences max), rapid fire
- NEVER use the other person's name or refer to them as "A" or "B" — speak directly without addressing them by any name
- AUDIO ONLY: the audience cannot see anything. Every line must make sense with ears alone — no references to things only visible in the room
- FIRST LINE must be a direct accusation: state exactly what the other person did wrong, with anger and energy. NOT a question, NOT a metaphor, NOT a joke — a clear statement of the problem. (e.g. "Your cat has turned this apartment into a BIOHAZARD and you don't even care!" not "Did a cheese factory explode in your room?")
- Structure: ACCUSATION (line 1) → ESCALATING FIGHT (lines 2–8) → UNHINGED ENDING (final 2–3 lines)
- The middle must be REAL conflict — frustrated, specific, escalating. NOT jokes.
- The ending goes OFF THE RAILS — someone completely loses it. Creative, unhinged insults. Weird. Absurd. Real Housewives table-flip energy.
- BAD ending: "Deal. But no pets invited." (too tidy, too friendly)
- GOOD ending: "You're not a roommate, you're a FERAL RACCOON in a human costume!" or "I have lived with mould that had more self-awareness than you!"
- NO RESOLUTION: the fight does NOT end with agreement or compromise. It ends mid-argument — someone storms off, delivers a final unhinged insult, or drops a mic. No "deal", no peace made.

Return ONLY this exact JSON structure — no markdown, no explanation:
{{"lines": [{{"speaker": "A", "text": "..."}}, {{"speaker": "B", "text": "..."}}, ...]}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.85,
    )

    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)

    # normalise — model should return {"lines": [...]} but handle variations
    if isinstance(data, list):
        items = data
    elif "lines" in data:
        items = data["lines"]
    else:
        # grab the first list value
        items = next(v for v in data.values() if isinstance(v, list))

    lines = []
    for item in items:
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
