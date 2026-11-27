# gate.py — Python 3.12+. Runs offline: python3 gate.py (same callback shape the Agent SDK calls)
import asyncio

verified: set[str] = set()  # customer IDs that get_customer has verified this session


async def remember_verified(
    inp, tool_use_id, ctx
):  # PostToolUse, matcher: get_customer
    if inp["tool_response"].get("verified"):
        verified.add(inp["tool_input"]["customer_id"])
    return {}


async def require_verified(
    inp, tool_use_id, ctx
):  # PreToolUse, matcher: lookup_order|process_refund
    cid = inp["tool_input"].get("customer_id")
    if cid in verified:
        return {}  # no decision → normal permission flow
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Customer {cid} is not verified. Call get_customer first.",
        }
    }


async def demo():
    refund = {
        "tool_name": "mcp__support__process_refund",
        "tool_input": {"customer_id": "C7", "amount": 40},
    }
    print("before:", await require_verified(refund, None, None))
    await remember_verified(
        {
            "tool_name": "mcp__support__get_customer",
            "tool_input": {"customer_id": "C7"},
            "tool_response": {"verified": True},
        },
        None,
        None,
    )
    print("after: ", await require_verified(refund, None, None))


asyncio.run(demo())


# ---------------------------------------------------------------------------
# Sample output: make run 1_4
# ---------------------------------------------------------------------------
# before: {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': 'Customer C7 is not verified. Call get_customer first.'}}
# after:  {}
