import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
for k in ("ANTHROPIC_API_KEY", "TAVILY_API_KEY"): os.environ.pop(k, None)
from fastapi.testclient import TestClient
import main, rules

client = TestClient(main.app)
SCAM = "Congratulations! You are selected for the National Student Scholarship. Pay Rs 499 processing fee before midnight to claim your reward. Visit http://bit.ly/abc"

def test_health(): assert client.get("/health").json()["ok"] is True

def test_scam_scores_high_without_keys():
    d = client.post("/investigate", data={"text": SCAM}).json()
    assert d["risk_score"] >= 60 and any(c["status"] == "suspicious" for c in d["claims"])
    assert d["evidence"] == []   # never invents sources

def test_empty_rejected(): assert client.post("/investigate", data={"text": ""}).status_code == 400
def test_fake_image_rejected():
    r = client.post("/investigate", files={"file": ("x.png", b"not an image", "image/png")})
    assert r.status_code in (400,)
def test_clean_text_low(): assert rules.indicators("Meeting at 5pm in room 2.", {}, [], 1) == []
