# 5_4_manifest.py — Python 3.13+, offline. Crash recovery: agents save state; a new coordinator resumes from a manifest.
import json, pathlib, tempfile

STATE_DIR = pathlib.Path(tempfile.mkdtemp())


def save_agent_state(
    agent: str, done: list[str], findings: list[str], next_step: str
) -> None:
    (STATE_DIR / f"{agent}.json").write_text(
        json.dumps({"done": done, "findings": findings, "next": next_step})
    )
    manifest = {
        path.stem: path.name
        for path in STATE_DIR.glob("*.json")
        if path.stem != "manifest"
    }
    # one known place to look
    (STATE_DIR / "manifest.json").write_text(json.dumps(manifest))


save_agent_state(
    "test-mapper",
    ["listed 212 test files"],
    ["pytest; shared fixtures in tests/conftest.py"],
    "find the 10 slowest tests",
)
save_agent_state(
    "refund-tracer",
    ["traced refund_order → issue_refund → gateway.pay"],
    ["no retry on gateway timeout"],
    "check jobs/nightly.py",
)

# ---- the process crashes here; a fresh coordinator starts with an empty context ----
manifest = json.loads((STATE_DIR / "manifest.json").read_text())
summary_lines = []
for agent, state_file in sorted(manifest.items()):
    state = json.loads((STATE_DIR / state_file).read_text())
    summary_lines.append(
        f"- {agent}: done {state['done']}; found {state['findings']}; next: {state['next']}"
    )
print(
    "Resume the investigation. Saved state from before the restart:\n"
    + "\n".join(summary_lines)
)
