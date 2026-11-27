# hooks_demo.py — Python 3.12+. Runs offline: python3 hooks_demo.py
import asyncio, json
from datetime import datetime, timezone

STATUS = {0: "pending", 1: "shipped", 2: "delivered", 9: "cancelled"}


def normalize(rec: dict) -> dict:
    if isinstance(rec.get("updated"), (int, float)):  # Unix seconds → ISO 8601
        rec["updated"] = datetime.fromtimestamp(
            rec["updated"], timezone.utc
        ).isoformat()
    if isinstance(rec.get("status"), int):  # numeric code → word
        rec["status"] = STATUS.get(rec["status"], f"unknown({rec['status']})")
    return rec


async def normalize_output(inp, tool_use_id, ctx):  # PostToolUse, matcher "^mcp__"
    rec = normalize(json.loads(inp["tool_response"]["content"][0]["text"]))
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "updatedToolOutput": {
                "content": [{"type": "text", "text": json.dumps(rec)}]
            },
        }
    }


async def refund_limit(inp, tool_use_id, ctx):  # PreToolUse, matcher process_refund
    if inp["tool_input"]["amount"] <= 500:
        return {}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Refunds over $500 need a human. Call escalate_to_human.",
        }
    }


async def demo():
    raw = {
        "content": [
            {
                "type": "text",
                "text": '{"order": "ORD-9", "status": 1, "updated": 1764000000}',
            }
        ]
    }
    print(
        (await normalize_output({"tool_response": raw}, None, None))[
            "hookSpecificOutput"
        ]["updatedToolOutput"]
    )
    print(await refund_limit({"tool_input": {"amount": 120}}, None, None))
    print(await refund_limit({"tool_input": {"amount": 900}}, None, None))


asyncio.run(demo())


# ---------------------------------------------------------------------------
# Sample output: make run 1_5
# ---------------------------------------------------------------------------
# {'content': [{'type': 'text', 'text': '{"order": "ORD-9", "status": "shipped", "updated": "2025-11-24T16:00:00+00:00"}'}]}
# {}
# {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': 'Refunds over $500 need a human. Call escalate_to_human.'}}
