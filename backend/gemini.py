"""Thin Gemini REST client (no SDK needed)."""
import os
import time

import httpx

BASE = "https://generativelanguage.googleapis.com/v1beta"
GEN_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
EMBED_DIM = int(os.getenv("GEMINI_EMBED_DIM", "768"))


def _headers():
    h = {"Content-Type": "application/json"}
    key = os.getenv("GEMINI_API_KEY")
    if key:
        h["x-goog-api-key"] = key
    return h


def _post(path, body, timeout=60, retries=4):
    last = None
    for i in range(retries):
        try:
            r = httpx.post(f"{BASE}/{path}", json=body, headers=_headers(), timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504):
                last = RuntimeError(f"Gemini {r.status_code}: {r.text[:300]}")
                time.sleep(30 if r.status_code == 429 else 2 ** i)
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
    data = _post(f"models/{GEN_MODEL}:generateContent", body, timeout=30, retries=2)
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)
