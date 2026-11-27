# 2_4_kb_server.py — mcp 2.3 (Python SDK). Started by Claude Code over stdio (see .mcp.json).
import json
from mcp.server import MCPServer

kb_server = MCPServer("team-kb")
TEAM_DOCS = {
    "deploy": "Deploy: merge to main, CI builds image, ArgoCD syncs to prod within 5 min.",
    "oncall": "On-call: PagerDuty rotation weekly, handoff Monday 10:00, runbooks in /runbooks.",
    "db-schema": "Tables: users(id, email), orders(id, user_id, total, status).",
}


@kb_server.resource("kb://index")
def doc_index() -> str:
    """Catalog of every team doc: slug and first sentence. Read this before searching."""
    return json.dumps({slug: text.split(".")[0] for slug, text in TEAM_DOCS.items()})


@kb_server.resource("kb://docs/{slug}")
def read_doc(slug: str) -> str:
    """Full text of one team doc by slug (see kb://index for slugs)."""
    return TEAM_DOCS[slug]


@kb_server.tool()
def search_kb(query: str) -> str:
    """Full-text search over team docs (deploy, on-call, DB schema). Returns matching slugs
    with their text. Use for team-internal how-to questions, not for searching code."""
    matches = {
        slug: text for slug, text in TEAM_DOCS.items() if query.lower() in text.lower()
    }
    return json.dumps(matches)  # empty {} = valid "no match", not an error


if __name__ == "__main__":
    kb_server.run()
