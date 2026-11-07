# shape of the request
# {
#     "object": "whatsapp_business_account",
#     "entry": [
#         {
#             "id": "1033838589633318",
#             "changes": [
#                 {
#                     "value": {
#                         "messaging_product": "whatsapp",
#                         "metadata": {
#                             "display_phone_number": "923209667499",
#                             "phone_number_id": "1404190916100720"
#                         },
#                         "contacts": [
#                             {
#                                 "profile": {
#                                     "name": "aaa"
#                                 },
#                                 "wa_id": "923001015768",
#                                 "user_id": "PK.1682873062791440"
#                             }
#                         ],
#                         "messages": [
#                             {
#                                 "from": "923001015768",
#                                 "from_user_id": "PK.1682873062791440",
#                                 "id": "wamid.HBgMOTIzMDAxMDE1NzY4FQIAEhggQTVGQTA2MTlCODk5QTI0N0IzQUE2QjcyMDQ5QjBFMjYA",
#                                 "timestamp": "1793980543",
#                                 "text": {
#                                     "body": "G"
#                                 },
#                                 "type": "text"
#                             }
#                         ]
#                     },
#                     "field": "messages"
#                 }
#             ]
#         }
#     ]
# }


# router.py

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.core.config import get_settings
from src.features.chat.graph.state import SimpleChatState
from src.features.chat.graph.workflow import get_graph
from src.features.chat.whatsapp import send_whatsapp_message

settings = get_settings()
app = APIRouter()

# Meta retries a webhook if it doesn't get a fast 200, which would answer the same
# message twice. We remember message ids we've already handled.
# (In-memory only: it resets on restart. Fine for learning.)
_seen_message_ids: set[str] = set()


@app.get("/webhook")
async def verify_webhook(
    # Meta sends these query params with dots in their names, so we need aliases
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
    """One-time handshake when you click 'Verify and save' in the Meta dashboard."""
    if mode == "subscribe" and token == settings.WHATSAPP_WEBHOOK_SECRET:
        # Meta expects the challenge echoed back as a plain number/string
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


async def process_message(phone_id: str, sender: str, text: str) -> None:
    graph = await get_graph()
    config: RunnableConfig = {"configurable": {"thread_id": sender}}
    result = await graph.ainvoke(
        SimpleChatState(
            messages=[HumanMessage(content=text)],
        ),
        config=config,
    )

    for message in result.get("messages", []):
        message.pretty_print()

    last = result["messages"][-1]
    reply = str(last.content).strip() or "Sorry, I couldn't generate a reply."

    await send_whatsapp_message(phone_id, sender, reply)


@app.post("/webhook")
async def whats_app(request: Request, background_tasks: BackgroundTasks):

    # delivery results arrive here (no "messages" key)
    value = await request.json()
    if value.get("statuses"):
        print(f"[STATUS] {value['statuses']}")
    data = await request.json()

    # Defensive parsing: Meta also sends delivery/read receipts (no "messages" key)
    try:
        value = data["entry"][0]["changes"][0]["value"]
    except (KeyError, IndexError):
        return {"status": "ignored"}

    messages = value.get("messages")
    if not messages:
        return {"status": "ignored"}  # a status update, nothing to answer

    msg = messages[0]
    sender = msg["from"]

    # dev-only allowlist: only answer your own number
    if sender != "923001015768":
        print(f"[WEBHOOK] ignoring message from {sender}")
        return {"status": "ignored"}

    # only text for now (images, audio, etc. come later)
    if msg.get("type") != "text":
        return {"status": "ignored"}

    # skip duplicates caused by Meta retries
    if msg["id"] in _seen_message_ids:
        return {"status": "duplicate"}
    _seen_message_ids.add(msg["id"])

    phone_id = value["metadata"]["phone_number_id"]  # the number the user wrote TO
    text = msg["text"]["body"]

    background_tasks.add_task(process_message, phone_id, sender, text)
    return {"status": "ok"}
