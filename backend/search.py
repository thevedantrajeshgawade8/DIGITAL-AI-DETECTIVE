"""Evidence retrieval through the Tavily search API. Only really retrieved links are ever returned."""
import asyncio, os
from datetime import datetime, timezone
import httpx


def enabled() -> bool:
    return bool(os.getenv("TAVILY_API_KEY"))


async def _one(client: httpx.AsyncClient, query: str) -> list[dict]:
    r = await client.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {os.environ['TAVILY_API_KEY']}"},
        json={"query": query, "max_results": 4, "search_depth": "basic"},
    )
    r.raise_for_status()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return [{"title": x.get("title") or x["url"], "url": x["url"],
             "snippet": (x.get("content") or "")[:320], "retrieved": now}
            for x in r.json().get("results", []) if x.get("url", "").startswith("http")]


async def gather(queries: list[str]) -> list[dict]:
    async with httpx.AsyncClient(timeout=20) as client:
        results = await asyncio.gather(*[_one(client, q) for q in queries], return_exceptions=True)
    seen, out = set(), []
    for res in results:
        if isinstance(res, Exception):
            continue
        for e in res:
            if e["url"] not in seen:
                seen.add(e["url"]); out.append(e)
    return out[:10]
