from __future__ import annotations

import json
import os
from dataclasses import dataclass

from openai import OpenAI

from .personas import DIMENSION_DESCRIPTIONS, PERSONA_CODES, PERSONAS, PersonaMeta


@dataclass
class ClassificationResult:
    code: str
    reasoning: str

    @property
    def meta(self) -> PersonaMeta:
        return PERSONAS[self.code]


def is_conflict_story(title: str, selftext: str, *, client: OpenAI | None = None) -> bool:
    client = client or OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = f"""Does this Reddit post describe a real, specific roommate conflict that actually happened to the poster?

Answer NO if it is:
- A hypothetical question ("would this be okay?", "how much is too much?")
- A general advice request with no specific incident
- A meta/subreddit post
- A rant with no specific conflict described

Answer YES only if it describes a specific real incident or ongoing conflict.

Title: {title}
Body: {selftext[:500] or "(none)"}

Reply with only YES or NO."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=5,
    )
    return response.choices[0].message.content.strip().upper().startswith("YES")


def classify_post(
    title: str,
    selftext: str,
    top_comments: list[str],
    *,
    client: OpenAI | None = None,
) -> ClassificationResult:
    client = client or OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    comment_block = "\n".join(f"- {c}" for c in top_comments[:8]) if top_comments else "(no comments)"

    prompt = f"""You are classifying the author of a Reddit roommate post into one of 16 HMTI personality types.

{DIMENSION_DESCRIPTIONS}

The 16 types are: {", ".join(PERSONA_CODES)}

Analyze the author's voice, values, and how they describe the situation — not their roommate.
Look at: how they handle conflict, how social they seem at home, how organized/structured they are,
and whether they're direct or harmony-seeking.

Reddit post title: {title}

Post body:
{selftext or "(no body text)"}

Top comments from others:
{comment_block}

Return ONLY valid JSON with this shape:
{{"code": "XXXX", "reasoning": "2-3 sentences explaining the classification"}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    data = json.loads(response.choices[0].message.content)
    code = data["code"].upper()

    if code not in PERSONAS:
        raise ValueError(f"Model returned unknown persona code: {code}")

    return ClassificationResult(code=code, reasoning=data.get("reasoning", ""))
