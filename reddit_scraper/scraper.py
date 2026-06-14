from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup, Tag

_BASE = "https://old.reddit.com"

_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
})

_DELAY = 2.0
_LAST_REQUEST = 0.0
_WARMED_UP = False


def _warmup() -> None:
    global _WARMED_UP, _LAST_REQUEST
    if _WARMED_UP:
        return
    _SESSION.get(f"{_BASE}/", timeout=10)
    _LAST_REQUEST = time.time()
    _WARMED_UP = True
    time.sleep(_DELAY)


def _get_html(url: str, params: dict | None = None) -> BeautifulSoup:
    global _LAST_REQUEST
    _warmup()

    elapsed = time.time() - _LAST_REQUEST
    if elapsed < _DELAY:
        time.sleep(_DELAY - elapsed)

    resp = _SESSION.get(url, params=params, timeout=15)
    _LAST_REQUEST = time.time()

    if resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", 10))
        print(f"  Rate limited, waiting {retry_after}s...")
        time.sleep(retry_after)
        return _get_html(url, params)

    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


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


def _parse_timestamp(ms_str: str) -> str:
    try:
        ts = int(ms_str) / 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except (ValueError, TypeError):
        return ""


def _extract_text(element: Tag | None) -> str:
    if element is None:
        return ""
    md_div = element.find("div", class_="md")
    if md_div:
        return md_div.get_text(separator="\n").strip()
    return element.get_text(separator="\n").strip()


def fetch_posts(
    subreddit_name: str,
    sort: str = "hot",
    limit: int = 25,
    time_filter: str = "week",
) -> list[PostData]:
    url = f"{_BASE}/r/{subreddit_name}/{sort}/"
    params: dict = {}
    if sort == "top":
        params["t"] = time_filter

    posts: list[PostData] = []
    after = None

    while len(posts) < limit:
        if after:
            params["after"] = after

        soup = _get_html(url, params)
        things = soup.find_all("div", class_=re.compile(r"\bthing\b"), attrs={"data-fullname": True})

        if not things:
            break

        for thing in things:
            if len(posts) >= limit:
                break

            fullname = thing.get("data-fullname", "")
            if not fullname.startswith("t3_"):
                continue

            post_id = fullname[3:]
            title_link = thing.find("a", class_=re.compile(r"\btitle\b"))
            title = title_link.get_text().strip() if title_link else ""

            score_el = thing.find("div", class_="score")
            score_text = thing.get("data-score", "0")

            timestamp = thing.get("data-timestamp", "0")
            permalink = thing.get("data-permalink", "")
            data_url = thing.get("data-url", "")
            comments_count = thing.get("data-comments-count", "0")
            author = thing.get("data-author", "[deleted]")
            domain = thing.get("data-domain", "")

            posts.append(
                PostData(
                    post_id=post_id,
                    subreddit=subreddit_name,
                    title=title,
                    author=author,
                    score=int(score_text),
                    upvote_ratio=0.0,
                    num_comments=int(comments_count),
                    created_utc=_parse_timestamp(timestamp),
                    url=data_url if data_url.startswith("http") else f"https://reddit.com{data_url}",
                    selftext="",
                    is_video=data_url.endswith(("/DASH_720.mp4", "/DASH_480.mp4")) or "v.redd.it" in data_url,
                    permalink=f"https://reddit.com{permalink}",
                )
            )

        next_btn = soup.find("span", class_="next-button")
        if next_btn:
            next_link = next_btn.find("a")
            if next_link and next_link.get("href"):
                after_match = re.search(r"after=([\w]+)", next_link["href"])
                after = after_match.group(1) if after_match else None
            else:
                after = None
        else:
            after = None

        if not after:
            break

    return posts


def fetch_post_selftext(permalink: str) -> str:
    if not permalink.startswith("http"):
        permalink = f"{_BASE}{permalink}"
    else:
        permalink = permalink.replace("https://reddit.com", _BASE)

    soup = _get_html(permalink)
    expando = soup.find("div", class_="expando")
    if expando:
        return _extract_text(expando.find("div", class_="usertext-body"))
    return ""


def fetch_comments(
    post_id: str,
    subreddit_name: str,
) -> list[CommentData]:
    url = f"{_BASE}/r/{subreddit_name}/comments/{post_id}/"
    soup = _get_html(url)

    comment_area = soup.find("div", class_="commentarea")
    if not comment_area:
        return []

    comments: list[CommentData] = []
    comment_things = comment_area.find_all(
        "div", class_=re.compile(r"\bthing\b"), attrs={"data-fullname": re.compile(r"^t1_")}
    )

    for thing in comment_things:
        fullname = thing.get("data-fullname", "")
        author = thing.get("data-author", "[deleted]")

        body_div = thing.find("div", class_="usertext-body", recursive=False) or \
                   thing.find("div", class_="entry").find("div", class_="usertext-body") if thing.find("div", class_="entry") else None
        body = _extract_text(body_div)

        score_span = thing.find("span", class_="score", attrs={"title": True})
        score = int(score_span["title"]) if score_span else 0

        time_tag = thing.find("time")
        created = time_tag.get("datetime", "") if time_tag else ""

        parent = thing.find_parent("div", class_=re.compile(r"\bthing\b"), attrs={"data-fullname": True})
        parent_id = parent.get("data-fullname", "") if parent else f"t3_{post_id}"

        nesting = thing.get("class", [])
        depth = 0
        for cls in nesting:
            m = re.match(r"noncollapsed", cls)
        p = thing
        while p:
            p = p.find_parent("div", class_=re.compile(r"\bchild\b"))
            if p:
                depth += 1

        comments.append(
            CommentData(
                comment_id=fullname[3:],
                post_id=post_id,
                subreddit=subreddit_name,
                author=author,
                body=body,
                score=score,
                created_utc=created,
                parent_id=parent_id,
                depth=depth,
            )
        )

    return comments
