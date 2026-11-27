# 2_3_force_tool.py — anthropic 2.13. Run: uv run --with anthropic python 2_3_force_tool.py
import anthropic

client = anthropic.Anthropic()


def string_fields_schema(*field_names: str) -> dict:
    return {
        "type": "object",
        "properties": {name: {"type": "string"} for name in field_names},
        "required": list(field_names),
    }


TOOLS = [
    {
        "name": "extract_metadata",
        "input_schema": string_fields_schema("title", "author", "date", "doc_type"),
        "description": "Extract title, author, date (YYYY-MM-DD) and document type from a document. Run first.",
    },
    {
        "name": "enrich_company",
        "input_schema": string_fields_schema("company"),
        "description": "Look up industry and size for ONE company named in a document.",
    },
]
DOCUMENT = "Q3 Report — Acme Robotics. Author: Dana Lee. 2 Oct 2026. Revenue grew 12% on warehouse robots."
MODEL = "claude-haiku-5-5"  # accepts forced tool_choice; Opus 5.5 / Sonnet 5.5 return 400 for any/tool

for tool_choice in (
    {"type": "auto"},
    {"type": "any"},
    {"type": "tool", "name": "extract_metadata"},
):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        tools=TOOLS,
        tool_choice=tool_choice,
        messages=[{"role": "user", "content": f"Here is a document:\n{DOCUMENT}"}],
    )
    tool_calls = [
        (block.name, block.input)
        for block in response.content
        if block.type == "tool_use"
    ]
    print(f"{tool_choice['type']:5} stop={response.stop_reason:9} calls={tool_calls}")
