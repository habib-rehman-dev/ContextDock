from pathlib import Path

import httpx
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.core.config import get_settings
from src.features.chat.graph.state import SimpleChatState
from src.features.chat.graph.workflow import get_graph

settings = get_settings()

whatsapp_token = settings.WHATSAPP_TOKEN
whatsapp_phone_id = settings.WHATSAPP_PHONE_ID
whatsapp_webhook_secret = settings.WHATSAPP_WEBHOOK_SECRET

# Fail fast with a clear message if the token is missing
if not whatsapp_token:
    raise ValueError("WHATSAPP_TOKEN is not set in the environment")

# Downloaded files are saved here
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


# async def send_message(client: httpx.AsyncClient, chat_id: int, text: str):
#     """Send a text reply to a chat."""
#     try:
#         resp = await client.post(
#             f"{whatsapp_api}/sendMessage",
#             json={"chat_id": chat_id, "text": text},
#         )
#         resp.raise_for_status()
#     except httpx.HTTPError as err:
#         print(f"[ERROR] sendMessage failed: {err}")


# async def download_file(client: httpx.AsyncClient, file_id: str) -> Path | None:
#     """Two-step download: getFile -> file_path -> bytes saved to disk."""
#     try:
#         # Step 1: ask Telegram where the file lives
#         r = await client.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id})
#         r.raise_for_status()
#         file_path = r.json()["result"]["file_path"]  # e.g. "photos/file_12.jpg"

#         # Step 2: download the bytes from that path
#         content = await client.get(f"{FILE_API}/{file_path}")
#         content.raise_for_status()

#         # Save with a unique-ish name so files don't overwrite each other
#         save_path = DOWNLOAD_DIR / f"{file_id[:10]}_{Path(file_path).name}"
#         save_path.write_bytes(content.content)
#         print(f"[INFO] downloaded {file_path} -> {save_path}")
#         return save_path
#     except httpx.HTTPError as err:
#         # Usually: file bigger than 20 MB, or network/VPN issue
#         print(f"[ERROR] download failed: {err}")
#         return None


async def handle_text(client, msg) -> str:
    text = msg["text"]

    # Commands look like "/start" or "/start@MyBot hello"
    if text.startswith("/"):
        parts = text.split()
        command = parts[0].split("@")[0]  # strip "@BotName" if present
        args = parts[1:]  # everything after the command
        if command == "/start":
            return "👋 Hello! Send me text, photo, voice, file, location..."
        return f"Command: {command}, args: {args}"

    # Use the Telegram chat id as the thread id, so each chat gets its own
    # memory. (You had "1", which makes every user share one conversation.)
    chat_id = msg["chat"]["id"]
    config: RunnableConfig = {"configurable": {"thread_id": str(chat_id)}}

    # FIX: get_graph() is async, so it must be awaited.
    # Without await you get a coroutine object, not the graph.
    compiled_graph = await get_graph()

    res = await compiled_graph.ainvoke(
        SimpleChatState(
            messages=[HumanMessage(content=text)],
            
        ),
        config=config,
    )

    # The last message in the state is the model's reply
    ready = res["messages"][-1].content

    return ready


# async def handle_photo(client, msg) -> str:
#     # `photo` is a LIST of the same image in different sizes.
#     # The last item is the biggest one.
#     best = msg["photo"][-1]
#     caption = msg.get("caption", "(no caption)")
#     path = await download_file(client, best["file_id"])
#     return (
#         f"🖼 Photo {best['width']}x{best['height']}\nCaption: {caption}\nSaved: {path}"
#     )


# async def handle_document(client, msg) -> str:
#     doc = msg["document"]
#     path = await download_file(client, doc["file_id"])
#     return (
#         f"📄 File: {doc.get('file_name')}\n"
#         f"Type: {doc.get('mime_type')}\n"
#         f"Size: {doc.get('file_size')} bytes\n"
#         f"Saved: {path}"
#     )


# async def handle_voice(client, msg) -> str:
#     voice = msg["voice"]
#     path = await download_file(client, voice["file_id"])  # .oga (OGG/Opus)
#     return f"🎤 Voice note, {voice['duration']}s\nSaved: {path}"


# async def handle_video(client, msg) -> str:
#     print(f"[INFO] Handling video message: {msg}")
#     video = msg["video"]
#     path = await download_file(client, video["file_id"])  # .mp4

#     return (
#         f"🎬 Video {video['width']}x{video['height']}, "
#         f"{video['duration']}s, {video.get('file_size')} bytes \nSaved: {path}"
#     )


# async def handle_audio(client, msg) -> str:
#     audio = msg["audio"]
#     path = await download_file(client, audio["file_id"])  # .mp3, .m4a, etc.
#     return (
#         f"🎵 Audio: {audio.get('title')} by {audio.get('performer')}\n"
#         f"Duration: {audio['duration']}s \nSaved: {path}"
#     )


# async def handle_location(client, msg) -> str:
#     loc = msg["location"]
#     return f"📍 Location: lat {loc['latitude']}, lon {loc['longitude']}"


# async def handle_contact(client, msg) -> str:
#     c = msg["contact"]
#     return f"👤 Contact: {c['first_name']}, phone {c['phone_number']}"


# async def handle_sticker(client, msg) -> str:
#     s = msg["sticker"]
#     return f"😀 Sticker emoji: {s.get('emoji')}, set: {s.get('set_name')}"


# async def handle_poll(client, msg) -> str:
#     p = msg["poll"]
#     options = [o["text"] for o in p["options"]]
#     return f"📊 Poll: {p['question']}\nOptions: {options}"


# async def handle_dice(client, msg) -> str:
#     d = msg["dice"]
#     return f"🎲 Dice {d['emoji']} rolled: {d['value']}"


# HANDLERS = [
#     ("text", handle_text),
#     ("photo", handle_photo),
#     ("document", handle_document),
#     ("voice", handle_voice),
#     ("audio", handle_audio),
#     ("video", handle_video),
#     ("location", handle_location),
#     ("contact", handle_contact),
#     ("sticker", handle_sticker),
#     ("poll", handle_poll),
#     ("dice", handle_dice),
# ]
