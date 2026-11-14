# Can I Bring It? 🧳

**Know what you can pack before customs does.**

Ask any item for any border, like "Can I carry a 20,000 mAh power bank?" or "How much cash can I take into the UAE?" You get a traffic-light verdict (🟢 Allowed · 🟡 Limits · 🔴 Banned · ⚪ Not sure) built **only from official government customs and airline pages**, with the exact sentence quoted and linked.

Built for **HackGlobal 2026**, Grounded Knowledge & RAG track, powered by Vultr.

## Why
Customs and baggage rules differ by country and change often. Blogs and forums are outdated or wrong, and a wrong guess costs you a confiscated bag, a fine, or a missed flight.

## How it works
1. **Ask in plain words.** Pick the route (from → to, optional airline) and type the item.
2. **Read only official pages.** Live search is limited to an allow-list of government and airline domains.
3. **Verdict with proof.** The LLM answers only from the fetched text and must quote it. If no official source matches, it says **Not sure** instead of guessing.

## Architecture
```
Browser (frontend/index.html)
   │  POST /api/check {from, to, airline, question}
   ▼
FastAPI backend on Vultr Compute
   │  1. Exa search restricted to official domains
   │  2. Gemini answers ONLY from fetched text, quote required
   ▼
Verdict JSON {verdict, answer, limit, quote, source_name, source_url, fetched}
```

**Official-source allow-list:** iata.org, faa.gov, u.ae, dubaicustoms.gov.ae, customs.go.jp, cbic.gov.in, gov.uk, cbp.gov, cbsa-asfc.gc.ca, abf.gov.au, ica.gov.sg, zoll.de

## Run the frontend
It's a static site with no build step.
```bash
cd frontend
python3 -m http.server 8080
# open http://localhost:8080
```
With `API_BASE` empty (top of the script in `index.html`) it runs in **demo mode** with four real, sourced answers: power bank, cash into UAE, whisky into Japan, alcohol into Dubai. Set `API_BASE` to your Vultr backend URL (e.g. `http://YOUR_VULTR_IP:8000`) for live answers.

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
HTML/CSS/JS frontend · FastAPI (Python) · Exa search · Google Gemini · Vultr Compute

## Credits
Illustrations are AI-generated watercolor artwork made for this project. Demo answers are quoted from the FAA, the UAE Government Portal (u.ae), Japan Customs and Dubai Customs.

> Not legal advice. Rules change, so always confirm with official customs or your airline.
