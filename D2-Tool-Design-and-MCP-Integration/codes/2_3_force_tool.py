# 2_3_force_tool.py — anthropic 2.13. Run: uv run --with anthropic python 2_3_force_tool.py
import anthropic

client = anthropic.Anthropic()


def obj(*names: str) -> dict:
    return {
        "type": "object",
        "properties": {n: {"type": "string"} for n in names},
        "required": list(names),
    }


TOOLS = [
    {
        "name": "extract_metadata",
        "input_schema": obj("title", "author", "date", "doc_type"),
        "description": "Extract title, author, date (YYYY-MM-DD) and document type from a document. Run first.",
    },
    {
        "name": "enrich_company",
        "input_schema": obj("company"),
        "description": "Look up industry and size for ONE company named in a document.",
    },
]
DOC = "Q3 Report — Acme Robotics. Author: Dana Lee. 2 Oct 2026. Revenue grew 12% on warehouse robots."
MODEL = "claude-haiku-5-5"  # accepts forced tool_choice; Opus 5.5 / Sonnet 5.5 return 400 for any/tool

for choice in (
    {"type": "auto"},
    {"type": "any"},
    {"type": "tool", "name": "extract_metadata"},
):
    r = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        tools=TOOLS,
        tool_choice=choice,
        messages=[{"role": "user", "content": f"Here is a document:\n{DOC}"}],
    )
    calls = [(b.name, b.input) for b in r.content if b.type == "tool_use"]
    print(f"{choice['type']:5} stop={r.stop_reason:9} calls={calls}")
