# D1 Review

## Goal
After this you can answer mixed Domain 1 scenario questions in about 2 minutes each, and build one small agent that uses every idea of D1.

## Guess first
Warm-up, from memory, before you read anything below:
1. Write one line for each lesson 1.1 → 1.7. Which one feels weakest?
2. Official sample question 1: why is "a programmatic prerequisite" right and "few-shot examples" wrong?

## Idea
The whole level on one screen:
1. **Loop** — continue on `tool_use`, stop on `end_turn`; tool results go back into `messages`. Text and caps are not exit signals. *(1.1)*
2. **Coordinator** — decompose broadly → choose subagents by complexity → aggregate → refine gaps; all traffic through the hub. Subagents get only their prompt: pass full, structured findings; spawn in parallel in one response. *(1.2, 1.3)*
3. **Must-happen rules live in code** — prerequisite gates and hooks (`PreToolUse` blocks or rewrites, `PostToolUse` cleans results). Prompts are probabilistic. Escalate with a self-contained handoff. *(1.4, 1.5)*
4. **Known steps → prompt chain** (per-file passes + one integration pass). **Unknown steps → dynamic plan** that adapts. *(1.6)*
5. **Context still valid → resume** (and name what changed). **Compare approaches → fork.** **Stale → fresh session + summary.** *(1.7)*

## Code
The mini-project below needs a fake backend. Here it is, ready to use. `claude-agent-sdk` 0.2.188. Save as `support_tools.py` (no need to run it alone).

```python
# support_tools.py — claude-agent-sdk 0.2.188. A fake backend as an in-process MCP server "support".
import json
from claude_agent_sdk import create_sdk_mcp_server, tool

CUSTOMERS = {"ana@example.com": {"customer_id": "C7", "verified": True}}
ORDERS = {"ORD-9": {"customer_id": "C7", "total": 650.0, "status": "delivered"}}

def reply(data: dict, error: bool = False) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(data)}], "is_error": error}

@tool("get_customer", "Find and verify a customer by email. Call before any order or refund tool.", {"email": str})
async def get_customer(args):
    customer = CUSTOMERS.get(args["email"])
    return reply(customer) if customer else reply({"error": "not_found", "retryable": False}, error=True)

@tool("lookup_order", "Get ONE order (ORD-<n>) of a verified customer.", {"customer_id": str, "order_id": str})
async def lookup_order(args):
    order = ORDERS.get(args["order_id"])
    return reply(order) if order else reply({"error": "not_found", "retryable": False}, error=True)

@tool("process_refund", "Refund one order. amount in USD.", {"customer_id": str, "order_id": str, "amount": float})
async def process_refund(args):
    return reply({"refunded": args["amount"], "order_id": args["order_id"]})

@tool("escalate_to_human", "Hand the case to a human. summary = complete JSON handoff.", {"summary": str})
async def escalate_to_human(args):
    print("HANDOFF →", args["summary"])
    return reply({"ticket": "T-1001", "status": "queued"})

server = create_sdk_mcp_server("support", tools=[get_customer, lookup_order, process_refund, escalate_to_human])
```
The tools are exposed to Claude as `mcp__support__get_customer`, `mcp__support__lookup_order`, and so on.

## When to use · gotchas
Fast mapping from question words to the D1 answer:

| The question says… | Think… |
|---|---|
| "must always", "guarantee", money, identity, compliance | Programmatic gate / `PreToolUse` hook |
| different formats from several tools | `PostToolUse` normalisation |
| "agent stops early" / "never finishes" | Loop control on `stop_reason`, not text or caps |
| report misses whole areas, subagents fine | Coordinator decomposition too narrow |
| subagent output generic / missing sources | Context not passed, or passed unstructured |
| subagents slow, independent work | Several Task calls in one response |
| many files, uneven review | Per-file passes + integration pass |
| open-ended investigation | Dynamic decomposition |
| files changed since the last session | Tell it what changed (few) / fresh + summary (many) |
| compare two approaches from one analysis | Fork the session |

