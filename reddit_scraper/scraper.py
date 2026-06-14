from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

import praw
from praw.models import MoreComments


@dataclass
class PostData:
    post_id: str
    subreddit: str
    title: str
    author: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: str
    url: str
    selftext: str
    is_video: bool
    permalink: str


@dataclass
class CommentData:
    comment_id: str
    post_id: str
    subreddit: str
    author: str
    body: str
    score: int
    created_utc: str
    parent_id: str
    depth: int


def create_reddit_instance() -> praw.Reddit:
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "reddit-scraper/0.1.0")

    if not client_id or not client_secret:
        raise ValueError(
            "REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set. "
            "Copy .env.example to .env and fill in your credentials."
        )

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def _format_timestamp(utc_timestamp: float) -> str:
    return datetime.fromtimestamp(utc_timestamp, tz=timezone.utc).isoformat()


def fetch_posts(
    reddit: praw.Reddit,
    subreddit_name: str,
    sort: str = "hot",
    limit: int = 25,
    time_filter: str = "week",
) -> list[PostData]:
    subreddit = reddit.subreddit(subreddit_name)

    if sort == "top":
        submissions = subreddit.top(limit=limit, time_filter=time_filter)
    elif sort == "new":
        submissions = subreddit.new(limit=limit)
    elif sort == "rising":
        submissions = subreddit.rising(limit=limit)
    else:
        submissions = subreddit.hot(limit=limit)

    posts = []
    for submission in submissions:
        posts.append(
            PostData(
                post_id=submission.id,
                subreddit=subreddit_name,
                title=submission.title,
                author=str(submission.author) if submission.author else "[deleted]",
                score=submission.score,
                upvote_ratio=submission.upvote_ratio,
                num_comments=submission.num_comments,
                created_utc=_format_timestamp(submission.created_utc),
                url=submission.url,
                selftext=submission.selftext,
                is_video=submission.is_video,
                permalink=f"https://reddit.com{submission.permalink}",
            )
        )

    return posts


def fetch_comments(
    reddit: praw.Reddit,
    post_id: str,
    subreddit_name: str,
) -> list[CommentData]:
    submission = reddit.submission(id=post_id)
    submission.comments.replace_more(limit=0)

    comments = []
    for comment in submission.comments.list():
        if isinstance(comment, MoreComments):
            continue

        comments.append(
            CommentData(
                comment_id=comment.id,
                post_id=post_id,
                subreddit=subreddit_name,
                author=str(comment.author) if comment.author else "[deleted]",
                body=comment.body,
                score=comment.score,
                created_utc=_format_timestamp(comment.created_utc),
                parent_id=comment.parent_id,
                depth=comment.depth,
            )
        )

    return comments
