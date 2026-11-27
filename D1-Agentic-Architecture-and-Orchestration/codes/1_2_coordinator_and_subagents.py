# 1_2_coordinator_and_subagents.py — claude-agent-sdk 0.2.188. Run: uv run --with claude-agent-sdk python 1_2_coordinator_and_subagents.py
import asyncio
from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    ToolUseBlock,
    query,
)

COORDINATOR_PROMPT = """You lead a research team. Goal: a cited brief that covers EVERY major
sub-area of the topic. First list the sub-areas, aiming for breadth.
Give each searcher a DIFFERENT sub-area. Quality bar: 2+ sources per sub-area;
name gaps, never hide them. If synthesis shows a gap, search again, then re-synthesize."""

SUBAGENTS = {
    "searcher": AgentDefinition(
        description="Web research on ONE assigned sub-area. Returns claims with sources.",
        prompt="Research only your sub-area. Return a JSON list of {claim, url, date}.",
        tools=["WebSearch", "WebFetch"],
        model="haiku",
    ),
    "synthesizer": AgentDefinition(
        description="Merges findings given in its prompt into a cited brief. Lists gaps.",
        prompt="Use only the findings in your prompt. Keep each claim's source.",
        tools=["Read"],
        model="haiku",
    ),
}


async def main():
    options = ClaudeAgentOptions(
        model="haiku",  # the coordinator; without this it uses the CLI default model
        system_prompt=COORDINATOR_PROMPT,
        agents=SUBAGENTS,
        max_budget_usd=0.5,
        # "Agent" = built-in tool that starts a subagent; listing it auto-approves it.
        allowed_tools=["Agent", "WebSearch", "WebFetch"],
    )
    async for message in query(
        prompt="Topic: impact of AI on creative industries", options=options
    ):
        if (
            isinstance(message, AssistantMessage) and message.parent_tool_use_id is None
        ):  # coordinator only
            for block in message.content:
                # Same tool, two names: "Agent" now, "Task" before Claude Code v2.1.63
                # (the init tools list still says "Task"). Match both for old/new SDKs.
                if isinstance(block, ToolUseBlock) and block.name in ("Agent", "Task"):
                    print(
                        "DELEGATE →",
                        block.input.get("subagent_type"),
                        "|",
                        block.input.get("description"),
                    )
        if isinstance(message, ResultMessage):
            print(
                message.subtype, message.result if message.subtype == "success" else ""
            )


asyncio.run(main())


# ---------------------------------------------------------------------------
# Sample output: make run 1_2_coordinator_and_subagents
# ---------------------------------------------------------------------------
# DELEGATE → searcher | AI in visual art and design
# DELEGATE → searcher | AI in music production
# DELEGATE → searcher | AI in writing and publishing
# DELEGATE → searcher | AI in film and video
# DELEGATE → synthesizer | Merge findings into a cited brief
# success # Impact of AI on creative industries ...
