# 2_2_errors_server.py — mcp 2.3 (Python SDK). Offline: uv run --with mcp python 2_2_errors_server.py
import asyncio, json
from mcp import Client
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

billing_server = MCPServer("billing")
gateway_call_count = 0


def structured_error(
    category: str, retryable: bool, message: str, **details
) -> ToolError:
    return ToolError(
        json.dumps(
            {
                "errorCategory": category,
                "isRetryable": retryable,
                "message": message,
                **details,
            }
        )
    )


@billing_server.tool()
def refund(order_id: str, amount: float) -> str:
    """Refund one order (ORD-<n>), max $500. Larger refunds need a human."""
    global gateway_call_count
    if not order_id.startswith("ORD-"):
        raise structured_error(
            "validation", False, "order_id must look like ORD-123", got=order_id
        )
    if amount > 500:
        raise structured_error(
            "business",
            False,
            "Over the $500 agent limit.",
            customer_message="A specialist will review this refund within 24 hours.",
        )
    gateway_call_count += 1
    if gateway_call_count == 1:  # simulate one gateway timeout
        raise structured_error(
            "transient", True, "Payment gateway timeout after 10 s.", retry_after_s=2
        )
    return json.dumps({"refunded": amount, "order_id": order_id})


async def main():
    async with Client(billing_server) as client:
        for order_id, amount in [
            ("123", 50),
            ("ORD-9", 900),
            ("ORD-9", 50),
            ("ORD-9", 50),
        ]:
            result = await client.call_tool(
                "refund", {"order_id": order_id, "amount": amount}
            )
            print(result.is_error, result.content[0].text)


asyncio.run(main())
