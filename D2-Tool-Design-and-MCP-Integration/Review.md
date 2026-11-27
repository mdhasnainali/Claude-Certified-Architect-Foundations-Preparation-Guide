# D2 Review

## Goal
After this you can answer mixed Domain 2 scenario questions in about 2 minutes each, and upgrade a real tool set with clear boundaries and structured errors.

## Guess first
Warm-up, from memory, before you read anything below:
1. Write one line for each lesson 2.1 → 2.5. Which one feels weakest?
2. Official sample question 2: why is "expand the tool descriptions" right, and "add a routing layer" wrong?

## Idea
The whole level on one screen:
1. **Descriptions drive selection** — what, when / when not, inputs, outputs, limits. Fix overlap by renaming and rewriting; split vague multi-job tools; watch system-prompt keywords. *(2.1)*
2. **Errors are data for the agent** — `isError: true` plus `errorCategory` (transient / validation / business / permission), `isRetryable`, a clear message. Empty result ≠ failure. Recover locally first. *(2.2)*
3. **Few tools per agent** — 4–5 role tools, one narrow cross-role tool for frequent needs. `tool_choice`: `auto` may answer in text, `any` guarantees a call, a forced tool guarantees *that* call. *(2.3)*
4. **MCP config** — team servers in project `.mcp.json`, personal ones in `~/.claude.json`, secrets via `${VAR}`. Catalogs as resources, actions as tools. Reuse community servers. *(2.4)*
5. **Built-ins** — Grep = contents, Glob = names, Edit = exact + unique (fallback Read + Write). Explore by search → read → follow imports; trace wrapper exports. *(2.5)*

## Code
The mini-project upgrades `support_tools.py` from [D1 Review](../D1-Agentic-Architecture-and-Orchestration/Review.md). Here is the new **part 1** (helpers and data), ready to use. It replaces the top of the old file.

```python
# support_tools.py v2 — part 1: helpers and data. claude-agent-sdk 0.2.188
import json
from claude_agent_sdk import create_sdk_mcp_server, tool

CUSTOMERS = {"ana@example.com": {"customer_id": "C7", "verified": True}}
ORDERS = {"ORD-9": {"customer_id": "C7", "total": 650.0, "status": "delivered", "month": "2026-10"}}
DB_UP = True  # set False to simulate an outage

def ok(data) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(data)}]}

def structured_error(category: str, retryable: bool, message: str, **details) -> dict:
    body = {"errorCategory": category, "isRetryable": retryable, "message": message, **details}
    return {"content": [{"type": "text", "text": json.dumps(body)}], "is_error": True}
```
In Agent SDK custom tools you return `"is_error": True` (the in-process server turns it into MCP `isError`).

## When to use · gotchas
Fast mapping from question words to the D2 answer:

| The question says… | Think… |
|---|---|
| agent picks the wrong one of two similar tools | Rewrite descriptions with boundaries (first step) |
| tool picks drift after a system-prompt change | Keyword-sensitive instruction |
| "Operation failed" everywhere, wasted retries | Structured errors: category + `isRetryable` |
| "no results" while the service was down | Access failure ≠ valid empty result |
| agent has 15+ tools / uses tools outside its role | Scope tools per role; one narrow cross-role tool |
| must always get structured output | `tool_choice: any` (or a forced tool) |
| must run step X first | Force tool X, then `auto` |
| teammates don't get the server | Project `.mcp.json`, not user scope |
| secret in config | `${ENV_VAR}` expansion |
| agent explores just to see what exists | MCP resources as a catalog |
| callers / error text / imports | Grep · file names → Glob |
| Edit fails, text not unique | More context, `replace_all`, or Read + Write |

## Try it
*≤ 30 min. Needs `ANTHROPIC_API_KEY`; costs well under $1.* Upgrade the L1 support agent:
1. Use the new part 1 above. Keep `get_customer`, `process_refund`, `escalate_to_human` from L1.
2. Replace `lookup_order` with a version that has a description with boundaries, and add a similar tool `get_order_history`. *(2.1)*
3. Return a transient structured error when `DB_UP` is `False`; return "not found" and "no orders" as normal results. *(2.2)*
4. Add `get_order_history` to the server, to `allowed_tools`, and to the `require_verified` hook's matcher. *(2.3)*
5. In `run_session()`, print each tool the agent calls. Run: *"I'm ana@example.com. What did I buy in October?"* and *"…Where is ORD-9?"* Each should hit a different tool. Then set `DB_UP = False` and run again: the agent should say the system is down, not "you have no orders".

<details><summary>Solution</summary>

