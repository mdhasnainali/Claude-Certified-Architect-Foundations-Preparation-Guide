# 5_2_escalate_test.py — anthropic 2.13. Run: uv run --with anthropic python 5_2_escalate_test.py
import anthropic

client = anthropic.Anthropic()
SYSTEM = """You are a support agent for an online shop.
Call escalate_to_human when: the customer asks for a person (at once, no investigation first);
policy is silent or unclear on the request; or you cannot make progress.
Do NOT escalate only because the customer is upset or the case has several steps.
If a lookup returns several matching customers, call ask_customer for another identifier.
Otherwise call resolve.
<example>"Third broken mug!! Fix it." → resolve: damage replacement; acknowledge the frustration.</example>
<example>"Amazon is $20 cheaper, match it." → escalate_to_human: policy covers only our own price changes.</example>"""


def tool(name: str, desc: str) -> dict:
    return {
        "name": name,
        "description": desc,
        "input_schema": {
            "type": "object",
            "properties": {"note": {"type": "string"}},
            "required": ["note"],
        },
    }


TOOLS = [
    tool("escalate_to_human", "Hand the case to a human. note = reason."),
    tool(
        "ask_customer", "Ask the customer ONE clarifying question. note = the question."
    ),
    tool("resolve", "Solve the case within policy. note = the action taken."),
]
CASES = [
    "I want to talk to a real person, now.",
    "My parcel came damaged, photo attached. So annoying!!",
    "Can you match the price BestDeals has for this TV?",
    "Refund my order. I'm John Smith. [lookup: 3 customers named John Smith]",
]

for case in CASES:
    r = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=2000,
        system=SYSTEM,
        tools=TOOLS,
        messages=[{"role": "user", "content": case}],
    )
    print(
        f"{case[:46]:48} → {[b.name for b in r.content if b.type == 'tool_use'] or ['(text only)']}"
    )