## Try it
*≤ 30 min. Needs `ANTHROPIC_API_KEY`; costs well under $1.* Build `support_agent.py` in the same folder as `support_tools.py`. It must:
1. Load the `support` MCP server and auto-approve its 4 tools. *(1.3 allowed tools)*
2. Block `lookup_order` and `process_refund` until `get_customer` returned a verified ID. *(1.4)*
3. Block refunds over $500 and redirect to `escalate_to_human` with a JSON handoff. *(1.5)*
4. Print the `ResultMessage` subtype and result for each request. *(1.1)*
5. Ask: *"I'm ana@example.com. ORD-9 arrived broken and I want my $650 back."* — then **resume** with a follow-up, then **fork** to try store credit instead. *(1.7)*

Run `uv run --with claude-agent-sdk python support_agent.py`. You should see a `HANDOFF →` line with the exact amount, then `[success]` lines.

<details><summary>Solution (two blocks, one file)</summary>

```python
# support_agent.py — part 1: hooks (lessons 1.4 + 1.5)
import asyncio, json
from dataclasses import replace
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, ResultMessage, query
from support_tools import server

TOOL_PREFIX = "mcp__support__"
verified_customers: set[str] = set()

def deny(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny", "permissionDecisionReason": reason}}

async def remember_verified(input_data, tool_use_id, context):     # PostToolUse on get_customer
    customer = json.loads(input_data["tool_response"]["content"][0]["text"])
    if customer.get("verified"):
        verified_customers.add(customer["customer_id"])
    return {}

async def require_verified(input_data, tool_use_id, context):      # PreToolUse on lookup_order | process_refund
    if input_data["tool_input"].get("customer_id") in verified_customers:
        return {}
    return deny("Customer not verified. Call get_customer first.")

async def enforce_refund_limit(input_data, tool_use_id, context):  # PreToolUse on process_refund
    if input_data["tool_input"]["amount"] <= 500:
        return {}
    return deny("Refunds over $500 need a human. Call escalate_to_human with a JSON handoff.")
```
```python
# support_agent.py — part 2: options, loop result, sessions (lessons 1.1 + 1.7)
options = ClaudeAgentOptions(
    system_prompt="You are a support agent. When you escalate, the handoff JSON has: customer_id, "
                  "issue, root_cause, amount, done_so_far, recommended_action.",
    mcp_servers={"support": server},
    allowed_tools=[TOOL_PREFIX + name for name in ("get_customer", "lookup_order", "process_refund", "escalate_to_human")],
    hooks={"PostToolUse": [HookMatcher(matcher=TOOL_PREFIX + "get_customer", hooks=[remember_verified])],
           "PreToolUse": [HookMatcher(matcher=f"{TOOL_PREFIX}lookup_order|{TOOL_PREFIX}process_refund",
                                      hooks=[require_verified]),
                          HookMatcher(matcher=TOOL_PREFIX + "process_refund", hooks=[enforce_refund_limit])]},
)

async def run_session(prompt: str, **session_options) -> str:
    session_id = ""
    async for message in query(prompt=prompt, options=replace(options, **session_options)):
        if isinstance(message, ResultMessage):          # loop finished: check WHY (subtype)
            session_id = message.session_id
            print(f"[{message.subtype}] {message.result}\n")
    return session_id

async def main():
    base_session_id = await run_session("I'm ana@example.com. ORD-9 arrived broken and I want my $650 back.")
    await run_session("Also: please send the refund to my other card.", resume=base_session_id)
    await run_session("Instead of a refund, offer store credit.", resume=base_session_id, fork_session=True)

asyncio.run(main())
```
Expected (wording varies): `get_customer` → `lookup_order` → `process_refund` is denied by `enforce_refund_limit` → `HANDOFF → {"customer_id": "C7", "issue": "ORD-9 arrived broken", "amount": 650.0, ...}` → `[success] I've passed your case to a colleague…`. The resumed run remembers the case; the fork explores store credit without changing the original session.
**Stretch:** add a read-only `policy-checker` subagent (`AgentDefinition`) and `"Agent"` to `allowed_tools`.

</details>

