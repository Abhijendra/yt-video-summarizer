# YouTube Video Summarizer

A Flask web app that fetches the transcript of any YouTube video and generates a structured summary using a large language model via [Groq](https://groq.com/).

## How it works

1. You paste a YouTube video URL into the web UI.
2. The backend extracts the video ID, fetches the auto-generated transcript, and cleans it (strips filler words like "um", "uh", etc.).
3. The transcript is tokenized with `tiktoken` and split into **1,200-token chunks with 100-token overlap**.
4. Each chunk is independently summarized by the LLM (map step), with a 1.5 s delay between calls to stay within Groq's rate limits.
5. All chunk summaries are combined in a second LLM call to produce the final summary (reduce step).
6. The summary is returned to the UI and displayed in a read-only textarea.

## Requirements

- Python 3.12+
- A [Groq API key](https://console.groq.com/)

## Setup

```bash
# Clone and enter the repo
git clone <repo-url>
cd yt-video-summarizer

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env   # or create .env manually
```

Populate `.env`:

```
GROQ_API_KEY=your_groq_api_key_here
```

`SECRET_KEY` is optional (Flask session secret); a default is used if omitted.

## Running

```bash
# Activate the venv first
source .venv/bin/activate

# Start the development server on port 5000
python app.py
```

Open `http://localhost:5000` in your browser.

## Docker

```bash
# Build
docker build -t yt-summarizer .

# Run (pass the .env file so the API key is available)
docker run -p 5000:5000 --env-file .env yt-summarizer
```

## API

### `GET /`
Returns the web UI (`templates/index.html`).

### `GET /health`
Health check. Returns:
```json
{"status": "healthy"}
```

### `POST /fetch`
Accepts the raw YouTube URL as plain text in the request body (`Content-Type: text/plain`).

**Request body:**
```
https://www.youtube.com/watch?v=VIDEO_ID
```

**Success response (200):**
```json
{
  "status": "success",
  "video_id": "VIDEO_ID",
  "generated_summary": "..."
}
```

**Error response (400 / 500):**
```json
{
  "status": "error",
  "message": "..."
}
```

## Project structure

```
app.py                  Flask entry point and route handlers
log_config.py           Configures root logger (StreamHandler, INFO level)
services/
  youtube_service.py    Extracts video ID and fetches transcript
  summarizer.py         Map-reduce summarization pipeline
templates/
  index.html            Single-page web UI
static/
  js/app.js             Calls POST /fetch, renders result
  css/styles.css        UI styles
Dockerfile
requirements.txt
```

## Known limitations

- **Only `?v=` URLs are supported.** Shortened `youtu.be/` links and `/embed/` or `/v/` formats are validated client-side but the server-side ID extractor (`get_video_id_from_link`) only splits on `?v=`.
- Videos without auto-generated captions will return an empty transcript, producing an empty summary.
- The 1.5 s inter-chunk sleep is a hard-coded rate-limit guard for Groq's free tier; remove or reduce it if you have a paid plan.

## LLM backend

The app uses Groq's OpenAI-compatible endpoint (`https://api.groq.com/openai/v1`) with model `openai/gpt-oss-120b`. The `Summarizer` class accepts constructor overrides for `model`, `LLM_API_KEY`, and `LLM_BASE_URL`, making it straightforward to swap in any OpenAI-compatible provider.

## Dependencies

| Package | Purpose |
|---|---|
| `flask` | Web framework |
| `openai` | OpenAI-compatible SDK (used for Groq) |
| `tiktoken` | Token counting and chunking |
| `youtube-transcript-api` | Fetches YouTube transcripts |
| `python-dotenv` | Loads `.env` at startup |
