# 2_1_pick_test.py — anthropic 2.13. Run: uv run --with anthropic python 2_1_pick_test.py
import anthropic

client = anthropic.Anthropic()
SOURCE_INPUT_SCHEMA = {
    "type": "object",
    "properties": {"source": {"type": "string"}},
    "required": ["source"],
}
VAGUE_TOOLS = [
    {
        "name": "analyze_content",
        "description": "Analyzes content and returns insights.",
        "input_schema": SOURCE_INPUT_SCHEMA,
    },
    {
        "name": "analyze_document",
        "description": "Analyzes a document and returns insights.",
        "input_schema": SOURCE_INPUT_SCHEMA,
    },
]
CLEAR_TOOLS = [
    {
        "name": "extract_web_results",
        "input_schema": SOURCE_INPUT_SCHEMA,
        "description": "Extract facts from WEB SEARCH RESULTS already fetched in this conversation. source = the "
        "search query they came from. Use for anything found online. Never use for files or PDFs.",
    },
    {
        "name": "analyze_document",
        "input_schema": SOURCE_INPUT_SCHEMA,
        "description": "Analyze ONE uploaded file (PDF, DOCX, report). source = file name, e.g. q3-report.pdf. "
        "Returns key figures with page numbers. Use only for files, never for web search results.",
    },
]
QUERIES = [
    "Pull the key numbers from q3-report.pdf",
    "What did the search results for 'EU AI Act fines' say?",
    "Check the report's revenue claim against what we found online",
]


def pick_tools(tools: list, query: str) -> list[str]:
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=2000,
        tools=tools,
        messages=[{"role": "user", "content": query}],
    )
    return [block.name for block in response.content if block.type == "tool_use"] or [
        "(no tool)"
    ]


for query in QUERIES:
    print(
        f"{query[:40]:42} vague → {pick_tools(VAGUE_TOOLS, query)}\n"
        f"{'':42} clear → {pick_tools(CLEAR_TOOLS, query)}"
    )


# ---------------------------------------------------------------------------
# Sample output: make run 2_1
# ---------------------------------------------------------------------------
# Pull the key numbers from q3-report.pdf    vague → ['analyze_document']
#                                            clear → ['analyze_document']
# What did the search results for 'EU AI A   vague → ['(no tool)']
#                                            clear → ['extract_web_results']
# Check the report's revenue claim against   vague → ['(no tool)']
#                                            clear → ['(no tool)']
