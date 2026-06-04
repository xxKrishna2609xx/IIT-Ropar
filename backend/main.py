from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests as http_requests

# ── Load environment variables ───────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Please add it to backend/.env")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
FAQS_PATH   = os.path.join(BASE_DIR, "faqs.json")
FAQS_HI_PATH = os.path.join(BASE_DIR, "faqs_hi.json")
VOTES_PATH  = os.path.join(BASE_DIR, "votes.json")

# ── Build FAQ knowledge base once at startup ─────────────────────────────────
def load_faq_text() -> str:
    """Flatten entire FAQ JSON into clean plain-text for the system prompt."""
    with open(FAQS_PATH, "r", encoding="utf-8") as f:
        sections = json.load(f)

    lines: List[str] = []
    for section in sections:
        lines.append(f"\n## {section['title']}\n")
        for q in section["questions"]:
            clean_answer = re.sub(r"<[^>]+>", " ", q["answer"])
            clean_answer = re.sub(r"\s+", " ", clean_answer).strip()
            lines.append(f"Q: {q['question']}")
            lines.append(f"A: {clean_answer}\n")
    return "\n".join(lines)

FAQ_KNOWLEDGE_BASE = load_faq_text()
print(f"[Yaksha] Loaded {len(FAQ_KNOWLEDGE_BASE)} chars of FAQ knowledge.")

# ── Yaksha system prompt ─────────────────────────────────────────────────────
YAKSHA_SYSTEM_PROMPT = f"""You are Yaksha, the official AI assistant for the Vicharanashala Internship Programme at IIT Ropar.

YOUR ROLE:
- Answer questions ONLY about the Vicharanashala Internship (VINS/VISE), samagama.in, ViBe LMS, NOC process, offer letters, certificates, Rosetta journal, Spurti Points, team formation, and anything in the FAQ below.
- Be concise, accurate, and direct. Do not add unnecessary filler or pleasantries.
- If a question is completely unrelated to the internship programme, politely redirect: say you can only help with Vicharanashala Internship questions, and suggest checking the FAQ page or emailing sudarshansudarshan@gmail.com.
- Ground every answer in the FAQ knowledge base below. Do NOT make up or invent information.
- When stating rules or policies, be precise — these are binding programme rules.
- Write in plain readable text only. Do NOT use markdown formatting like **, ##, __, or bullet dashes — the chat widget shows plain text.
- Keep answers focused: 2 to 5 sentences is ideal unless the question genuinely requires more detail.
- Use a warm but professional tone — like a knowledgeable senior who has read every FAQ.

FAQ KNOWLEDGE BASE:
{FAQ_KNOWLEDGE_BASE}
"""

# ── Gemini API config ───────────────────────────────────────────────────────────────────
# Always call the global endpoint directly so Render's server region
# doesn't trigger "User location not supported" errors.
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
YAKSHA_MODEL    = "gemini-2.5-flash"        # primary
YAKSHA_FALLBACK = "gemini-2.5-flash-lite"   # fallback if primary quota exhausted

# ── Initialize votes file ────────────────────────────────────────────────────
if not os.path.exists(VOTES_PATH):
    with open(VOTES_PATH, "w") as f:
        json.dump({}, f)

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(title="Vicharanashala FAQ API")


# ── CORS origin validator ────────────────────────────────────────────────────
_VERCEL_ORIGIN = re.compile(
    r"^https://[\w\-]+(\.vercel\.app)$"           # any *.vercel.app subdomain
)

def _is_allowed_origin(origin: str) -> bool:
    if origin in (
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:4173",   # vite preview port
    ):
        return True
    return bool(_VERCEL_ORIGIN.match(origin))

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://[\w\-]+(\.vercel\.app)$",
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ──────────────────────────────────────────────────────────
class VoteRequest(BaseModel):
    faq_id: str
    vote_type: Optional[str] = None       # "up", "down", or None (= remove)
    previous_vote: Optional[str] = None

class ChatMessage(BaseModel):
    role: str   # "user" or "model"
    text: str

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[ChatMessage]] = []


# ── Health check endpoint ─────────────────────────────────────────────────────
import time as _time
_SERVER_START = _time.time()

@app.get("/api/health")
def health_check():
    uptime_seconds = int(_time.time() - _SERVER_START)
    return {"status": "ok", "uptime_seconds": uptime_seconds}


# ── FAQ endpoint ─────────────────────────────────────────────────────────────
@app.get("/api/faqs")
def get_faqs(lang: str = "en"):
    path = FAQS_HI_PATH if lang == "hi" and os.path.exists(FAQS_HI_PATH) else FAQS_PATH
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="FAQ data not found")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# ── Votes endpoints ──────────────────────────────────────────────────────────
@app.get("/api/votes")
def get_votes():
    with open(VOTES_PATH, "r", encoding="utf-8") as f:
        votes = json.load(f)
    return votes


@app.post("/api/vote")
def post_vote(req: VoteRequest):
    with open(VOTES_PATH, "r", encoding="utf-8") as f:
        votes = json.load(f)

    if req.faq_id not in votes:
        votes[req.faq_id] = {"up": 0, "down": 0}

    entry = votes[req.faq_id]

    if req.previous_vote in ("up", "down"):
        entry[req.previous_vote] = max(0, entry.get(req.previous_vote, 0) - 1)

    if req.vote_type in ("up", "down"):
        entry[req.vote_type] = entry.get(req.vote_type, 0) + 1

    with open(VOTES_PATH, "w", encoding="utf-8") as f:
        json.dump(votes, f, indent=2)

    return {"status": "success", "votes": entry}


# ── Agentic Chat — Yaksha powered by Gemini ──────────────────────────────────
@app.post("/api/chat")
async def chat(req: ChatRequest):
    # Build Gemini REST API conversation history
    contents = []
    for msg in (req.history or []):
        if msg.role in ("user", "model") and msg.text.strip():
            contents.append({"role": msg.role, "parts": [{"text": msg.text}]})
    # Append current user query
    contents.append({"role": "user", "parts": [{"text": req.query}]})

    payload = {
        "system_instruction": {"parts": [{"text": YAKSHA_SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024,
        },
    }

    # Try primary model, fall back to lite on quota errors
    models_to_try = [YAKSHA_MODEL, YAKSHA_FALLBACK]

    for model in models_to_try:
        try:
            url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={GEMINI_API_KEY}"
            resp = http_requests.post(url, json=payload, timeout=30)

            if resp.status_code == 429:
                print(f"[Yaksha] {model} quota exhausted, trying fallback...")
                continue

            if not resp.ok:
                detail = resp.json().get("error", {}).get("message", resp.text)
                raise HTTPException(status_code=500, detail=f"Yaksha error: {detail}")

            answer = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"answer": answer.strip()}

        except HTTPException:
            raise
        except Exception as e:
            print(f"[Yaksha] {model} unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"Yaksha error: {str(e)}")

    # All models quota-exhausted
    raise HTTPException(
        status_code=429,
        detail="Yaksha is currently unavailable due to API quota limits. Please try again later."
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
