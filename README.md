# Claude Certified Architect — Foundations Preparation Guide

Study notes and runnable code for the Claude Certified Architect (Foundations) exam, one folder per domain.

## Domains

| # | Domain | Code |
|---|--------|------|
| D1 | Agentic Architecture and Orchestration | [`D1-Agentic-Architecture-and-Orchestration/codes`](D1-Agentic-Architecture-and-Orchestration/codes) |

## Setup

Needs Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
```

## Run an example

```bash
uv run --env-file .env python D1-Agentic-Architecture-and-Orchestration/codes/1_1_agentic_loop.py
```
