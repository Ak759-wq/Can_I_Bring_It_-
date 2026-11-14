# Can I Bring It? 🧳

**Know what you can pack before customs does.**

Ask any item for any border, like "Can I carry a 20,000 mAh power bank?" or "How much cash can I take into the UAE?" You get a traffic-light verdict (🟢 Allowed · 🟡 Limits · 🔴 Banned · ⚪ Not sure) built **only from official government customs and airline pages**, with the exact sentence quoted and linked.

Built for **HackGlobal 2026**, Grounded Knowledge & RAG track, powered by Vultr.

## Why
Customs and baggage rules differ by country and change often. Blogs and forums are outdated or wrong, and a wrong guess costs you a confiscated bag, a fine, or a missed flight.

## How it works
1. **Ask in plain words.** Pick the route (from → to, optional airline) and type the item.
2. **Retrieve from official pages only.** At ingest time the backend fetches an allow-list of government customs and aviation-safety pages (HTML and PDF), chunks them and embeds them with Gemini. At question time it runs hybrid retrieval (Gemini embeddings + BM25), filtered to the origin, destination and global aviation rules, boosted toward the destination country's customs rules.
3. **Grounded verdict with proof.** Gemini 3.5 Flash-Lite answers **only** from the retrieved excerpts, in a strict JSON schema, and must copy a verbatim quote and the excerpt number.
4. **Quote verification.** The backend checks the quote really appears in that official excerpt (exact or ≥92% fuzzy match). If it doesn't, or the sources don't cover the route, the answer is **⚪ Not sure** instead of a guess.

## Architecture
```
Browser (frontend/index.html)
   │  POST /api/check {from, to, airline, question}
   ▼
FastAPI on Vultr Compute (Docker)
   ├─ ingest.py   fetch allow-listed pages → clean → chunk → Gemini embeddings → data/
   ├─ rag.py      hybrid search (dense + BM25), country filter, destination boost
   │              Gemini 3.5 Flash-Lite, JSON schema, verbatim quote required
   │              quote verified against the source text, else "Not sure"
   └─ app.py      /api/check · /api/sources · /api/health · serves the frontend · cache · rate limit
   ▼
{verdict, answer, limit, quote, source_name, source_url, fetched}
```

**Official-source allow-list** (`backend/sources.py`): faa.gov, iata.org, tsa.gov, gov.uk, dubaicustoms.gov.ae, u.ae, customs.go.jp, cbic.gov.in, cbp.gov, customs.gov.sg, abf.gov.au, zoll.de, cbsa-asfc.gc.ca. Countries covered: India, UAE, Japan, UK, USA, Singapore, Australia, Germany, Canada, plus aviation rules on every route. Pages that block automated fetches use a dated verbatim snapshot from the same official URL (`backend/seed_snapshots.py`).

## Run locally
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your GEMINI_API_KEY
python ingest.py              # optional: rebuild the index (a prebuilt one ships in data/)
uvicorn app:app --port 8000   # open http://localhost:8000
```
The frontend is served by the backend, so live answers work out of the box. Opened as a plain file, or if the backend is down, it falls back to four sourced demo answers.

## Deploy on Vultr Compute
1. Create a Vultr Cloud Compute instance (Ubuntu 24.04, 1 vCPU / 1–2 GB is enough).
2. SSH in as root and run:
```bash
curl -fsSL https://raw.githubusercontent.com/Ak759-wq/Can_I_Bring_It_-/main/deploy/vultr-setup.sh | bash -s -- YOUR_GEMINI_API_KEY
```
3. Open `http://YOUR_VULTR_IP/`. That's the public demo URL.

Or manually: `cp backend/.env.example backend/.env`, add the key, then `docker compose up -d --build` (serves on port 80).

## API
`GET /api/health` · `GET /api/sources` (allow-list and indexed pages)

## API contract
`POST /api/check`
```json
{ "from": "India", "to": "UAE", "airline": "", "question": "How much cash can I take?" }
```
Response:
```json
{
  "verdict": "allowed | limits | banned | unsure",
  "answer": "Yes, you can carry cash. Declare it if you have more than AED 60,000.",
  "limit": "Declare above AED 60,000",
  "quote": "Passengers ... exceeding AED 60,000 ... are required to declare it",
  "source_name": "u.ae",
  "source_url": "https://u.ae/...",
  "fetched": "14 Nov 2026"
}
```

## Tech stack
HTML/CSS/JS frontend · FastAPI (Python) · Gemini 3.5 Flash-Lite + gemini-embedding-001 · BM25 (rank-bm25) · RapidFuzz quote verification · Docker · Vultr Compute

## Credits
Illustrations are AI-generated watercolor artwork made for this project. Demo answers are quoted from the FAA, the UAE Government Portal (u.ae), Japan Customs and Dubai Customs.

> Not legal advice. Rules change, so always confirm with official customs or your airline.
