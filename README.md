# Claude Certified Architect — Foundations Preparation Guide

Study notes and runnable code for the Claude Certified Architect (Foundations) exam, one folder per domain.

## Domains

| # | Domain | Weight | Covers |
|---|---|---|---|
| [D1](#d1--agentic-architecture--orchestration) | Agentic Architecture & Orchestration | 27% | the tool loop, coordinator + subagents, hooks that enforce rules, sessions |
| [D2](#d2--tool-design--mcp-integration) | Tool Design & MCP Integration | 18% | tool descriptions, structured errors, tool choice, MCP servers, built-in tools |
| [D3](#d3--claude-code-configuration--workflows) | Claude Code Configuration & Workflows | 20% | CLAUDE.md levels, commands, skills, path rules, plan mode, CI |
| [D4](#d4--prompt-engineering--structured-output) | Prompt Engineering & Structured Output | 20% | explicit criteria, few-shot, tool_use + JSON schema, validation, batches, multi-pass review |
| [D5](#d5--context-management--reliability) | Context Management & Reliability | 15% | case facts, escalation, error propagation, human review, provenance |

Each lesson: Goal → Guess first → Idea → Code → Gotchas → Try it → Quiz → References. Each domain ends with a Review: mixed scenario questions and a mini-project.

## Lessons

### D1 · Agentic Architecture & Orchestration

- [1.1 Agentic Loop](D1-Agentic-Architecture-and-Orchestration/1.1-Agentic-Loop.md)
- [1.2 Coordinator and Subagents](D1-Agentic-Architecture-and-Orchestration/1.2-Coordinator-and-Subagents.md)
- [1.3 Spawning Subagents and Passing Context](D1-Agentic-Architecture-and-Orchestration/1.3-Spawning-Subagents-and-Passing-Context.md)
- [1.4 Enforcement and Handoffs](D1-Agentic-Architecture-and-Orchestration/1.4-Enforcement-and-Handoffs.md)
- [1.5 Hooks](D1-Agentic-Architecture-and-Orchestration/1.5-Hooks.md)
- [1.6 Task Decomposition](D1-Agentic-Architecture-and-Orchestration/1.6-Task-Decomposition.md)
- [1.7 Sessions Resume and Fork](D1-Agentic-Architecture-and-Orchestration/1.7-Sessions-Resume-and-Fork.md)
- [D1 Review](D1-Agentic-Architecture-and-Orchestration/Review.md)
- Code: [`D1-Agentic-Architecture-and-Orchestration/codes`](D1-Agentic-Architecture-and-Orchestration/codes)

### D2 · Tool Design & MCP Integration

- [2.1 Tool Descriptions and Boundaries](D2-Tool-Design-and-MCP-Integration/2.1-Tool-Descriptions-and-Boundaries.md)
- [2.2 Structured Tool Errors](D2-Tool-Design-and-MCP-Integration/2.2-Structured-Tool-Errors.md)
- [2.3 Tool Distribution and Tool Choice](D2-Tool-Design-and-MCP-Integration/2.3-Tool-Distribution-and-Tool-Choice.md)
- [2.4 MCP Servers in Claude Code](D2-Tool-Design-and-MCP-Integration/2.4-MCP-Servers-in-Claude-Code.md)
- [2.5 Built-in Tools](D2-Tool-Design-and-MCP-Integration/2.5-Built-in-Tools.md)
- [D2 Review](D2-Tool-Design-and-MCP-Integration/Review.md)
- Code: [`D2-Tool-Design-and-MCP-Integration/codes`](D2-Tool-Design-and-MCP-Integration/codes)

### D3 · Claude Code Configuration & Workflows

- [3.1 CLAUDE.md Hierarchy](D3-Claude-Code-Configuration-and-Workflows/3.1-CLAUDE.md-Hierarchy.md)
- [3.2 Commands and Skills](D3-Claude-Code-Configuration-and-Workflows/3.2-Commands-and-Skills.md)
- [3.3 Path-Specific Rules](D3-Claude-Code-Configuration-and-Workflows/3.3-Path-Specific-Rules.md)
- [3.4 Plan Mode vs Direct Execution](D3-Claude-Code-Configuration-and-Workflows/3.4-Plan-Mode-vs-Direct-Execution.md)
- [3.5 Iterative Refinement](D3-Claude-Code-Configuration-and-Workflows/3.5-Iterative-Refinement.md)
- [3.6 Claude Code in CI](D3-Claude-Code-Configuration-and-Workflows/3.6-Claude-Code-in-CI.md)
- [D3 Review](D3-Claude-Code-Configuration-and-Workflows/Review.md)
- Code: [`D3-Claude-Code-Configuration-and-Workflows/codes`](D3-Claude-Code-Configuration-and-Workflows/codes)

### D4 · Prompt Engineering & Structured Output

- [4.1 Explicit Criteria](D4-Prompt-Engineering-and-Structured-Output/4.1-Explicit-Criteria.md)
- [4.2 Few-Shot Examples](D4-Prompt-Engineering-and-Structured-Output/4.2-Few-Shot-Examples.md)
- [4.3 Structured Output with Tool Use](D4-Prompt-Engineering-and-Structured-Output/4.3-Structured-Output-with-Tool-Use.md)
- [4.4 Validation and Retry Loops](D4-Prompt-Engineering-and-Structured-Output/4.4-Validation-and-Retry-Loops.md)
- [4.5 Batch Processing](D4-Prompt-Engineering-and-Structured-Output/4.5-Batch-Processing.md)
- [4.6 Multi-Pass Review](D4-Prompt-Engineering-and-Structured-Output/4.6-Multi-Pass-Review.md)
- [D4 Review](D4-Prompt-Engineering-and-Structured-Output/Review.md)
- Code: [`D4-Prompt-Engineering-and-Structured-Output/codes`](D4-Prompt-Engineering-and-Structured-Output/codes)

### D5 · Context Management & Reliability

- [5.1 Case Facts and Long Context](D5-Context-Management-and-Reliability/5.1-Case-Facts-and-Long-Context.md)
- [5.2 Escalation and Ambiguity](D5-Context-Management-and-Reliability/5.2-Escalation-and-Ambiguity.md)
- [5.3 Error Propagation](D5-Context-Management-and-Reliability/5.3-Error-Propagation.md)
- [5.4 Context in Codebase Exploration](D5-Context-Management-and-Reliability/5.4-Context-in-Codebase-Exploration.md)
- [5.5 Human Review and Confidence](D5-Context-Management-and-Reliability/5.5-Human-Review-and-Confidence.md)
- [5.6 Provenance and Uncertainty](D5-Context-Management-and-Reliability/5.6-Provenance-and-Uncertainty.md)
- [D5 Review](D5-Context-Management-and-Reliability/Review.md)
- Code: [`D5-Context-Management-and-Reliability/codes`](D5-Context-Management-and-Reliability/codes)

## Setup

Needs Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
```

## Run an example

```bash
make run 1_1   # code = <domain>_<lesson>; runs D1-*/codes/1_1_*.py
make run 2_1   # runs D2-*/codes/2_1_*.py
make run 4_5_sla   # a lesson with two files: give the full name
```

Same as `uv run --env-file .env python <path>`. D3 shell scripts (`3_*.sh`) create a demo project in the current folder, so run them from an empty folder: `bash path/to/3_1_setup.sh`.
