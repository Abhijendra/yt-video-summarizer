# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the Flask dev server (port 5000)
python app.py

# Or via Docker
docker build -t yt-summarizer .
docker run -p 5000:5000 --env-file .env yt-summarizer
```

The app exposes:
- `GET /` — web UI (`templates/index.html`)
- `GET /health` — health check
- `POST /fetch` — accepts raw YouTube URL in the request body, returns JSON with `generated_summary`

## Environment

Copy `.env` and populate:
```
GROQ_API_KEY=...
OPENAI_API_KEY=...   # unused at runtime, kept for reference
```

The `Summarizer` class reads `GROQ_API_KEY` at module load time (not via constructor injection), so the `.env` must be loaded before `services/summarizer` is imported — `app.py` handles this via `load_dotenv(override=True)` before the import.

## Architecture

```
app.py                  Flask entry point, route handlers
log_config.py           Configures root logger (StreamHandler, INFO level)
services/
  youtube_service.py    Fetches transcript via youtube-transcript-api
  summarizer.py         Map-reduce summarization over transcript chunks
templates/index.html    Single-page UI
static/js/app.js        Calls POST /fetch, renders result into textarea
```

### Summarization pipeline (map-reduce)

1. `youtube_service.get_ytvideo_transcript` fetches the raw transcript string.
2. `clean_transcript` strips filler words ("um", "uh", etc.).
3. `chunk_text` tokenizes with `tiktoken` (`cl100k_base`) and splits into 1200-token windows with 100-token overlap.
4. Each chunk is independently summarized by the LLM (`summarize_chunk`) with a 1.5 s sleep between calls to respect rate limits.
5. All chunk summaries are concatenated and sent to the LLM again to produce the final combined summary.

The LLM backend is Groq's OpenAI-compatible endpoint (`https://api.groq.com/openai/v1`) using model `openai/gpt-oss-120b`. The `Summarizer` constructor accepts overrides for model, API key, and base URL, making it straightforward to swap providers.

### Key constraints

- The frontend sends the raw URL as plain text in the POST body (not JSON). `app.py` decodes it with `request.get_data().decode("utf-8")`.
- `get_video_id_from_link` only handles the `?v=` query-param format; shortened `youtu.be` URLs will fail.
- Final summary uses `<br>` for line breaks (not `\n`) because it is rendered inside an HTML `<textarea>`.
