# 2_2_errors_server.py — mcp 2.3 (Python SDK). Offline: uv run --with mcp python 2_2_errors_server.py
import asyncio, json
from mcp import Client
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp, gateway_calls = MCPServer("billing"), [0]


def fail(category: str, retryable: bool, message: str, **extra) -> ToolError:
    return ToolError(
        json.dumps(
            {
                "errorCategory": category,
                "isRetryable": retryable,
                "message": message,
                **extra,
            }
        )
    )


@mcp.tool()
def refund(order_id: str, amount: float) -> str:
    """Refund one order (ORD-<n>), max $500. Larger refunds need a human."""
    if not order_id.startswith("ORD-"):
        raise fail("validation", False, "order_id must look like ORD-123", got=order_id)
    if amount > 500:
        raise fail(
            "business",
            False,
            "Over the $500 agent limit.",
            customer_message="A specialist will review this refund within 24 hours.",
        )
    gateway_calls[0] += 1
    if gateway_calls[0] == 1:  # simulate one gateway timeout
        raise fail(
            "transient", True, "Payment gateway timeout after 10 s.", retry_after_s=2
        )
    return json.dumps({"refunded": amount, "order_id": order_id})


async def main():
    async with Client(mcp) as c:
        for oid, amt in [("123", 50), ("ORD-9", 900), ("ORD-9", 50), ("ORD-9", 50)]:
            r = await c.call_tool("refund", {"order_id": oid, "amount": amt})
            print(r.is_error, r.content[0].text)


asyncio.run(main())
