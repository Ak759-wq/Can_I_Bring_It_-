"""Can I Bring It? — FastAPI backend.

    uvicorn app:app --host 0.0.0.0 --port 8000

Serves the API under /api and the frontend at /.
"""
import os
import time
from collections import OrderedDict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

import rag  # noqa: E402
from sources import ALLOWED_DOMAINS  # noqa: E402

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Can I Bring It?", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "*").split(","), allow_methods=["GET", "POST"], allow_headers=["*"])

index = None
cache = OrderedDict()
CACHE_MAX = 500
hits_by_ip = {}
RATE_PER_MIN = int(os.getenv("RATE_PER_MIN", "20"))


@app.on_event("startup")
def load():
    global index
    index = rag.Index()


class CheckIn(BaseModel):
    from_: str = Field("India", alias="from", max_length=60)
    to: str = Field("UAE", max_length=60)
    airline: str = Field("", max_length=60)
    question: str = Field(..., min_length=3, max_length=300)


@app.get("/api/health")
def health():
    return {"ok": index is not None, "chunks": len(index.records) if index else 0}


@app.get("/api/sources")
def sources():
    return {"allowed_domains": ALLOWED_DOMAINS, "sources": index.sources}


@app.post("/api/check")
def check(body: CheckIn, request: Request):
    ip = request.client.host if request.client else "?"
    now = time.time()
    recent = [t for t in hits_by_ip.get(ip, []) if now - t < 60]
    if len(recent) >= RATE_PER_MIN:
        raise HTTPException(429, "Too many questions. Wait a minute.")
    hits_by_ip[ip] = recent + [now]

    key = (body.from_.lower(), body.to.lower(), body.airline.lower(), " ".join(body.question.lower().split()))
    if key in cache:
        cache.move_to_end(key)
        return cache[key]
    result = rag.answer(index, body.from_, body.to, body.airline, body.question.strip())
    cache[key] = result
    if len(cache) > CACHE_MAX:
        cache.popitem(last=False)
    return result


if FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

    @app.get("/")
    def home():
        return FileResponse(FRONTEND / "index.html")

    @app.get("/{name}")
    def asset(name: str):
        f = (FRONTEND / name).resolve()
        if f.parent != FRONTEND or not f.is_file():
            raise HTTPException(404)
        return FileResponse(f)
