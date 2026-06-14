from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .classifier import classify_post, is_conflict_story
from .image_gen import generate_pillow_fight_image
from .transcript import generate_transcript
from .tts import render_transcript


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="roomie-pipeline",
        description="Classify a roommate story → dialogue transcript + pillow fight image",
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--title", help="Story title / situation (skips Reddit)")
    source.add_argument("--subreddit", help="Subreddit to scrape (without r/ prefix)")

    parser.add_argument("--body", default="", help="Story body text (used with --title)")
    parser.add_argument("--sort", choices=["hot", "new", "top", "rising"], default="hot")
    parser.add_argument("--limit", type=int, default=10, help="Posts to fetch (default: 10)")
    parser.add_argument("--post-id", help="Process a single specific Reddit post ID")
    parser.add_argument("--vs-persona", help="Opponent persona code (e.g. CODF)")
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--image", action="store_true", help="Generate pillow fight image (gpt-image-1)")
    parser.add_argument("--tts", action="store_true", help="Render transcript to MP3 via ElevenLabs")

    return parser.parse_args(argv)


_OPPOSITES: dict[str, str] = {
    "NPDS": "COHF", "NPDF": "COHS", "NPHS": "CODF", "NPHF": "CODS",
    "NODS": "CPHF", "NODF": "CPHS", "NOHS": "CPDF", "NOHF": "CPDS",
    "CPDS": "NOHF", "CPDF": "NOHS", "CPHS": "NODF", "CPHF": "NODS",
    "CODS": "NPHF", "CODF": "NPHS", "COHS": "NPDF", "COHF": "NPDS",
}


def _print_transcript(transcript) -> None:
    print()
    for line in transcript.lines:
        label = f"{line.speaker} [{line.persona_code} — {line.persona_title}]"
        print(f"  {label}")
        print(f"    {line.text}")
    print()


def _process(
    title: str,
    body: str,
    permalink: str | None,
    out_dir: Path,
    args: argparse.Namespace,
    client: OpenAI,
) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    if permalink:
        print(f"  {permalink}")
    print(f"{'─' * 60}")

    print("Classifying persona...", end=" ", flush=True)
    classification = classify_post(title, body, [], client=client)
    vs = args.vs_persona or _OPPOSITES.get(classification.code, "CODF")
    print(f"{classification.code} ({classification.meta.title}) vs {vs}")
    print(f"  {classification.reasoning}")

    print("Generating transcript...", end=" ", flush=True)
    transcript = generate_transcript(title, body, classification, vs, client=client)
    print("done")

    _print_transcript(transcript)

    out_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = out_dir / "transcript.json"
    transcript.save(transcript_path)
    print(f"  Saved → {transcript_path}")
    print()
    print(transcript.to_json())

    (out_dir / "meta.json").write_text(
        json.dumps({
            "title": title,
            "permalink": permalink,
            "persona": classification.code,
            "persona_title": classification.meta.title,
            "vs_persona": vs,
            "reasoning": classification.reasoning,
        }, indent=2),
        encoding="utf-8",
    )

    if args.tts:
        audio_path = out_dir / "dialogue.mp3"
        print("Rendering audio via ElevenLabs...")
        render_transcript(transcript, audio_path)
        print(f"  Audio → {audio_path}")

    if args.image:
        fight_name = f"{classification.code}_vs_{vs}"
        image_path = Path("animal_images") / fight_name / f"{fight_name}.png"
        print(f"Generating pillow fight image...", end=" ", flush=True)
        generate_pillow_fight_image(classification.code, vs, image_path, client=client)
        print(f"done → {image_path}")


def _run_story(args: argparse.Namespace, client: OpenAI) -> None:
    title = args.title
    body = args.body or ""
    slug = title[:40].lower().replace(" ", "-").replace("/", "-")
    _process(title, body, None, args.output / slug, args, client)


def _run_reddit(args: argparse.Namespace, client: OpenAI) -> None:
    from reddit_scraper.scraper import fetch_comments, fetch_posts, fetch_post_selftext

    print(f"Fetching r/{args.subreddit} ({args.sort}, limit={args.limit})...")
    posts = fetch_posts(args.subreddit, sort=args.sort, limit=args.limit)

    if args.post_id:
        posts = [p for p in posts if p.post_id == args.post_id] or posts[:1]

    if not posts:
        print("No posts found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(posts)} posts.\n")

    for post in posts:
        out_dir = args.output / post.post_id

        transcript_path = out_dir / "transcript.json"
        if transcript_path.exists():
            print(f"  Skipping {post.post_id} — transcript already exists")
            continue

        body = fetch_post_selftext(post.permalink) if not post.selftext else post.selftext

        if not is_conflict_story(post.title, body, client=client):
            print(f"  Skipping {post.post_id} — not a real conflict story")
            continue

        comments = fetch_comments(post.post_id, post.subreddit)

        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "post.json").write_text(
            json.dumps({
                "post_id": post.post_id,
                "title": post.title,
                "author": post.author,
                "score": post.score,
                "permalink": post.permalink,
                "selftext": body,
                "comments": [
                    {"author": c.author, "score": c.score, "body": c.body}
                    for c in comments
                ],
            }, indent=2),
            encoding="utf-8",
        )
        print(f"  Saved post → {out_dir / 'post.json'}")

        _process(
            post.title,
            body,
            post.permalink,
            out_dir,
            args,
            client,
        )


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = parse_args(argv)
    client = OpenAI()

    if args.title:
        _run_story(args, client)
    else:
        _run_reddit(args, client)

    print(f"\nDone. Results in {args.output}/")
