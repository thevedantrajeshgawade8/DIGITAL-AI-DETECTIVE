"""Explainable rule-based risk indicators + a no-API-key fallback extractor."""
import re
from urllib.parse import urlparse

I = re.I
PAYMENT = re.compile(r"((processing|registration|claim|security|delivery|handling|verification)\s+(fee|charge|deposit)"
                     r"|\b(pay|send|transfer|deposit)\b[^.]{0,60}(₹|rs\.?|inr|\$|usd)\s?\d[\d,]*"
                     r"|(₹|rs\.?|inr|\$)\s?\d[\d,]*[^.]{0,40}\b(fee|to claim|to receive|to unlock))", I)
URGENCY = re.compile(r"(before midnight|within \d+\s*(hours?|hrs?|minutes?|mins?)|last chance|today only|expires?|"
                     r"immediately|urgent|act now|hurry|limited (slots|seats)|final warning)", I)
GUARANTEE = re.compile(r"(guaranteed|100% (selection|placement|job|refund)|you (are|have been) selected|"
                       r"you (won|have won)|congratulations|lottery|no interview|assured (job|selection))", I)
CREDS = re.compile(r"\b(otp|password|pin|cvv|aadhaar|pan (number|card)|bank (details|account)|card number)\b", I)
URL = re.compile(r"https?://[^\s)>\]]+|\b(?:www\.|bit\.ly/|tinyurl\.com/)[^\s)>\]]+", I)
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "cutt.ly", "rb.gy", "is.gd", "shorturl.at"}
BAD_TLD = (".xyz", ".top", ".click", ".work", ".icu", ".buzz", ".tk", ".ml", ".cf", ".gq", ".zip", ".loan")
DEADLINE = re.compile(r"(before midnight|within \d+\s*\w+|by \w+ \d{1,2}|today|tonight|in \d+\s*(hours?|days?)|deadline[^.]*)", I)
ORG = re.compile(r"((?:[A-Z][\w&.\-]+\s){1,5}(?:Scholarship|Foundation|University|Institute|Bank|Ltd|Pvt|Company|"
                 r"Corporation|Services|Yojana|Scheme|Commission|Fellowship))")


def is_payment(text: str) -> bool:
    return bool(PAYMENT.search(text or ""))


def fallback_extract(text: str) -> dict:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) > 15][:5]
    pay, dl, org = PAYMENT.search(text), DEADLINE.search(text), ORG.search(text)
    return {"organization": org.group(1).strip() if org else None,
            "deadline": dl.group(0) if dl else None,
            "urls": URL.findall(text),
            "payment": pay.group(0) if pay else None,
            "transcript": "",
            "claims": [{"id": f"C{i+1}", "text": s} for i, s in enumerate(sentences)]}


def _bad_url(u: str) -> bool:
    host = (urlparse(u if "//" in u else "http://" + u).hostname or "").lower()
    return (host in SHORTENERS or host.endswith(BAD_TLD) or "xn--" in host or "@" in u
            or bool(re.fullmatch(r"[\d.]+", host)) or host.count("-") >= 3)


def indicators(text: str, ex: dict, claims: list[dict], n_evidence: int) -> list[dict]:
    out = []
    def add(name, w): out.append({"name": name, "weight": w, "max": 30})
    if ex.get("payment") or is_payment(text): add("Unusual upfront payment request", 25)
    if URGENCY.search(text): add("High-pressure deadline", 10)
    if GUARANTEE.search(text): add("Unsupported guaranteed-selection claim", 15)
    if any(_bad_url(u) for u in ex.get("urls", [])): add("Suspicious or shortened link", 20)
    if CREDS.search(text): add("Asks for sensitive credentials", 20)
    if any(c["status"] == "contradicted" for c in claims): add("Claim contradicted by retrieved sources", 25)
    elif claims and n_evidence == 0: add("No independent source found", 5)
    return out


def next_steps(inds: list[dict]) -> list[str]:
    names = {i["name"] for i in inds}
    steps = []
    if "Unusual upfront payment request" in names: steps.append("Do not pay anything until the offer is independently verified.")
    if "Asks for sensitive credentials" in names: steps.append("Never share OTPs, passwords, PINs or card details by message.")
    if "Suspicious or shortened link" in names: steps.append("Do not open the link. Type the organization's official address yourself.")
    steps += ["Contact the organization using details you found independently.",
              "Report the message to the platform or to cybercrime.gov.in (India) if it looks like fraud."]
    return steps
