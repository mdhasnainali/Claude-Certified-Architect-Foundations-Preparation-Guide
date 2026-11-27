# 1_5_hooks.py — Python 3.13+. Runs offline: python3 1_5_hooks.py
import asyncio, json
from datetime import datetime, timezone

STATUS_NAMES = {0: "pending", 1: "shipped", 2: "delivered", 9: "cancelled"}


def normalize_order(order: dict) -> dict:
    if isinstance(order.get("updated"), (int, float)):  # Unix seconds → ISO 8601
        order["updated"] = datetime.fromtimestamp(
            order["updated"], timezone.utc
        ).isoformat()
    if isinstance(order.get("status"), int):  # numeric code → word
        order["status"] = STATUS_NAMES.get(
            order["status"], f"unknown({order['status']})"
        )
    return order


# PostToolUse hook, matcher "^mcp__"
async def normalize_output(input_data, tool_use_id, context):
    order = normalize_order(
        json.loads(input_data["tool_response"]["content"][0]["text"])
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "updatedToolOutput": {
                "content": [{"type": "text", "text": json.dumps(order)}]
            },
        }
    }


# PreToolUse hook, matcher: process_refund
async def enforce_refund_limit(input_data, tool_use_id, context):
    if input_data["tool_input"]["amount"] <= 500:
        return {}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Refunds over $500 need a human. Call escalate_to_human.",
        }
    }


async def demo():
    tool_response = {
        "content": [
            {
                "type": "text",
                "text": '{"order": "ORD-9", "status": 1, "updated": 1764000000}',
            }
        ]
    }
    print(
        (await normalize_output({"tool_response": tool_response}, None, None))[
            "hookSpecificOutput"
        ]["updatedToolOutput"]
    )
    print(await enforce_refund_limit({"tool_input": {"amount": 120}}, None, None))
    print(await enforce_refund_limit({"tool_input": {"amount": 900}}, None, None))


asyncio.run(demo())


# ---------------------------------------------------------------------------
# Sample output: make run 1_5
# ---------------------------------------------------------------------------
# {'content': [{'type': 'text', 'text': '{"order": "ORD-9", "status": "shipped", "updated": "2025-11-24T16:00:00+00:00"}'}]}
# {}
# {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': 'Refunds over $500 need a human. Call escalate_to_human.'}}
