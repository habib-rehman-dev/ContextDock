import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request, Response

# Load the variables from your .env file
load_dotenv()

app = FastAPI()

# Grab the secret you invented in the .env file
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: int = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Meta sends a GET request here exactly once when you configure the webhook in their portal.
    If the secret matches, we echo back their challenge number to prove we are real.
    """
    if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_SECRET:
        print("\n✅ Webhook verified successfully by Meta!")
        return Response(content=str(hub_challenge))

    print("\n❌ Webhook verification failed - secrets do not match.")
    return Response(status_code=403)


from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/webhook")
async def receive_message(request: Request):
    update = await request.json()

    try:
        entry = update.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        # 1. Ignore status updates (delivered, read, sent receipts)
        if "statuses" in value:
            status_info = value["statuses"][0]
            print(
                f"ℹ️ Status Update: Message {status_info['id']} status is '{status_info['status']}'"
            )
            return {"status": "ok"}

        # 2. Catch actual user messages
        if "messages" in value:
            message = value["messages"][0]
            sender_phone = message.get("from")  # Sender's phone number
            msg_type = message.get("type")

            if msg_type == "text":
                user_text = message.get("text", {}).get("body")

                print("\n=======================================")
                print(f"📩 REAL MESSAGE RECEIVED!")
                print(f"From: +{sender_phone}")
                print(f"Text: {user_text}")
                print("=======================================\n")

    except (IndexError, KeyError, AttributeError) as err:
        print(f"[ERROR] Parsing error: {err}")

    return {"status": "ok"}
