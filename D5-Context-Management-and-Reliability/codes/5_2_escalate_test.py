# 5_2_escalate_test.py — anthropic 2.13. Run: uv run --with anthropic python 5_2_escalate_test.py
import anthropic

client = anthropic.Anthropic()
SYSTEM_PROMPT = """You are a support agent for an online shop.
Call escalate_to_human when: the customer asks for a person (at once, no investigation first);
policy is silent or unclear on the request; or you cannot make progress.
Do NOT escalate only because the customer is upset or the case has several steps.
If a lookup returns several matching customers, call ask_customer for another identifier.
Otherwise call resolve.
<example>"Third broken mug!! Fix it." → resolve: damage replacement; acknowledge the frustration.</example>
<example>"Amazon is $20 cheaper, match it." → escalate_to_human: policy covers only our own price changes.</example>"""


def make_tool(name: str, description: str) -> dict:
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": {"note": {"type": "string"}},
            "required": ["note"],
        },
    }


TOOLS = [
    make_tool("escalate_to_human", "Hand the case to a human. note = reason."),
    make_tool(
        "ask_customer", "Ask the customer ONE clarifying question. note = the question."
    ),
    make_tool("resolve", "Solve the case within policy. note = the action taken."),
]
CUSTOMER_MESSAGES = [
    "I want to talk to a real person, now.",
    "My parcel came damaged, photo attached. So annoying!!",
    "Can you match the price BestDeals has for this TV?",
    "Refund my order. I'm John Smith. [lookup: 3 customers named John Smith]",
]

for customer_message in CUSTOMER_MESSAGES:
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=[{"role": "user", "content": customer_message}],
    )
    tools_called = [
        block.name for block in response.content if block.type == "tool_use"
    ]
    print(f"{customer_message[:46]:48} → {tools_called or ['(text only)']}")
