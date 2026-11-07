# whatsapp.py
import httpx

from src.core.config import get_settings

settings = get_settings()
phone_id = settings.WHATSAPP_PHONE_ID

# check the current Graph API version in your Meta dashboard, v21.0 is fine
# GRAPH_URL  = f"https://graph.facebook.com/v21.0/{phone_id}/messages"


async def send_whatsapp_message(phone_id: str, to: str, text: str) -> None:
    url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
    """Send a plain text message to a WhatsApp user."""
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    # print(f"[DEBUG] sending WhatsApp message to {to}: {text[:50]}...")
    payload = {
        "messaging_product": "whatsapp",
        "to": to,  # the sender's number, exactly as received in "from"
        "type": "text",
        "text": {"body": text[:4096]},  # WhatsApp's text limit is 4096 chars
    }


    async with httpx.AsyncClient(timeout=20) as client:
        try:
           resp = await client.post(url, json=payload, headers=headers)
           resp.raise_for_status()
           # On success Meta returns a message id (wamid...). This proves it accepted the message.
        #    print(f"[INFO] Meta accepted: {resp.status_code} {resp.text}")
        except httpx.HTTPStatusError as err:
            # Meta explains the problem in the response body (expired token, etc.)
            print(f"[ERROR] send failed: {err.response.status_code} {err.response.text}")
        except httpx.HTTPError as err:
            print(f"[ERROR] network problem: {err}")