```python
# support_tools.py v2 — part 2: tools with boundaries + structured errors
@tool("lookup_order", "Get ONE order by its number (ORD-<n>): items, total, delivery status. "
      "Use when the customer names a specific order. For 'what did I buy / my past orders' "
      "use get_order_history instead. Needs a verified customer_id from get_customer.",
      {"customer_id": str, "order_id": str})
async def lookup_order(args):
    if not DB_UP:
        return structured_error("transient", True, "Order database timeout.", retry_after_s=2)
    order = ORDERS.get(args["order_id"])
    if not order:  # the query worked, there is just no match: a result, not an error
        return ok({"found": False, "order_id": args["order_id"], "hint": "Ask the customer to check the number."})
    return ok({"found": True, **order})

@tool("get_order_history", "List ALL orders of one verified customer, newest first (number, "
      "month, total, status). Use for 'my past orders', 'what did I buy in October'. Does not "
      "return item details; call lookup_order for one order's details.", {"customer_id": str})
async def get_order_history(args):
    if not DB_UP:
        return structured_error("transient", True, "Order database timeout.", retry_after_s=2)
    # an empty list is a valid answer ("no orders yet"), NOT an error
    return ok([{"order_id": order_id, **order} for order_id, order in ORDERS.items()
               if order["customer_id"] == args["customer_id"]])
```
Then add `get_order_history` to the `create_sdk_mcp_server(..., tools=[...])` list. In `support_agent.py`: add `"get_order_history"` to the `allowed_tools` names, use the matcher `f"{TOOL_PREFIX}lookup_order|{TOOL_PREFIX}get_order_history|{TOOL_PREFIX}process_refund"` for `require_verified`, and inside `run_session()`'s loop add:
```python
        if isinstance(message, AssistantMessage):        # import AssistantMessage, ToolUseBlock
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print("  tool →", block.name)
```
Expected: "What did I buy in October?" → `get_customer`, `get_order_history`. "Where is ORD-9?" → `get_customer`, `lookup_order`. With `DB_UP = False` the agent apologises that the order system is unavailable and may retry once.

</details>

## Quiz
Exam style: about 2 minutes each. Then redo official sample questions 2 and 9 (exam guide p.29, exam guide p.33).

**1.** `search_docs` ("Searches documents") and `search_kb` ("Searches the knowledge base") index the same wiki plus a ticket system. The agent alternates between them at random. Most effective first step? A) Merge them behind a router · B) Add 8 few-shot examples · C) Rewrite both descriptions: what each indexes, when to use it, when to use the other · D) Lower temperature

<details><summary>Answer</summary>

**C.** Overlapping descriptions are the root cause. A is bigger than a first step, B adds tokens without fixing it, D is unrelated (and not even allowed on new models).

</details>

**2.** **Choose 2.** Which should be returned as `isError: true`? A) Payment API timed out · B) Search ran fine and matched 0 tickets · C) Refund exceeds the policy limit · D) Customer has no past orders

<details><summary>Answer</summary>

**A and C.** A is transient (retryable), C is a business error (not retryable, explain to customer). B and D are valid empty results.

</details>

**3.** An extraction pipeline must always return structured JSON through one of 3 schema tools, and the document type is unknown. Which `tool_choice`?

<details><summary>Answer</summary>

`{"type": "any"}` — guarantees a tool call while letting Claude pick the matching schema.

</details>

**4.** You want to try an experimental MCP server without affecting teammates. Where?

<details><summary>Answer</summary>

User scope (`~/.claude.json`, e.g. `claude mcp add --scope user …`). Not the project's `.mcp.json`.

</details>

**5.** An Edit keeps failing because the anchor text appears in 4 places, and you need to change only one of them. Options?

<details><summary>Answer</summary>

Extend `old_string` with surrounding lines until it is unique, or Read the file and Write the full new version.

</details>

**6.** A research subagent's database query times out. It returns `{"results": []}` as success. What goes wrong downstream, and what should it return?

<details><summary>Answer</summary>

The coordinator believes there is no data and the report states a false gap or false conclusion. Return a structured transient error (`isError: true`, `isRetryable: true`, attempted query, partial results).

</details>

**7.** A report-writing agent has Read, Write, Edit, Bash, WebSearch and 12 CRM tools. It sometimes edits source files and runs searches. Fix?

<details><summary>Answer</summary>

Restrict it to its role: e.g. Read + Write for the report output, plus a narrow lookup tool if it really needs one. Remove Bash, Edit, WebSearch and the CRM tools.

</details>

**8.** Agents keep calling `describe_table` many times to learn the database. What MCP design helps?

<details><summary>Answer</summary>

Expose the schema as a resource catalog (e.g. `db://schema`, `db://tables/{name}`) so the agent sees the structure without exploratory calls.

</details>

**9.** *(D1)* Three MCP tools return timestamps as Unix seconds, ISO 8601 and `DD/MM/YYYY`. The agent mixes up dates. Most reliable fix?

<details><summary>Answer</summary>

A `PostToolUse` hook that normalises all formats before the model sees the results — deterministic, unlike a prompt instruction.

</details>

**10.** *(D1)* Your coordinator has `allowed_tools=["Read", "mcp__crm__*"]` and three subagents defined. It never delegates. Why?

<details><summary>Answer</summary>

The subagent tool (`Task` in the exam, `Agent` today) is not in `allowedTools`, so the coordinator can't spawn subagents.

</details>

## References
- [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Give Claude custom tools — handle errors](https://code.claude.com/docs/en/agent-sdk/custom-tools)
