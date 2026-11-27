# 1_4_enforcement_and_handoffs.py — Python 3.13+. Runs offline: python3 1_4_enforcement_and_handoffs.py (same callback shape the Agent SDK calls)
import asyncio

# customer IDs that get_customer has verified this session
verified_customers: set[str] = set()


# PostToolUse hook, matcher: get_customer
async def remember_verified(input_data, tool_use_id, context):
    if input_data["tool_response"].get("verified"):
        verified_customers.add(input_data["tool_input"]["customer_id"])
    return {}


# PreToolUse hook, matcher: lookup_order|process_refund
async def require_verified(input_data, tool_use_id, context):
    customer_id = input_data["tool_input"].get("customer_id")
    if customer_id in verified_customers:
        return {}  # no decision → normal permission flow
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Customer {customer_id} is not verified. Call get_customer first.",
        }
    }


async def demo():
    refund_call = {
        "tool_name": "mcp__support__process_refund",
        "tool_input": {"customer_id": "C7", "amount": 40},
    }
    print("before:", await require_verified(refund_call, None, None))
    await remember_verified(
        {
            "tool_name": "mcp__support__get_customer",
            "tool_input": {"customer_id": "C7"},
            "tool_response": {"verified": True},
        },
        None,
        None,
    )
    print("after: ", await require_verified(refund_call, None, None))


asyncio.run(demo())


# ---------------------------------------------------------------------------
# Sample output: make run 1_4
# ---------------------------------------------------------------------------
# before: {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': 'Customer C7 is not verified. Call get_customer first.'}}
# after:  {}
