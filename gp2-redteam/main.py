import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from tracker.database import init_db
from api.router import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")

app = FastAPI(
    title="GP-2: LLM Red-Teaming & Safety Eval Framework",
    description="Adversarial prompt library, automated scoring pipeline, and regression tracking across model versions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve the built React dashboard from /dashboard
_dashboard_dist = Path(__file__).parent / "dashboard" / "dist"
if _dashboard_dist.exists():
    app.mount("/dashboard", StaticFiles(directory=str(_dashboard_dist), html=True), name="dashboard")


@app.on_event("startup")
def startup():
    init_db()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("GP2_PORT", "8002"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
