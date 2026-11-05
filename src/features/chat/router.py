from fastapi import APIRouter, Header, HTTPException, Request

from src.features.chat.services import HANDLERS, WEBHOOK_SECRET, send_message

app = APIRouter()


@app.post("/telegram_message")
async def telegram_webhook(
    request: Request,
    # Telegram sends this header if you set secret_token when registering the webhook
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    update = await request.json()
    client = request.app.state.client

    message = update.get("message")

    if not message:
        return {"status": "ignored"}

    chat_id = message["chat"]["id"]
    # user = message["from"]

    reply = None
    for key, handler in HANDLERS:
        if key in message:
            reply = await handler(client, message)
            break

    if reply is None:
        reply = f"🤷 Unsupported type. Keys: {list(message.keys())}"

    await send_message(client, chat_id, reply)
