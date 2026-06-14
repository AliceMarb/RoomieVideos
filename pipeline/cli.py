from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .classifier import classify_post
from .image_gen import generate_pillow_fight_image
from .transcript import generate_transcript
from .tts import render_transcript


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="roomie-pipeline",
        description="Classify a roommate story → dialogue transcript + pillow fight image",
    )

    # Story input — either direct text or Reddit
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--title", help="Story title / situation (skips Reddit)")
    source.add_argument("--subreddit", help="Subreddit to scrape (without r/ prefix)")

    parser.add_argument("--body", default="", help="Story body text (used with --title)")

    # Reddit-only options
    parser.add_argument("--sort", choices=["hot", "new", "top", "rising"], default="hot")
    parser.add_argument("--limit", type=int, default=10, help="Posts to fetch (default: 10)")
    parser.add_argument("--post-id", help="Process a single specific post ID")

    # Shared options
    parser.add_argument(
        "--vs-persona",
        help="Persona code for the opponent roommate (e.g. CODF). "
             "Defaults to the natural opposite of the classified persona.",
    )
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--no-image", action="store_true", help="Skip image generation")
    parser.add_argument("--tts", action="store_true", help="Render transcript to MP3 via ElevenLabs")

    return parser.parse_args(argv)


_OPPOSITES: dict[str, str] = {
    "NPDS": "COHF", "NPDF": "COHS", "NPHS": "CODF", "NPHF": "CODS",
    "NODS": "CPHF", "NODF": "CPHS", "NOHS": "CPDF", "NOHF": "CPDS",
    "CPDS": "NOHF", "CPDF": "NOHS", "CPHS": "NODF", "CPHF": "NODS",
    "CODS": "NPHF", "CODF": "NPHS", "COHS": "NPDF", "COHF": "NPDS",
    # v1 codes
    "NPSD": "COFL", "NPSL": "COFD", "NPFD": "COSL", "NPFL": "COSD",
    "NOSD": "CPFL", "NOSL": "CPFD", "NOFD": "CPSL", "NOFL": "CPSD",
    "CPSD": "NOFL", "CPSL": "NOFD", "CPFD": "NOSL", "CPFL": "NOSD",
    "COSD": "NPFL", "COSL": "NPFD", "COFD": "NPSL", "COFL": "NPSD",
}


def _run_story(args: argparse.Namespace, client: OpenAI) -> None:
    title = args.title
    body = args.body or ""
    slug = title[:40].lower().replace(" ", "-").replace("/", "-")

    print(f"\n--- {title[:80]} ---")
    print("Classifying persona...", end=" ", flush=True)
    classification = classify_post(title, body, [], client=client)
    print(f"{classification.code} — {classification.meta.tagline}")
    print(f"  {classification.reasoning}")

    vs = args.vs_persona or _OPPOSITES.get(classification.code, "CODF")
    print(f"Generating transcript ({classification.code} vs {vs})...", end=" ", flush=True)
    transcript = generate_transcript(title, body, classification, vs, client=client)
    print("done")

    out_dir = args.output / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    transcript_path = out_dir / "transcript.json"
    transcript.save(transcript_path)
    print(f"  Transcript → {transcript_path}")

    if args.tts:
        audio_path = out_dir / "dialogue.mp3"
        print("Rendering audio via ElevenLabs...")
        render_transcript(transcript, audio_path)
        print(f"  Audio → {audio_path}")

    (out_dir / "meta.json").write_text(
        json.dumps({
            "title": title,
            "persona": classification.code,
            "persona_title": classification.meta.title,
            "vs_persona": vs,
            "reasoning": classification.reasoning,
        }, indent=2),
        encoding="utf-8",
    )

    if not args.no_image:
        image_path = out_dir / f"pillow_fight_{classification.code}_vs_{vs}.png"
        print(f"Generating pillow fight ({classification.code} vs {vs})...", end=" ", flush=True)
        generate_pillow_fight_image(classification.code, vs, image_path, client=client)
        print(f"done → {image_path}")


def _run_reddit(args: argparse.Namespace, client: OpenAI) -> None:
    from reddit_scraper.scraper import create_reddit_instance, fetch_comments, fetch_posts

    try:
        reddit = create_reddit_instance()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.post_id:
        posts = fetch_posts(reddit, args.subreddit, limit=1)
        posts = [p for p in posts if p.post_id == args.post_id] or posts[:1]
    else:
        posts = fetch_posts(reddit, args.subreddit, sort=args.sort, limit=args.limit)

    if not posts:
        print("No posts found.", file=sys.stderr)
        sys.exit(1)

    for post in posts:
        print(f"\n--- {post.title[:80]} ---")

        comments = fetch_comments(reddit, post.post_id, args.subreddit)
        top_comments = [c.body for c in sorted(comments, key=lambda c: -c.score)[:8]]

        print("Classifying persona...", end=" ", flush=True)
        classification = classify_post(post.title, post.selftext, top_comments, client=client)
        print(f"{classification.code} — {classification.meta.tagline}")
        print(f"  {classification.reasoning}")

        vs = args.vs_persona or _OPPOSITES.get(classification.code, "CODF")
        print(f"Generating transcript ({classification.code} vs {vs})...", end=" ", flush=True)
        transcript = generate_transcript(post.title, post.selftext, classification, vs, client=client)
        print("done")

        out_dir = args.output / post.post_id
        out_dir.mkdir(parents=True, exist_ok=True)

        transcript.save(out_dir / "transcript.json")
        print(f"  Transcript → {out_dir}/transcript.json")

        (out_dir / "meta.json").write_text(
            json.dumps({
                "post_id": post.post_id,
                "title": post.title,
                "persona": classification.code,
                "persona_title": classification.meta.title,
                "vs_persona": vs,
                "reasoning": classification.reasoning,
                "permalink": post.permalink,
            }, indent=2),
            encoding="utf-8",
        )

        if not args.no_image:
            image_path = out_dir / f"pillow_fight_{classification.code}_vs_{vs}.png"
            print(f"Generating pillow fight ({classification.code} vs {vs})...", end=" ", flush=True)
            generate_pillow_fight_image(classification.code, vs, image_path, client=client)
            print(f"done → {image_path}")


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = parse_args(argv)
    client = OpenAI()

    if args.title:
        _run_story(args, client)
    else:
        _run_reddit(args, client)

    print(f"\nDone. Results in {args.output}/")
