# 2_4_kb_server.py — mcp 2.3 (Python SDK). Started by Claude Code over stdio (see .mcp.json).
import json
from mcp.server import MCPServer

mcp = MCPServer("team-kb")
DOCS = {
    "deploy": "Deploy: merge to main, CI builds image, ArgoCD syncs to prod within 5 min.",
    "oncall": "On-call: PagerDuty rotation weekly, handoff Monday 10:00, runbooks in /runbooks.",
    "db-schema": "Tables: users(id, email), orders(id, user_id, total, status).",
}


@mcp.resource("kb://index")
def index() -> str:
    """Catalog of every team doc: slug and first sentence. Read this before searching."""
    return json.dumps({slug: text.split(".")[0] for slug, text in DOCS.items()})


@mcp.resource("kb://docs/{slug}")
def doc(slug: str) -> str:
    """Full text of one team doc by slug (see kb://index for slugs)."""
    return DOCS[slug]


@mcp.tool()
def search_kb(query: str) -> str:
    """Full-text search over team docs (deploy, on-call, DB schema). Returns matching slugs
    with their text. Use for team-internal how-to questions, not for searching code."""
    hits = {s: t for s, t in DOCS.items() if query.lower() in t.lower()}
    return json.dumps(hits)  # empty {} = valid "no match", not an error


if __name__ == "__main__":
    mcp.run()
