from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from .scraper import create_reddit_instance, fetch_comments, fetch_posts
from .writer import write_comments, write_posts


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="reddit-scraper",
        description="Scrape posts and comments from Reddit subreddits",
    )
    parser.add_argument(
        "subreddits",
        nargs="+",
        help="Subreddit names to scrape (without r/ prefix)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Number of posts per subreddit (default: 25)",
    )
    parser.add_argument(
        "--sort",
        choices=["hot", "new", "top", "rising"],
        default="hot",
        help="Sort order (default: hot)",
    )
    parser.add_argument(
        "--time-filter",
        choices=["hour", "day", "week", "month", "year", "all"],
        default="week",
        help="Time filter for 'top' sort (default: week)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--no-comments",
        action="store_true",
        help="Skip scraping comments",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = parse_args(argv)

    try:
        reddit = create_reddit_instance()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    total_posts = 0
    total_comments = 0

    for subreddit_name in args.subreddits:
        print(f"Scraping r/{subreddit_name} ({args.sort}, limit={args.limit})...")

        posts = fetch_posts(
            reddit,
            subreddit_name,
            sort=args.sort,
            limit=args.limit,
            time_filter=args.time_filter,
        )
        write_posts(posts, args.output)
        total_posts += len(posts)
        print(f"  {len(posts)} posts scraped")

        if not args.no_comments:
            subreddit_comments = 0
            for i, post in enumerate(posts, 1):
                comments = fetch_comments(reddit, post.post_id, subreddit_name)
                write_comments(comments, args.output)
                subreddit_comments += len(comments)
                print(
                    f"  [{i}/{len(posts)}] {len(comments)} comments from: {post.title[:60]}"
                )
            total_comments += subreddit_comments
            print(f"  {subreddit_comments} total comments from r/{subreddit_name}")

    print(f"\nDone. {total_posts} posts, {total_comments} comments -> {args.output}/")
