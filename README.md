# Storyteller

Generates narrated story videos (full-length and Shorts) and uploads them to YouTube. For each story, the pipeline writes the script with OpenAI's GPT, generates narration audio via TTS, sources illustration images, and compiles everything into a video with `moviepy` before uploading through the YouTube Data API.

## Project structure

Content lives in per-category folders (currently `cuentos/` and `terror/`), each with its own `creador_historias.py` (story generator) and supporting scripts for descriptions, thumbnails, and images. All categories share the root-level video creation and YouTube upload scripts.

## Setup

1. Clone the repository.
2. Install dependencies with pipenv: `pipenv install`.
3. Create a `.env` file (see below) in the root and in each category folder that needs one.
4. Place your Google OAuth client secret at `client_secret_oauth.json` in the root.

### Environment variables

| Variable | Description |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI API key used for story and description generation |
| `YOUTTUBE_API_KEY` | Google/YouTube Data API key |
| `YOUTUBE_CHANNEL_ID` | Target channel ID, used by the upload-scheduling scripts |
| `YOUTUBE_UPLOADS_PLAYLIST_ID` | Channel's uploads playlist ID, used to enumerate existing videos |

## Usage

Run a category's story creator from inside that category's folder, then run the video creator to compile and upload the result. Some auxiliary scripts (e.g. YouTube Studio automation) rely on Selenium and require a local Chrome/Firefox installation.