## Quiz
Exam style: about 2 minutes each. Then redo official sample questions 1, 7 and 8 (exam guide p.28, exam guide p.32).

**1.** A coordinator starts the synthesis subagent with "Combine the findings into a report." The report is generic, with no numbers. Why? A) The synthesis model is too small · B) The findings were never put in the subagent's prompt · C) `max_tokens` is too low · D) The coordinator needs extended thinking

<details><summary>Answer</summary>

**B.** Subagents don't inherit the coordinator's context. The only input is the Task prompt — it must contain the findings, ideally structured with sources.

</details>

**2.** A loop runs `while response.stop_reason != "end_turn":` and treats every other value as "run tools". What breaks?

<details><summary>Answer</summary>

A `max_tokens` or `refusal` response has no tool calls, so the loop sends an empty or invalid turn — errors or spins. Continue only on `"tool_use"`; handle `max_tokens`, `refusal` and `pause_turn` explicitly.

</details>

**3.** An agent must never send a full card number by email (`send_email` tool). Best control? A) A system-prompt rule · B) A `PreToolUse` hook on `send_email` that denies (or redacts via `updatedInput`) bodies with card numbers · C) A `PostToolUse` hook that scans sent emails · D) Few-shot examples of safe emails

<details><summary>Answer</summary>

**B.** Compliance needs a deterministic check *before* the action. C is too late — the email is gone.

</details>

**4.** Research on "effects of remote work": three searchers return overlapping articles on productivity; nothing on mental health or real estate. Root cause and fix?

<details><summary>Answer</summary>

The coordinator decomposed narrowly and didn't partition the scope. Have it list the sub-areas first and give each searcher a distinct one.

</details>

**5.** You mapped a monorepo for an hour in session `mono-map`. Tomorrow you want to try two refactoring approaches and keep the map clean. A) Resume `mono-map` in two terminals · B) `claude --resume mono-map --fork-session`, once per approach · C) `/compact`, then continue · D) Two fresh sessions that redo the map

<details><summary>Answer</summary>

**B.** Forks share the baseline and leave the original unchanged. A can lose messages; D wastes the hour.

</details>

**6.** Every week, 200 contracts are checked for the same 6 clauses. Which decomposition?

<details><summary>Answer</summary>

A fixed pipeline (prompt chain) per contract: extract clauses → check each rule → report. The steps are known in advance; dynamic decomposition adds cost and unpredictability.

</details>

**7.** Escalations currently paste the last 20 chat messages. Human agents still re-ask the customer for basics. Best improvement? A) Paste the full transcript · B) A structured handoff: customer ID, issue, root cause, amounts, actions taken, recommended action · C) Add a sentiment score · D) Give humans database access

<details><summary>Answer</summary>

**B.** Humans need the facts and the next step at a glance; more raw text (A) is slower to read.

</details>

**8.** Web search and document analysis are independent but run one after the other. Fastest fix?

<details><summary>Answer</summary>

The coordinator emits both Task calls in one response so the subagents run in parallel.

</details>

**9.** **Choose 2.** Which rules belong in hooks rather than in the prompt? A) Block transfers over $10,000 without approval · B) Use a friendly tone · C) Convert every tool timestamp to ISO 8601 before the model sees it · D) Prefer short answers · E) Suggest related products

<details><summary>Answer</summary>

**A and C.** A is a guaranteed business rule (`PreToolUse`). C is deterministic data normalisation (`PostToolUse`). B, D and E are soft preferences — prompts are fine.

</details>

**10.** A refund flow always runs the same 4 steps in the same order, with no judgment. A teammate proposes an agent with 12 tools. Best design? A) The agent with 12 tools · B) A fixed workflow in code (or a prompt chain) · C) A coordinator with 4 subagents · D) An agent with an iteration cap of 4

<details><summary>Answer</summary>

**B.** Use model-driven agents when the steps can't be predicted. A known, fixed sequence is cheaper and safer as code.

</details>

## References
- [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- [Custom tools / in-process MCP servers](https://code.claude.com/docs/en/agent-sdk/custom-tools)
