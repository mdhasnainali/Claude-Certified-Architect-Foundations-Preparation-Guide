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
make run 1_1   # code = <domain>_<lesson>; runs D1-*/codes/1_1_*.py
make run 2_1   # runs D2-*/codes/2_1_*.py
```

Same as `uv run --env-file .env python <path>`.
