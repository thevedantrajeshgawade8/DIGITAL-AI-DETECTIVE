"""Digital Detective API.  Run:  uvicorn main:app --reload   (from the backend/ folder)"""
import logging, os, time
from collections import defaultdict, deque
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import ai, rules, search

log = logging.getLogger("detective")
MAX_BYTES = 8 * 1024 * 1024
STATUSES = {"verified", "contradicted", "unverified", "suspicious"}
BASE_LIMITS = ["The score is a risk indicator, not a probability of fraud.",
               "No warning signs does not prove a message is legitimate."]

app = FastAPI(title="Digital Detective", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
                   allow_methods=["GET", "POST"], allow_headers=["*"])

_hits: dict[str, deque] = defaultdict(deque)
def rate_limit(request: Request, per_min: int = int(os.getenv("RATE_LIMIT_PER_MIN", "10"))):
    ip = (request.headers.get("x-forwarded-for") or request.client.host or "?").split(",")[0].strip()
    q, now = _hits[ip], time.time()
    while q and now - q[0] > 60: q.popleft()
    if len(q) >= per_min: raise HTTPException(429, "Too many requests. Please wait a minute and try again.")
    q.append(now)

def sniff(b: bytes):
    if b.startswith(b"\x89PNG\r\n\x1a\n"): return "image/png"
    if b.startswith(b"\xff\xd8\xff"): return "image/jpeg"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP": return "image/webp"
    return None

def normalize(ex: dict, text: str) -> dict:
    s = lambda v: str(v).strip()[:300] if v else None
    claims = [{"id": f"C{i+1}", "text": str(c.get("text", "")).strip()[:300]}
              for i, c in enumerate(ex.get("claims") or []) if isinstance(c, dict) and c.get("text")][:5]
    if not claims and text: claims = [{"id": "C1", "text": text[:300]}]
    return {"organization": s(ex.get("organization")), "deadline": s(ex.get("deadline")),
            "urls": [str(u)[:300] for u in (ex.get("urls") or [])][:8], "payment": s(ex.get("payment")),
            "transcript": str(ex.get("transcript") or "")[:3000], "claims": claims}

@app.get("/health")
def health():
    return {"ok": True, "ai": ai.enabled(), "search": search.enabled()}

@app.post("/investigate")
async def investigate(request: Request, text: str = Form(""), file: UploadFile | None = File(None)):
    rate_limit(request)
    text, image, limits = text.strip()[:5000], None, list(BASE_LIMITS)
    if file and file.filename:
        data = await file.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES: raise HTTPException(413, "Image must be 8 MB or smaller.")
        mt = sniff(data)
        if not mt: raise HTTPException(400, "Upload a real PNG, JPEG or WEBP image.")
        if not ai.enabled(): raise HTTPException(400, "Screenshot reading needs ANTHROPIC_API_KEY on the server. Paste the text instead.")
        image = (data, mt)
    if not text and not image: raise HTTPException(400, "Add some text or upload a screenshot first.")

    # 1-2. Upload + Extract
    raw = None
    if ai.enabled():
        try: raw = await ai.extract(text, image)
        except Exception: log.exception("AI extraction failed"); limits.append("AI extraction failed; basic rules were used instead.")
    else: limits.append("AI is not configured (ANTHROPIC_API_KEY); basic rule-based extraction was used.")
    ex = normalize(raw or rules.fallback_extract(text), text)
    full = f"{text}\n{ex['transcript']}"
    claims = ex["claims"]

    # 3. Search
    evidence = []
    if search.enabled() and claims:
        org = ex["organization"]
        qs = ([f"{org} official website", f"{org} scam OR fraud warning"] if org else []) + [c["text"][:150] for c in claims[:3]]
        try: evidence = await search.gather(qs[:5])
        except Exception: log.exception("Search failed")
        if not evidence: limits.append("Web search returned no usable sources.")
    elif not search.enabled(): limits.append("Web search is not configured (TAVILY_API_KEY), so claims could not be checked against sources.")

    # 4. Compare evidence
    verdicts = {}
    if ai.enabled() and evidence:
        try: verdicts = await ai.verify(claims, evidence)
        except Exception: log.exception("Verification failed"); limits.append("AI verification failed; claims are left unverified.")
    out_claims = []
    for c in claims:
        v = verdicts.get(c["id"], {})
        status, reason = v.get("status"), str(v.get("reason") or "").strip()
        ids = [i for i in (v.get("evidence_ids") or []) if str(i).startswith("E") and str(i)[1:].isdigit() and 0 < int(str(i)[1:]) <= len(evidence)]
        if status not in STATUSES or (status in ("verified", "contradicted") and not ids): status = "unverified"
        if not reason or v.get("status") != status: reason = "No official or independent source was found in the retrieved results."
        if status == "unverified" and rules.is_payment(c["text"]):
            status, reason = "suspicious", "An upfront payment is requested before any independent verification. This is a warning sign, not proof of fraud."
        out_claims.append({"id": c["id"], "text": c["text"], "status": status, "reason": reason, "sources": [evidence[int(i[1:]) - 1]["url"] for i in ids]})

    # 5. Report
    inds = rules.indicators(full, ex, out_claims, len(evidence))
    score = min(100, sum(i["weight"] for i in inds))
    overall = "High risk indicators" if score >= 60 else "Some warning signs found" if score >= 30 else "Few warning signs found"
    return {"demo": False, "overall": overall, "risk_score": score,
            "extracted": {k: ex[k] for k in ("organization", "deadline", "urls", "payment")},
            "claims": out_claims, "evidence": evidence, "indicators": inds,
            "next": rules.next_steps(inds), "limits": limits}

# Serve the frontend from the same origin (must be last).
FRONT = Path(__file__).resolve().parent.parent / "frontend"
if FRONT.is_dir(): app.mount("/", StaticFiles(directory=FRONT, html=True), name="frontend")
