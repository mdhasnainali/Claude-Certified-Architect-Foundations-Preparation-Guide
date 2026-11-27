# 5_4_manifest.py — Python 3.13+, offline. Crash recovery: agents save state; a new coordinator resumes from a manifest.
import json, pathlib, tempfile

STATE = pathlib.Path(tempfile.mkdtemp())


def save(agent: str, done: list[str], findings: list[str], next_step: str) -> None:
    (STATE / f"{agent}.json").write_text(
        json.dumps({"done": done, "findings": findings, "next": next_step})
    )
    manifest = {p.stem: p.name for p in STATE.glob("*.json") if p.stem != "manifest"}
    (STATE / "manifest.json").write_text(
        json.dumps(manifest)
    )  # one known place to look


save(
    "test-mapper",
    ["listed 212 test files"],
    ["pytest; shared fixtures in tests/conftest.py"],
    "find the 10 slowest tests",
)
save(
    "refund-tracer",
    ["traced refund_order → issue_refund → gateway.pay"],
    ["no retry on gateway timeout"],
    "check jobs/nightly.py",
)

# ---- the process crashes here; a fresh coordinator starts with an empty context ----
manifest = json.loads((STATE / "manifest.json").read_text())
lines = []
for agent, file in sorted(manifest.items()):
    s = json.loads((STATE / file).read_text())
    lines.append(
        f"- {agent}: done {s['done']}; found {s['findings']}; next: {s['next']}"
    )
print(
    "Resume the investigation. Saved state from before the restart:\n"
    + "\n".join(lines)
)
