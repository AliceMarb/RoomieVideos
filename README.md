# RoomieVideos

Scrapes Reddit roommate posts, classifies the poster into an HMTI persona, and generates a split-screen video transcript + pillow fight thumbnail.

## Pipeline

```
Reddit post → HMTI persona classification → 2-person dialogue transcript → pillow fight image
```

**Tools used:**
- **Reddit:** [PRAW](https://praw.readthedocs.io/) (Python Reddit API Wrapper) — official Reddit API, read-only
- **Classification + transcript:** OpenAI `gpt-4o-mini` (classify) and `gpt-4o` (dialogue)
- **Image generation:** OpenAI `gpt-image-1` at medium quality
- **Avatars:** 32 HMTI persona PNGs from RoomieScout

## Setup

1. **Create and activate the virtual environment:**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure credentials** — copy `.env` and fill in the Reddit keys:
   ```bash
   # .env already has the OpenAI key
   # Add your Reddit API credentials:
   REDDIT_CLIENT_ID=...
   REDDIT_CLIENT_SECRET=...
   ```

   Get Reddit credentials at https://www.reddit.com/prefs/apps — create a "script" app.

## Run the pipeline

```bash
# Scrape r/roommatesfromhell, classify top 10 posts, generate transcripts + images
.venv/bin/python -m pipeline roommatesfromhell --limit 10

# Use a specific sort
.venv/bin/python -m pipeline roommates --sort top --time-filter week --limit 5

# Single post by ID
.venv/bin/python -m pipeline roommatesfromhell --post-id abc123

# Set the "opponent" persona manually (otherwise picks natural opposite)
.venv/bin/python -m pipeline roommatesfromhell --vs-persona CODF

# Skip image generation
.venv/bin/python -m pipeline roommatesfromhell --no-image
```

### Output

Each post gets its own folder under `output/<post_id>/`:

| File | Contents |
|------|----------|
| `transcript.txt` | 2-person dialogue script, each character labeled with persona + tagline |
| `meta.json` | post ID, title, classified persona, reasoning, permalink |
| `pillow_fight_XXXX_vs_YYYY.png` | generated thumbnail — both avatars fighting in a messy room |

## Scraper only

To just scrape Reddit posts to CSV (no classification):

```bash
.venv/bin/python -m reddit_scraper roommatesfromhell --limit 25
.venv/bin/python -m reddit_scraper roommates --sort top --time-filter month --no-comments
```

Output: `output/posts.csv` and `output/comments.csv`.
