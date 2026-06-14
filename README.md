# RoomieVideos

Crazy funny videos with HMTI classification.

## Reddit Scraper

Scrape posts and comments from Reddit subreddits to CSV files.

### Setup

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Get Reddit API credentials:**
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app"
   - Select "script" as the app type
   - Note the `client_id` (under the app name) and `client_secret`

3. **Configure credentials:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`.

### Usage

```bash
# Scrape 25 hot posts (+ comments) from a subreddit
python -m reddit_scraper funny

# Multiple subreddits, custom limit
python -m reddit_scraper funny videos memes --limit 50

# Top posts from the past month, no comments
python -m reddit_scraper wallstreetbets --sort top --time-filter month --no-comments

# Custom output directory
python -m reddit_scraper python --output ./data --limit 10
```

### Output

Two CSV files are created in the output directory (default: `./output/`):

- **posts.csv** — post ID, subreddit, title, author, score, upvote ratio, comment count, timestamp, URL, selftext, is_video, permalink
- **comments.csv** — comment ID, post ID, subreddit, author, body, score, timestamp, parent ID, depth
