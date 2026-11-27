# 4_3_extract_tool.py — anthropic 2.13. Run: uv run --with anthropic python 4_3_extract_tool.py
import anthropic

client = anthropic.Anthropic()
NULLABLE = lambda t, d: {"type": [t, "null"], "description": d}
TOOL = {
    "name": "extract_invoice",
    "strict": True,
    "description": "Record the fields of ONE invoice. Use null when the document does not state a field.",
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "vendor",
            "invoice_date",
            "due_date",
            "total",
            "category",
            "category_detail",
        ],
        "properties": {
            "vendor": {"type": "string"},
            "invoice_date": NULLABLE("string", "YYYY-MM-DD"),
            "due_date": NULLABLE(
                "string", "YYYY-MM-DD. null if not stated: never guess"
            ),
            "total": NULLABLE("number", "Amount due in the invoice currency"),
            "category": {
                "type": "string",
                "enum": ["software", "hardware", "services", "other", "unclear"],
            },
            "category_detail": NULLABLE(
                "string", "Required when category is other or unclear"
            ),
        },
    },
}
DOC = "ACME CLOUD LTD. Invoice dated 3 Nov 2026. 12 seats TeamChat Pro: $1,440.00. Payment terms: see contract."

r = client.messages.create(
    model="claude-haiku-5-5",  # accepts forced tool_choice; on Opus 5.5 use auto + "Call extract_invoice"
    max_tokens=1000,
    tools=[TOOL],
    tool_choice={"type": "tool", "name": "extract_invoice"},
    messages=[{"role": "user", "content": DOC}],
)
print(r.stop_reason, next(b.input for b in r.content if b.type == "tool_use"))
