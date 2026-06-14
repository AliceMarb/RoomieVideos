from __future__ import annotations

import csv
from dataclasses import asdict, fields
from pathlib import Path

from .scraper import CommentData, PostData

POST_FIELDS = [f.name for f in fields(PostData)]
COMMENT_FIELDS = [f.name for f in fields(CommentData)]


def write_posts(posts: list[PostData], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "posts.csv"

    file_exists = path.exists() and path.stat().st_size > 0

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=POST_FIELDS)
        if not file_exists:
            writer.writeheader()
        for post in posts:
            writer.writerow(asdict(post))

    return path


def write_comments(comments: list[CommentData], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "comments.csv"

    file_exists = path.exists() and path.stat().st_size > 0

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COMMENT_FIELDS)
        if not file_exists:
            writer.writeheader()
        for comment in comments:
            writer.writerow(asdict(comment))

    return path
