import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from shared.claude_client import ClaudeClient
from classifier.moderator import Moderator
from appeals.database import init_db
from appeals.router import router as appeals_router
from api.router import router as moderation_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")

app = FastAPI(
    title="GP-1: Claude-Powered Content Moderation Pipeline",
    description="Harm classification, severity scoring, and appeals review queue built on the Claude API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(moderation_router)
app.include_router(appeals_router)


@app.on_event("startup")
def startup():
    init_db()
    app.state.moderator = Moderator(ClaudeClient())


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("GP1_PORT", "8001"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
