"""Build the RAG index from the official-source allow-list.

    python ingest.py            # fetch, chunk, embed -> data/index.json + data/vectors.npy

Run it once at deploy time (and again whenever you want fresher rules).
"""
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import httpx
import numpy as np
from bs4 import BeautifulSoup
from pypdf import PdfReader

import gemini
from seed_snapshots import SNAPSHOTS
from sources import SOURCES

DATA = Path(__file__).parent / "data"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36 CanIBringIt/1.0"
CHUNK_CHARS = 1100
OVERLAP = 200


def clean(text):
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def html_to_text(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form", "svg", "iframe", "aside"]):
        tag.decompose()
    main = soup.find("main") or soup.find(attrs={"role": "main"}) or soup.find("article") or soup.body or soup
    lines = []
    for el in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th", "dt", "dd"]):
        t = el.get_text(" ", strip=True)
        if len(t) > 2:
            lines.append(t)
    # de-duplicate consecutive repeats (nested li/p)
    out, prev = [], None
    for l in lines:
        if l != prev:
            out.append(l)
        prev = l
    return clean("\n".join(out))


def pdf_to_text(data):
    reader = PdfReader(io.BytesIO(data))
    return clean("\n".join((p.extract_text() or "") for p in reader.pages))


def fetch(url):
    r = httpx.get(url, headers={"User-Agent": UA, "Accept-Language": "en"}, follow_redirects=True, timeout=40)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    if url.lower().endswith(".pdf") or "pdf" in ctype:
        return pdf_to_text(r.content)
    return html_to_text(r.text)


def chunk(text):
    paras = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 <= CHUNK_CHARS:
            cur = f"{cur}\n{p}" if cur else p
            continue
        if cur:
            chunks.append(cur)
            cur = cur[-OVERLAP:] + "\n" + p if len(p) < CHUNK_CHARS else ""
        while len(p) > CHUNK_CHARS:
            chunks.append(p[:CHUNK_CHARS])
            p = p[CHUNK_CHARS - OVERLAP:]
        if not cur:
            cur = p
    if cur:
        chunks.append(cur)
    return [c for c in chunks if len(c) > 60]


def main():
    DATA.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%d %b %Y")
    records = []
    for src in SOURCES:
        url, mode = src["url"], "live"
        try:
            text = fetch(url)
            if len(text) < 200:
                raise ValueError("page text too short")
        except Exception as e:
            if url in SNAPSHOTS:
                text, mode = SNAPSHOTS[url], "snapshot"
            else:
                print(f"  SKIP  {src['name']}: {e}")
                continue
        pieces = chunk(text)
        for i, c in enumerate(pieces):
            records.append({
                "id": f"{len(records)}",
                "source_name": src["name"],
                "source_url": url,
                "countries": src["countries"],
                "fetched": today if mode == "live" else "14 Nov 2026",
                "mode": mode,
                "text": c,
            })
        print(f"  {mode.upper():8} {len(pieces):3} chunks  {src['name']}")

    print(f"Embedding {len(records)} chunks with {gemini.EMBED_MODEL} ...")
    vecs = np.array(gemini.embed([f"{r['source_name']}\n{r['text']}" for r in records]), dtype=np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
    np.save(DATA / "vectors.npy", vecs)
    (DATA / "index.json").write_text(json.dumps(records, ensure_ascii=False, indent=1))
    print(f"Saved {len(records)} chunks to {DATA}")


if __name__ == "__main__":
    main()
