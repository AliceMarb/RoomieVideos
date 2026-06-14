# RoomieVideos

Scrapes Reddit roommate posts, classifies the poster into an HMTI persona, and generates a split-screen video transcript + pillow fight thumbnail.

## Pipeline

```
Reddit post → HMTI persona classification → 2-person dialogue transcript → pillow fight image
```

**Tools used:**
- **Reddit:** BeautifulSoup scraping of old.reddit.com (no API key needed)
- **Classification:** OpenAI `gpt-4o-mini`
- **Transcript:** OpenAI `gpt-4o` — 30s live argument between two personas
- **Image:** OpenAI `gpt-image-1` medium quality, using both avatar PNGs as style references
- **Audio:** ElevenLabs TTS, two voices stitched with pydub
- **Avatars:** 32 HMTI persona PNGs from RoomieScout

## Setup

1. **Create and activate the virtual environment:**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Add credentials to `.env`:**
   ```bash
   OPENAI_API_KEY=...
   ELEVENLABS_API_KEY=...       # only needed for --tts
   ELEVENLABS_VOICE_A=...       # voice ID for speaker A (default: George)
   ELEVENLABS_VOICE_B=...       # voice ID for speaker B (default: Rachel)
   ```

## Run the pipeline

```bash
# From a title only (no Reddit)
.venv/bin/python -m pipeline --title "My roommate ate my labeled leftovers and blamed the cat"

# From a title + body
.venv/bin/python -m pipeline --title "AITA for locking the fridge?" --body "My roommate keeps..."

# From Reddit
.venv/bin/python -m pipeline --subreddit roommatesfromhell --limit 5

# Force a specific opponent persona
.venv/bin/python -m pipeline --title "..." --vs-persona CODF

# With image generation
.venv/bin/python -m pipeline --title "..." --image

# With TTS audio
.venv/bin/python -m pipeline --title "..." --tts

# Full run
.venv/bin/python -m pipeline --subreddit roommatesfromhell --limit 5 --image --tts
```

## Output structure

**Per post/story** (`output/<post_id or slug>/`):

| File | Contents |
|------|----------|
| `post.json` | Reddit title, author, score, permalink, body, all comments (Reddit mode only) |
| `meta.json` | Classified persona, opponent persona, reasoning |
| `transcript.json` | Dialogue lines — `{"speaker": "A"/"B", "text": "..."}` — ready for ElevenLabs |
| `dialogue.mp3` | Stitched TTS audio (if `--tts`) |

**Images** (`animal_images/<A>_vs_<B>/`):

| File | Contents |
|------|----------|
| `<A>_vs_<B>.png` | Pillow fight scene generated using both avatar PNGs as style references |

## Scraper only

```bash
.venv/bin/python -m reddit_scraper roommatesfromhell --limit 25
```

Output: `output/posts.csv` and `output/comments.csv`.
