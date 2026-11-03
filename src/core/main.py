from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI

from features.chat.router import app as chat_router

# Load variables from .env into the environment
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup: create ONE reusable HTTP client
    # local_address="0.0.0.0" forces IPv4 (avoids broken IPv6 routes)
    transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0", retries=2)
    app.state.client = httpx.AsyncClient(
        transport=transport,
        timeout=httpx.Timeout(15.0, connect=10.0),
    )
    yield
    # Runs on shutdown: close connections cleanly
    await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(chat_router, tags=["chat"])
