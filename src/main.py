from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# from src.features.chat.graph.workflow import init_graph
from src.features.chat.router import app as chat_router

# Load variables from .env into the environment
load_dotenv()


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Opens an aiosqlite connection and closes it automatically on shutdown
#     async with AsyncSqliteSaver.from_conn_string(
#         "chat_graph_checkpoint.db"
#     ) as checkpointer:
#         await checkpointer.setup()  # creates the checkpoint tables if missing
#         init_graph(checkpointer)  # build the graph with the live checkpointer
#         yield  # the app runs while we're paused here
#     # leaving the `async with` closes the DB connection


app = FastAPI()  # <-- add lifespan here
app.include_router(chat_router, tags=["chat"])




