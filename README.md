# ContextDock

ContextDock is a Telegram bot backend built with FastAPI. It receives Telegram messages through a webhook, responds to text with a Groq-powered language model, and can download and summarize metadata for common Telegram message types.

## Features

- **Telegram webhook:** Accepts Telegram updates at `POST /telegram_message` and can validate Telegram's webhook secret-token header.
- **AI text replies:** Routes text messages through a LangGraph workflow and generates responses with Groq's `qwen/qwen3.8-27b` model.
- **Message handling:** Handles photos, documents, voice notes, audio, video, locations, contacts, stickers, polls, and dice. Media files are downloaded into `downloads/`; other message types are summarized in the reply.
- **Async HTTP lifecycle:** Reuses an `httpx.AsyncClient` for Telegram API calls and closes it when the application shuts down.

## Architecture and technology

```text
Telegram
   │ webhook update
   ▼
FastAPI router (/telegram_message)
   │ selects a handler by message type
   ├── Text ──► LangGraph workflow ──► Groq chat model
   ├── Media ──► Telegram Bot API (download) ──► reply
   └── Other supported types ──► Metadata handler ──► reply
```

The application is written in Python 3.13 or newer. FastAPI provides the async HTTP API; `httpx` handles Telegram requests; LangChain and LangGraph connect the text handler to Groq. Dependencies are managed with [uv](https://docs.astral.sh/uv/).

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Groq API key
- A publicly reachable HTTPS URL to receive Telegram webhooks

## Setup

1. Clone the repository and enter its directory.
2. Create a local environment file:

   ```bash
   cp .env.example .env
   ```

3. Replace the placeholder values in `.env`:

   ```dotenv
   BOT_TOKEN=your_telegram_bot_token
   GROQ_API_KEY=your_groq_api_key
   WEBHOOK_SECRET=your_webhook_secret
   ```

   `WEBHOOK_SECRET` is optional. When set, requests must include Telegram's `X-Telegram-Bot-Api-Secret-Token` header with the same value. Keep `.env` private; it is excluded from Git.

4. Install project dependencies:

   ```bash
   uv sync
   ```

## Run locally

Start the development server from the repository root:

```bash
uv run uvicorn main:app --app-dir src --reload
```

The API is available at `http://127.0.0.1:8000`; FastAPI's interactive documentation is at `http://127.0.0.1:8000/docs`. To receive real Telegram updates, expose the server through an HTTPS endpoint and register that URL with Telegram, ending in `/telegram_message`.

## Webhook endpoint

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/telegram_message` | Receives a Telegram update, selects a message handler, and sends a reply. |

Updates without a `message` field are ignored. Unsupported message types receive a fallback response.

## Current implementation notes

- The text intent check recognizes the words `help` and `support`, but both intents currently use the same response-generation node.
- Media files are saved under `downloads/`; the bot reports their metadata but does not transcribe audio or analyze image/video contents.
- The graph uses an in-memory checkpointer, and text requests currently use the same thread ID. Conversation state is not persisted across restarts or isolated by Telegram chat.

## Project layout

```text
src/
├── core/
│   ├── config.py                 # Environment-backed settings
│   └── main.py                   # FastAPI application
└── features/
    └── chat/
        ├── router.py             # Telegram webhook route
        ├── services.py           # Telegram API and message handlers
        └── graph/
            ├── workflow.py       # LangGraph workflow
            ├── nodes.py          # Intent and response nodes
            ├── edges.py          # Intent routing
            ├── llms.py           # Groq model configuration
            └── state.py          # Workflow state
```
