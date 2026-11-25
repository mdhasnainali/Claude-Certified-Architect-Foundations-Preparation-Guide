# loop.py — Python 3.12+, anthropic 2.13. Run: uv run --with anthropic python loop.py
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
TOOLS = [
    {
        "name": "get_order_status",
        "description": "Look up ONE order by ID (format ORD-<n>). Returns its status.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    }
]
ORDERS = {"ORD-1": "shipped, arrives in 2 days", "ORD-2": "refunded on 20 Nov"}
messages = [{"role": "user", "content": "Where are my orders ORD-1 and ORD-2?"}]

for turn in range(1, 11):  # safety net only; stop_reason is the real exit
    resp = client.messages.create(
        model="claude-haiku-5-5", max_tokens=4000, tools=TOOLS, messages=messages
    )
    messages.append(
        {"role": "assistant", "content": resp.content}
    )  # keep tool_use blocks
    if resp.stop_reason == "end_turn":
        break
    if resp.stop_reason != "tool_use":
        raise RuntimeError(f"unexpected stop: {resp.stop_reason}")
    results = [
        {
            "type": "tool_result",
            "tool_use_id": b.id,
            "content": ORDERS.get(b.input["order_id"], "error: no such order"),
        }
        for b in resp.content
        if b.type == "tool_use"
    ]
    messages.append({"role": "user", "content": results})  # all results, ONE message
    print(f"turn {turn}: ran {len(results)} tool call(s)")

print(resp.stop_reason, "→", "".join(b.text for b in resp.content if b.type == "text"))
