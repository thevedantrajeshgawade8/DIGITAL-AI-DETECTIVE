# Digital Detective 🔍
Evidence-based message checker: paste a message or upload a screenshot → **Extract** claims (Claude, vision-enabled) → **Search** independent sources (Tavily) → **Compare evidence** (Claude, grounded only in retrieved links) → **Report** with an explainable rule-based risk score.

Team: Prathmesh (Frontend), Vedant (Backend + AI), Archit (Evidence search + testing)

## Run locally
```bash
git clone <your-repo-url> && cd digital-detective
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cp .env.example .env                                    # add your keys (optional, see below)
cd backend && uvicorn main:app --reload
```
Open http://localhost:8000 — the backend serves the frontend, so no extra setup.

| Keys set | Behaviour |
|---|---|
| none | Works in rule-based mode (regex extraction + risk indicators). Claims stay *unverified*. |
| `ANTHROPIC_API_KEY` | AI extraction + screenshot reading |
| + `TAVILY_API_KEY` | Live evidence search and AI claim verification (full pipeline) |

Frontend-only demo: open `frontend/index.html` (demo data, no backend needed).

## API
`POST /investigate` (multipart: `text`, optional `file` PNG/JPEG/WEBP ≤ 8 MB) · `GET /health`

## Honesty & safety design
- Unknown stays **unverified**; `verified`/`contradicted` are downgraded unless backed by a retrieved source.
- Only links actually returned by search appear in reports — no invented citations.
- Message/screenshot text is treated as data; the prompt forbids following instructions inside it.
- API keys live only on the server (`.env`, git-ignored). Upload sniffing, size limit, per-IP rate limit.

## Test
```bash
pip install pytest && pytest tests
```

## Deploy (free)
Render → New → Blueprint → select this repo (uses `render.yaml` + `Dockerfile`), then add the two keys in the dashboard. Put the live URL below:

**Live demo:** _add URL here_
