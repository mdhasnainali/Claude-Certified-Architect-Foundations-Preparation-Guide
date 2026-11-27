# 2_1_pick_test.py — anthropic 2.13. Run: uv run --with anthropic python 2_1_pick_test.py
import anthropic

client = anthropic.Anthropic()
ARG = {
    "type": "object",
    "properties": {"source": {"type": "string"}},
    "required": ["source"],
}
VAGUE = [
    {
        "name": "analyze_content",
        "description": "Analyzes content and returns insights.",
        "input_schema": ARG,
    },
    {
        "name": "analyze_document",
        "description": "Analyzes a document and returns insights.",
        "input_schema": ARG,
    },
]
CLEAR = [
    {
        "name": "extract_web_results",
        "input_schema": ARG,
        "description": "Extract facts from WEB SEARCH RESULTS already fetched in this conversation. source = the "
        "search query they came from. Use for anything found online. Never use for files or PDFs.",
    },
    {
        "name": "analyze_document",
        "input_schema": ARG,
        "description": "Analyze ONE uploaded file (PDF, DOCX, report). source = file name, e.g. q3-report.pdf. "
        "Returns key figures with page numbers. Use only for files, never for web search results.",
    },
]
QUERIES = [
    "Pull the key numbers from q3-report.pdf",
    "What did the search results for 'EU AI Act fines' say?",
    "Check the report's revenue claim against what we found online",
]


def pick(tools: list, query: str) -> list[str]:
    r = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=2000,
        tools=tools,
        messages=[{"role": "user", "content": query}],
    )
    return [b.name for b in r.content if b.type == "tool_use"] or ["(no tool)"]


for q in QUERIES:
    print(f"{q[:40]:42} vague → {pick(VAGUE, q)}\n{'':42} clear → {pick(CLEAR, q)}")
