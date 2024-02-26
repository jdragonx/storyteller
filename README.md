# OpenAI Storyteller

This project uses OpenAI's GPT-3.5 and DALL-E APIs, along with a Text-to-Speech (TTS) service, to create a narrated story with images, compile it into a video, and upload it to YouTube.

## Project Structure

Each folder has their own story creator, and they all share the main video creator

## Setup

1. Clone the repository.
2. Install the dependencies with pipenv: `pipenv install`.
3. Copy the `.env.example` file to `.env` and fill in your API keys and other settings.
4. Run the main script: `pipenv run python main.py`.

## Usage

To use the project, you need to call the story creator, be sure to call it while inside the corresponding folder. After that call the video creator, this will compile everything into a video, and upload the video to YouTube.
