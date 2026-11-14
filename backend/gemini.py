"""Thin Gemini REST client (no SDK needed)."""
import os
import time

import httpx

BASE = "https://generativelanguage.googleapis.com/v1beta"
GEN_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEN_MODELS = [m.strip() for m in os.getenv("GEMINI_FALLBACK_MODELS", GEN_MODEL + ",gemini-3.1-flash-lite,gemini-flash-lite-latest,gemini-2.5-flash").split(",") if m.strip()]
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
EMBED_DIM = int(os.getenv("GEMINI_EMBED_DIM", "768"))


def _headers():
    h = {"Content-Type": "application/json"}
    key = os.getenv("GEMINI_API_KEY")
    if key:
        h["x-goog-api-key"] = key
    return h


class RateLimited(RuntimeError):
    pass


def _post(path, body, timeout=60, retries=4, wait_429=30):
    last = None
    for i in range(retries):
        try:
            r = httpx.post(f"{BASE}/{path}", json=body, headers=_headers(), timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504):
                last = (RateLimited if r.status_code == 429 else RuntimeError)(f"Gemini {r.status_code}: {r.text[:300]}")
                if r.status_code == 429 and wait_429 == 0:
                    raise last
                time.sleep(wait_429 if r.status_code == 429 else min(2 ** i, 2))
                continue
            r.raise_for_status()
            return r.json()
        except httpx.HTTPError as e:
            last = e
            time.sleep(2 ** i)
    raise last


def embed(texts, task="RETRIEVAL_DOCUMENT"):
    """Embed a list of strings. Returns list of float lists."""
    # Free tier allows 100 embed requests/minute (each text counts), so batch 90 and pace.
    out = []
    step = int(os.getenv("EMBED_BATCH", "90"))
    for i in range(0, len(texts), step):
        if i:
            time.sleep(float(os.getenv("EMBED_PAUSE", "61")))
        batch = texts[i:i + step]
        body = {"requests": [{
            "model": f"models/{EMBED_MODEL}",
            "content": {"parts": [{"text": t[:8000]}]},
            "taskType": task,
            "outputDimensionality": EMBED_DIM,
        } for t in batch]}
        data = _post(f"models/{EMBED_MODEL}:batchEmbedContents", body)
        out.extend(e["values"] for e in data["embeddings"])
    return out


def generate_json(system, user, schema, temperature=0.1):
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
            "responseSchema": schema,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    # Each model has its own free-tier quota: on a 429 move straight to the next one.
    last = None
    for model in GEN_MODELS:
        b = dict(body)
        if not model.startswith("gemini-2.5"):
            b["generationConfig"] = {k: v for k, v in body["generationConfig"].items() if k != "thinkingConfig"}
        try:
            data = _post(f"models/{model}:generateContent", b, timeout=25, retries=2, wait_429=0)
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts)
        except Exception as e:  # rate limit, timeout or bad response: try the next model
            last = e
    raise last
