"""Retrieval + grounded answer generation with quote verification."""
import json
import re
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from rapidfuzz import fuzz

import gemini

DATA = Path(__file__).parent / "data"
TOP_K = 8
VERDICTS = {"allowed", "limits", "banned", "unsure"}

SYSTEM = """You are "Can I Bring It?", a customs and airline baggage checker.
You answer ONLY from the numbered official excerpts you are given. Never use outside knowledge.

Rules:
- Pick the single excerpt that best answers the question and copy one or two sentences from it VERBATIM into "quote" (exact characters, no paraphrase, no ellipsis in the middle of a number).
- "source_id" is the number of that excerpt.
- verdict: "allowed" = permitted with no meaningful limit; "limits" = permitted with quantity/value/declaration/approval/cabin-only conditions; "banned" = prohibited; "unsure" = the excerpts do not clearly answer the question for this route.
- Apply the right country: customs allowances belong to the DESTINATION country (where the traveller arrives). Aviation safety rules (batteries, liquids, sharp items) apply on any flight. Cash declaration rules can apply on leaving the origin country too.
- If the excerpts are about a different country than the one asked about, or do not cover the item, answer "unsure". Do not guess.
- "answer": one or two plain sentences, starting with Yes / No / Only if / Not sure. Do arithmetic for the user when helpful (e.g. 20,000 mAh at 3.7 V ≈ 74 Wh; 4 bottles vs a 3-bottle allowance).
- If no excerpt states the specific rule or number the question needs, answer "unsure" rather than a vague yes.
- "limit": the specific number/condition in a short phrase, or "—" if none.
"""

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "verdict": {"type": "STRING", "enum": ["allowed", "limits", "banned", "unsure"]},
        "answer": {"type": "STRING"},
        "limit": {"type": "STRING"},
        "quote": {"type": "STRING"},
        "source_id": {"type": "INTEGER"},
    },
    "required": ["verdict", "answer", "limit", "quote", "source_id"],
}

TOKEN = re.compile(r"[a-z0-9]+")

# User wording often joins product names that official pages keep as separate
# words. Keep retrieval broad without changing the question sent to the model.
QUERY_ALIASES = (
    (re.compile(r"\bpowerbank(s)?\b", re.I), "power bank portable charger"),
    (re.compile(r"\bpower[- ]?banks?\b", re.I), "power bank portable charger"),
    (re.compile(r"\bmah\b", re.I), "mAh milliamp hours"),
)


def tok(s):
    return TOKEN.findall(s.lower())


def retrieval_query(s):
    for pattern, replacement in QUERY_ALIASES:
        s = pattern.sub(replacement, s)
    return s


def norm(s):
    s = s.lower().replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()


class Index:
    def __init__(self):
        self.records = json.loads((DATA / "index.json").read_text())
        self.vecs = np.load(DATA / "vectors.npy")
        self.bm25 = BM25Okapi([tok(r["source_name"] + " " + r["text"]) for r in self.records])

    @property
    def sources(self):
        seen = {}
        for r in self.records:
            seen.setdefault(r["source_url"], {"name": r["source_name"], "url": r["source_url"], "countries": r["countries"], "mode": r["mode"]})
        return list(seen.values())

    def search(self, query, countries, k=TOP_K, dest=None):
        query = retrieval_query(query)
        qv = np.array(gemini.embed([query], task="RETRIEVAL_QUERY")[0], dtype=np.float32)
        qv /= np.linalg.norm(qv) + 1e-9
        dense = self.vecs @ qv
        sparse = np.array(self.bm25.get_scores(tok(query)))
        if sparse.max() > 0:
            sparse = sparse / sparse.max()
        score = 0.7 * dense + 0.3 * sparse
        wanted = set(countries) | {"ANY"}
        mask = np.array([bool(wanted & set(r["countries"])) for r in self.records])
        if dest:  # customs allowances belong to the destination country
            score = score + 0.08 * np.array([dest in r["countries"] for r in self.records])
        score = np.where(mask, score, -1.0)
        order = np.argsort(-score)[:k]
        results = [self.records[i] for i in order if score[i] > 0]
        if results:
            return results
        # A relevant lexical match must not disappear just because the dense
        # embedding score is negative (this can happen for short/compound
        # product names such as "powerbank").
        lexical_order = np.argsort(-sparse)
        return [self.records[i] for i in lexical_order if mask[i] and sparse[i] > 0][:k]


def verify_quote(quote, text):
    q, t = norm(quote), norm(text)
    if len(q) < 15:
        return False
    if q in t:
        return True
    return fuzz.partial_ratio(q, t) >= 92


SENT = re.compile(r"(?<=[.!?])\s+")


def snap_quote(quote, text, threshold=85):
    """Return the real sentence span from text that best matches the model's quote, or None."""
    q = norm(quote)
    if len(q) < 15:
        return None
    sents = [x.strip() for x in SENT.split(text) if x.strip()]
    best, score = None, 0
    for i in range(len(sents)):
        for j in (1, 2):
            cand = " ".join(sents[i:i + j])
            sc = fuzz.ratio(q, norm(cand))
            if sc > score:
                best, score = cand, sc
    return best if score >= threshold else None


def unsure(msg="I couldn't find an official source that answers this for your route, so I won't guess."):
    return {
        "verdict": "unsure",
        "answer": msg,
        "limit": "—",
        "quote": "No official page in our allow-list matched this question.",
        "source_name": "",
        "source_url": "",
        "fetched": "",
    }


def answer(index, origin, dest, airline, question):
    query = f"{question} (travelling from {origin} to {dest}{', airline ' + airline if airline else ''})"
    hits = index.search(query, [origin, dest], dest=dest)
    if not hits:
        return unsure()
    ctx = "\n\n".join(
        f"[{i}] SOURCE: {h['source_name']} | applies to: {', '.join(h['countries'])}\n{h['text']}"
        for i, h in enumerate(hits)
    )
    user = (
        f"Route: from {origin} to {dest}. Airline: {airline or 'not specified'}.\n"
        f"Question: {question}\n\nOfficial excerpts:\n{ctx}"
    )
    out, hit, quote = None, None, ""
    for attempt in range(2):  # one retry if the model's quote can't be verified
        try:
            out = json.loads(gemini.generate_json(SYSTEM, user, SCHEMA, temperature=0.1 if attempt == 0 else 0.0))
        except Exception:
            if attempt == 0:
                continue
            return unsure("The checker couldn't read the official sources right now. Please try again.")
        v = out.get("verdict") if out.get("verdict") in VERDICTS else "unsure"
        sid = out.get("source_id")
        if v == "unsure" or not isinstance(sid, int) or not (0 <= sid < len(hits)):
            return unsure()
        quote = (out.get("quote") or "").strip().strip('"“”')
        hit = hits[sid] if verify_quote(quote, hits[sid]["text"]) else next(
            (h for h in hits if verify_quote(quote, h["text"])), None)
        if hit:
            break
        # Snap a near-verbatim quote to the real sentence in the cited excerpt, so what we show is always source text.
        snapped = snap_quote(quote, hits[sid]["text"])
        if snapped:
            hit, quote = hits[sid], snapped
            break
    if not hit:
        return unsure("I found related official pages but couldn't verify an exact quote, so I won't guess.")
    return {
        "verdict": v,
        "answer": out.get("answer", "").strip(),
        "limit": (out.get("limit") or "—").strip(),
        "quote": quote,
        "source_name": hit["source_name"],
        "source_url": hit["source_url"],
        "fetched": hit["fetched"],
    }
