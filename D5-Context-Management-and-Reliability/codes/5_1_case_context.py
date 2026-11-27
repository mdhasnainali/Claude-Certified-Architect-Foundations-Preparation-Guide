# 5_1_case_context.py — Python 3.13+, offline. Build every turn's prompt so key facts can't get lost.
import json

RAW_ORDER = {
    "order_id": "ORD-9",
    "status": "delivered",
    "total": 650.0,
    "delivered_at": "2026-11-20",
    "return_window_days": 30,
    **{f"internal_field_{i}": "x" * 20 for i in range(40)},
}
KEEP_FIELDS = ("order_id", "status", "total", "delivered_at", "return_window_days")


def trim_order(record: dict) -> dict:  # cut tool output BEFORE it enters the history
    return {field: record[field] for field in KEEP_FIELDS if field in record}


CASE_FACTS = {  # exact values, kept OUTSIDE the summarised history
    "customer_id": "C7",
    "verified": True,
    "issues": [
        {
            "order_id": "ORD-9",
            "problem": "arrived broken",
            "amount": 650.00,
            "status": "refund awaiting approval",
        },
        {
            "order_id": "ORD-12",
            "problem": "charged twice",
            "amount": 89.99,
            "status": "investigating",
        },
    ],
    "customer_expects": "refund to original card by 2026-11-27",
}


def build_prompt(summary: str, recent_turns: list[str], task: str) -> str:
    return (
        f"<case_facts>\n{json.dumps(CASE_FACTS)}\n</case_facts>\n"  # top: always present, exact
        f"<earlier_conversation_summary>\n{summary}\n</earlier_conversation_summary>\n"
        f"<recent_turns>\n" + "\n".join(recent_turns) + "\n</recent_turns>\n"
        f"<task>\n{task}\n</task>"
    )  # bottom: the ask


print(
    "order record:",
    len(json.dumps(RAW_ORDER)),
    "chars → trimmed:",
    len(json.dumps(trim_order(RAW_ORDER))),
    "chars",
)
print(
    build_prompt(
        "Customer reported two problems; identity verified; damage photo received.",
        ["Customer: Any news on the double charge?"],
        "Write the next reply to the customer.",
    )
)
