# sessions_sdk.py — claude-agent-sdk 0.2.188. Run: uv run --with claude-agent-sdk python sessions_sdk.py
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query


async def run(prompt: str, **opts) -> str | None:
    sid = None
    async for m in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model="haiku",  # without this it uses the CLI default model
            allowed_tools=["Read", "Grep", "Glob"],
            **opts,
        ),
    ):
        if isinstance(m, ResultMessage):
            sid = m.session_id
            print(f"[{m.subtype}] session={sid}\n{m.result or ''}\n")
    return sid


async def main():
    base = await run("Map this repo's test setup: frameworks, fixtures, slow tests.")
    # Branch A and B start from the SAME analysis; base stays unchanged
    a = await run(
        "Plan approach A: speed up tests with parallel runs.",
        resume=base,
        fork_session=True,
    )
    b = await run(
        "Plan approach B: speed up tests with better fixtures.",
        resume=base,
        fork_session=True,
    )
    # Later: continue the original line of work with a targeted update
    await run(
        "I edited tests/conftest.py since your analysis. Re-read only that file, "
        "then update your summary.",
        resume=base,
    )


asyncio.run(main())


# ---------------------------------------------------------------------------
# Sample output: make run 1_7
# Forks A and B get NEW session ids; the plain resume (last run) keeps base id ea97c20b.
# ---------------------------------------------------------------------------
# [success] session=ea97c20b-7296-4e27-9f3b-0ba9fc74290a
# Repo has no test suite. Nothing to map as tests.
#
# **Frameworks:** none. No pytest, unittest, or other test runner in `pyproject.toml`, `uv.lock` (0 pytest hits), or `.gitignore` beyond `.pytest_cache/` entry. `.ruff_cache/` exists, so ruff was run at some point, but it's not a declared dependency and no lint config exists.
#
# **Test files:** zero. No `test_*.py`, `*_test.py`, `conftest.py`, `pytest.ini`, `tox.ini`, `setup.cfg`, `.coveragerc`, or CI config (`.github/` absent). Only `.venv/` hits are third-party packages.
#
# **Fixtures / mocks:** none. No `mock`, `fixture`, `unittest`, or `assert` in project code.
#
# **What exists instead:**
# - `Makefile`: `make run <code>` → `uv run --env-file .env python D*/*/<code>_*.py`. Manual smoke runs, not tests. Needs `ANTHROPIC_API_KEY` in `.env`.
# - Code files in `D1-Agentic-Architecture-and-Orchestration/codes/` (677 lines total) each end with `asyncio.run(demo())` / `main()` / a top-level script. They are demos that print output, not assertions.
#
# **Slow parts (the closest thing to slow tests):** every run is a live API call.
# - `1_1`, `1_6`: direct `client.messages.create` (`claude-haiku-5-5`). Network + model latency.
# - `1_2`, `1_7`: Agent SDK `query()`, which spawns the Claude CLI subprocess. Slowest path. Multi-agent in `1_2` = several sequential model calls.
# - `1_4`, `1_5`: `asyncio.run(demo())` over SDK. Also live.
# - No `sleep` calls in code. Nothing offline. Every run costs tokens and needs network.
#
# **Gaps / notes:**
# - Nothing verifiable offline. Hooks (`1_5`), enforcement (`1_4`), decomposition (`1_6`) logic can't be asserted without a mock layer.
# - Cheap next step if wanted: add `pytest` as dev dep, put pure helpers (`extra/` inventory/pricing/orders, parsing in `1_3`) under test, stub the SDK/client for the agent files. Say the word and I'll set it up.
# - Repo state: `1_2_...py` is modified; `1_4`–`1_7` and `extra/` are untracked. Test map reflects working tree.
# - Didn't read `.env` (secret). Didn't run anything.
#
# [success] session=12c18d96-1879-4184-9983-56715ae7042a
# Plan only. Nothing edited or run.
#
# **Blocker:** repo has no tests (see last report). "Approach A" isn't in my earlier options, so I'm not sure which one you mean. Two candidates below; pick one.
#
# **Option 1: parallel unit tests (needs the tests first)**
# 1. Add dev deps: `pytest`, `pytest-xdist`. Via `uv add --dev`.
# 2. `pyproject.toml`: `[tool.pytest.ini_options]` with `addopts = "-n auto"`.
# 3. `tests/`: unit tests for pure code only: `extra/inventory.py`, `pricing.py`, `orders.py`, and parsing in `1_3`. No network.
# 4. Stub the Anthropic client and Agent SDK `query()` for the agent files. No live calls in the suite.
# 5. Run: `uv run pytest -n auto`. Each test independent, so xdist is safe. Check for shared module state first (`extra/` may hold globals).
#
# Gain: seconds, not minutes. Fails if I skip step 4 and tests hit the API.
#
# **Option 2: parallel live smoke runs (works now, no tests needed)**
# 1. Add a `make smoke` target: list all codes, run `make run <code>` via `xargs -P 4`.
# 2. Each run writes its own log file (`logs/<code>.log`) so output doesn't interleave. Print pass/fail per code at end.
# 3. Run: `make smoke`.
#
# Gain: wall-clock drops roughly by the parallel factor. Costs: every run burns tokens; concurrency may hit rate limits (keep `-P` low, 2–4). Agent SDK runs spawn CLI subprocesses, so they're heavier.
#
# **My pick:** Option 1 if you want a real test suite, Option 2 if you only want faster checks of the demos. Tell me which, and whether `-P` 4 is OK for Option 2. I'll start on your word.
#
# [success] session=3097ace0-628d-4de4-9d9f-154b4a931c74
# Can't find "approach B" in this chat. I never proposed A or B, and I haven't saved a plan file. Also, there are no tests yet, so "speed up tests" has nothing to speed up. Tell me if B means something else. If it means my earlier "add tests + stub the SDK" idea, here's the plan.
#
# **Plan: fast offline test harness, with fixtures**
#
# 1. **Add pytest as dev dep.** `uv add --dev pytest`. Changes `pyproject.toml` and `uv.lock`, so I need your OK first.
# 2. **Fix import-time API calls (blocker).** `1_2`, `1_4`, `1_5`, `1_7` call `asyncio.run(...)` at column 0. No `if __name__ == "__main__":` guard in any file. So importing a lesson fires live API calls. Tests can't import these safely. Fix: wrap each entry point in a `__main__` guard. Touches your study files, so needs OK. Code-behavior unchanged for `make run`.
# 3. **`conftest.py` fixtures (session scope where safe):**
#    - `block_network`: autouse; patches `socket.socket.connect` to raise. Any accidental live call fails in ms instead of hanging.
#    - `fake_client`: monkeypatches `anthropic.Anthropic` so `messages.create` returns canned `Message` objects. Covers `1_1`, `1_6`.
#    - `fake_query`: replaces `claude_agent_sdk.query` with a scripted async generator. Covers `1_2`, `1_7`, and the SDK paths in `1_4`/`1_5`.
#    - `load_lesson`: session-scoped, `importlib` loader with a cache, so each file imports once.
# 4. **Marker `@pytest.mark.live`** for real-API smoke tests. Skipped by default; run with `pytest -m live`, needs `.env`.
# 5. **Test pure helpers first.** `extra/` (inventory, pricing, orders) and parsing in `1_3`. No fixtures needed, fastest wins.
# 6. **Verify:** `pytest` runs offline in under a few seconds. Baseline: time a run before and after.
#
# Open questions:
# - Is B the above, or something else?
# - OK to add pytest and edit `uv.lock`?
# - OK to add `__main__` guards to the four lesson files?
#
# [success] session=ea97c20b-7296-4e27-9f3b-0ba9fc74290a
# `tests/conftest.py` doesn't exist. Read returned "File does not exist" from this repo root. Nothing to re-read, so my summary stands as-is. Earlier scan for `conftest.py` also found none.
#
# Possible causes:
# - Edit saved elsewhere, or path differs (e.g. `D1-.../tests/conftest.py`, or repo root `conftest.py`).
# - Edit not saved, or in another clone/worktree.
#
# Give me the exact path, or confirm it should be created. Then I re-read that one file and update the summary.
