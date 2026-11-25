# Python 3.13, anthropic 2.14. Run: uv run --env-file .env python <this file>
import json

import anthropic
from anthropic.types import MessageParam, ToolParam, ToolResultBlockParam

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
TOOLS: list[ToolParam] = [
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
messages: list[MessageParam] = [
    {"role": "user", "content": "Where are my orders ORD-1 and ORD-2?"}
]


def show(title: str, body: bytes) -> None:
    print(f"\n{'=' * 20} {title} {'=' * 20}")
    print(json.dumps(json.loads(body), indent=2, ensure_ascii=False))


for turn in range(1, 11):  # safety net only; stop_reason is the real exit
    raw = client.messages.with_raw_response.create(
        model="claude-haiku-5-5", max_tokens=4000, tools=TOOLS, messages=messages
    )
    # Exact JSON bodies on the wire. Headers skipped: they carry the API key.
    req = raw.http_request
    show(f"TURN {turn} REQUEST: {req.method} {req.url}", req.content)
    show(f"TURN {turn} RESPONSE: {raw.status_code}", raw.http_response.content)
    resp = raw.parse()  # same body as a typed Message object

    messages.append({"role": "assistant", "content": resp.content})  # keep tool_use
    if resp.stop_reason == "end_turn":
        text = "".join(b.text for b in resp.content if b.type == "text")
        print(f"\n{'=' * 20} FINAL ANSWER {'=' * 20}\n{text}")
        break
    if resp.stop_reason != "tool_use":
        raise RuntimeError(f"unexpected stop: {resp.stop_reason}")
    results: list[ToolResultBlockParam] = [
        {
            "type": "tool_result",
            "tool_use_id": b.id,
            "content": ORDERS.get(str(b.input["order_id"]), "error: no such order"),
        }
        for b in resp.content
        if b.type == "tool_use"
    ]
    messages.append({"role": "user", "content": results})  # all results, ONE message
else:
    raise RuntimeError("no end_turn after 10 turns")


# ---------------------------------------------------------------------------
# Sample output: make run 1_1_agentic_loop
# ---------------------------------------------------------------------------
# ==================== TURN 1 REQUEST: POST https://api.anthropic.com/v1/messages ====================
# {
#   "max_tokens": 4000,
#   "messages": [
#     {
#       "role": "user",
#       "content": "Where are my orders ORD-1 and ORD-2?"
#     }
#   ],
#   "model": "claude-haiku-5-5",
#   "tools": [
#     {
#       "name": "get_order_status",
#       "description": "Look up ONE order by ID (format ORD-<n>). Returns its status.",
#       "input_schema": {
#         "type": "object",
#         "properties": {
#           "order_id": {
#             "type": "string"
#           }
#         },
#         "required": [
#           "order_id"
#         ]
#       }
#     }
#   ]
# }
#
# ==================== TURN 1 RESPONSE: 200 ====================
# {
#   "model": "claude-haiku-5-5",
#   "id": "msg_011ChQ7UMvCNf1JE5KAniHGp",
#   "type": "message",
#   "role": "assistant",
#   "content": [
#     {
#       "type": "tool_use",
#       "id": "toolu_01QwyjgF9Zgj3yX2Lxc5GhFa",
#       "name": "get_order_status",
#       "input": {
#         "order_id": "ORD-1"
#       },
#       "caller": {
#         "type": "direct"
#       }
#     },
#     {
#       "type": "tool_use",
#       "id": "toolu_01PNrazsrQfekAUQAYqxQbpm",
#       "name": "get_order_status",
#       "input": {
#         "order_id": "ORD-2"
#       },
#       "caller": {
#         "type": "direct"
#       }
#     }
#   ],
#   "container": null,
#   "stop_reason": "tool_use",
#   "stop_sequence": null,
#   "stop_details": null,
#   "usage": {
#     "input_tokens": 406,
#     "cache_creation_input_tokens": 0,
#     "cache_read_input_tokens": 0,
#     "cache_creation": {
#       "ephemeral_5m_input_tokens": 0,
#       "ephemeral_1h_input_tokens": 0
#     },
#     "output_tokens": 107,
#     "output_tokens_details": {
#       "thinking_tokens": 0
#     },
#     "service_tier": "standard",
#     "inference_geo": "global",
#     "speed": "standard"
#   },
#   "diagnostics": null
# }
#
# ==================== TURN 2 REQUEST: POST https://api.anthropic.com/v1/messages ====================
# {
#   "max_tokens": 4000,
#   "messages": [
#     {
#       "role": "user",
#       "content": "Where are my orders ORD-1 and ORD-2?"
#     },
#     {
#       "role": "assistant",
#       "content": [
#         {
#           "id": "toolu_01QwyjgF9Zgj3yX2Lxc5GhFa",
#           "caller": {
#             "type": "direct"
#           },
#           "input": {
#             "order_id": "ORD-1"
#           },
#           "name": "get_order_status",
#           "type": "tool_use"
#         },
#         {
#           "id": "toolu_01PNrazsrQfekAUQAYqxQbpm",
#           "caller": {
#             "type": "direct"
#           },
#           "input": {
#             "order_id": "ORD-2"
#           },
#           "name": "get_order_status",
#           "type": "tool_use"
#         }
#       ]
#     },
#     {
#       "role": "user",
#       "content": [
#         {
#           "type": "tool_result",
#           "tool_use_id": "toolu_01QwyjgF9Zgj3yX2Lxc5GhFa",
#           "content": "shipped, arrives in 2 days"
#         },
#         {
#           "type": "tool_result",
#           "tool_use_id": "toolu_01PNrazsrQfekAUQAYqxQbpm",
#           "content": "refunded on 20 Nov"
#         }
#       ]
#     }
#   ],
#   "model": "claude-haiku-5-5",
#   "tools": [
#     {
#       "name": "get_order_status",
#       "description": "Look up ONE order by ID (format ORD-<n>). Returns its status.",
#       "input_schema": {
#         "type": "object",
#         "properties": {
#           "order_id": {
#             "type": "string"
#           }
#         },
#         "required": [
#           "order_id"
#         ]
#       }
#     }
#   ]
# }
#
# ==================== TURN 2 RESPONSE: 200 ====================
# {
#   "model": "claude-haiku-5-5",
#   "id": "msg_011ChQ7URvJ752q7uQBQQcEa",
#   "type": "message",
#   "role": "assistant",
#   "content": [
#     {
#       "type": "text",
#       "text": "Here's where your two orders stand:\n\n- **ORD-1** has shipped and should arrive in 2 days.\n- **ORD-2** was refunded on 20 Nov, so it won't be delivered.\n\nIf you were expecting ORD-2 to arrive, I can check it again or help you look into the refund."
#     }
#   ],
#   "container": null,
#   "stop_reason": "end_turn",
#   "stop_sequence": null,
#   "stop_details": null,
#   "usage": {
#     "input_tokens": 595,
#     "cache_creation_input_tokens": 0,
#     "cache_read_input_tokens": 0,
#     "cache_creation": {
#       "ephemeral_5m_input_tokens": 0,
#       "ephemeral_1h_input_tokens": 0
#     },
#     "output_tokens": 99,
#     "output_tokens_details": {
#       "thinking_tokens": 0
#     },
#     "service_tier": "standard",
#     "inference_geo": "global",
#     "speed": "standard"
#   },
#   "diagnostics": null
# }
#
# ==================== FINAL ANSWER ====================
# Here's where your two orders stand:
#
# - **ORD-1** has shipped and should arrive in 2 days.
# - **ORD-2** was refunded on 20 Nov, so it won't be delivered.
#
# If you were expecting ORD-2 to arrive, I can check it again or help you look into the refund.
