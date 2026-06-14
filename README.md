# RoomieVideos

Scrapes Reddit roommate posts, classifies the poster into an HMTI persona, and generates a TikTok-ready video with a fight animation, persona cards, and AI dialogue audio.

## Full pipeline

```
Reddit post → filter (real conflict only) → HMTI classification → dialogue transcript
  → pillow fight image (opt-in) → TTS audio → final TikTok video
```

**Tools used:**
- **Reddit:** BeautifulSoup scraping of old.reddit.com — no API key needed
- **Classification + transcript:** OpenAI `gpt-4o-mini` (classify) and `gpt-4o` (dialogue)
- **Image generation:** OpenAI `gpt-image-1` medium quality, with avatar PNGs as style references
- **Persona cards:** Generated with Pillow from the 16 v2 HMTI persona definitions
- **TTS audio:** ElevenLabs (two voices, one per speaker)
- **Video:** FFmpeg — gameplay background + fight video in middle + persona cards at top

## Setup

1. **Create the virtual environment:**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure credentials** — add to `.env`:
   ```
   OPENAI_API_KEY=...
   ELEVENLABS_API_KEY=...

   # Optional: override ElevenLabs voices
   ELEVENLABS_VOICE_A=...
   ELEVENLABS_VOICE_B=...
   ```

## Step 1 — Generate transcript (+ optional image)

```bash
# Scrape r/roommatesfromhell, skip non-conflict posts, generate transcripts
.venv/bin/python -m pipeline --subreddit roommatesfromhell --sort new --limit 10

# Also generate the pillow fight image (requires avatar PNGs in avatars/)
.venv/bin/python -m pipeline --subreddit roommatesfromhell --limit 10 --image

# Use a custom title instead of Reddit
.venv/bin/python -m pipeline --title "My roommate cranks the heat to 80 and won't pay utilities"

# Override the opponent persona
.venv/bin/python -m pipeline --subreddit roommatesfromhell --vs-persona CODF
```

### Output per post — `output/<post_id>/`

| File | Contents |
|------|----------|
| `post.json` | Full Reddit post + all comments |
| `transcript.json` | 2-person dialogue (`persona_a`, `persona_b`, `lines`) |
| `meta.json` | Classified persona, vs persona, reasoning, permalink |

Images go to `animal_images/<A>_vs_<B>/<A>_vs_<B>.png`.

## Step 2 — Compose final video

```bash
.venv/bin/python make_tiktok.py \
  --transcript output/<post_id>/transcript.json \
  --fight-video path/to/fight.mp4 \
  --gameplay path/to/minecraft.mp4 \
  -o output/<post_id>/tiktok.mp4
```

**Video layout (1080×1920):**
- **Background:** gameplay video looping full screen
- **Top:** two HMTI persona cards side by side (generated from persona data)
- **Middle:** fight video looping, centred
- **Audio:** ElevenLabs TTS of the dialogue transcript

## Transcript guidance

See [`pipeline/guidance.md`](pipeline/guidance.md) for the rules governing transcript tone and structure (hook → real conflict → punchline, audio-only constraints, etc.).
