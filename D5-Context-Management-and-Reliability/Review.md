# D5 Review

## Goal
After this you can answer mixed Domain 5 scenario questions in about 2 minutes each, and build a coordinator that reports coverage and keeps sources honest.

## Guess first
Warm-up, from memory, before you read anything below:
1. Write one line for each lesson 5.1 → 5.6. Which one feels weakest?
2. Official sample question 3: why is "explicit escalation criteria with few-shot examples" right, and "self-reported confidence score" wrong?

## Idea
The whole level on one screen:
1. **Keep facts exact** — case-facts block outside the summary, trim tool outputs early, key summary first and task last (lost in the middle). *(5.1)*
2. **Escalate on the right signals** — explicit request (at once), policy gap, no progress. Not sentiment, not self-confidence. Multiple matches → ask. Explicit criteria + examples. *(5.2)*
3. **Errors travel with context** — failure type, what was tried, partial results, alternatives. Never silent "empty = success", never kill-all. Access failure ≠ empty result. Report coverage gaps. *(5.3)*
4. **Long explorations** — subagents for noisy digging, scratchpad files, phase summaries, manifest for crash recovery, `/compact`. *(5.4)*
5. **Trust, but measure** — accuracy per document type and field, calibrated thresholds, stratified audits; sources and dates kept through synthesis, conflicts annotated. *(5.5, 5.6)*

## Code
Mini-project starter: three research subagents, already "run" (stubs). Python 3.13+, offline. Save as `research_report.py`.

```python
# research_report.py — part 1: subagent results (stubs). Python 3.13+, offline.
from collections import defaultdict

def search(subtopic: str) -> dict:
    return {
        "visual art": {"status": "ok", "claims": [
            {"metric": "illustrators using AI weekly", "value": "62%", "source": "Survey A", "date": "2026-03"},
            {"metric": "illustrators using AI weekly", "value": "41%", "source": "Poll B", "date": "2024-05"}]},
        "music": {"status": "partial", "failure_type": "timeout", "attempted": "'royalties 2025-2026', 2 retries",
                  "claims": [
            {"metric": "stock-music royalty change", "value": "-9%", "source": "Music report p.14", "date": "2025-11"},
            {"metric": "stock-music royalty change", "value": "-4%", "source": "Label filing", "date": "2025-11"}]},
        "film": {"status": "ok", "claims": []},
    }[subtopic]
```

## When to use · gotchas
Fast mapping from question words to the D5 answer:

| The question says… | Think… |
|---|---|
| amounts / dates drift in long chats | Case-facts block outside the summary |
| huge tool outputs, context fills | Trim to relevant fields before they enter history |
| middle findings ignored | Key summary first, headers, task last |
| "customer asked for a human" | Escalate at once |
| angry but simple | Acknowledge + resolve; escalate if they repeat the request |
| policy silent / unclear | Escalate (policy gap) |
| several matching records | Ask for another identifier |
| subagent failed | Structured error context; local retry first |
| "empty result marked success" / "terminate workflow" | Anti-patterns |
| answers go vague in long exploration | Subagents + scratchpad + compact |
| crash mid-investigation | State exports + manifest |
| "97% accurate overall" | Segment by type and field; calibrate; stratified sampling |
| sources disagree | Show both with attribution and dates |

## Try it
*≤ 30 min, offline.* Write **part 2** of `research_report.py` — the coordinator:
1. Call `search()` for the three subtopics. Keep partial results. *(5.3)*
2. Build a coverage note per subtopic: covered / PARTIAL (with failure type and what was tried) / GAP (searched fine, nothing found). *(5.3)*
3. Group claims by metric and label each: single source / agreed / changed over time / CONTESTED — always printing value, source and date. *(5.6)*
4. Print a "Findings" section first and a "Coverage" section after it. *(5.1 — summary up front, explicit headers)*

<details><summary>Solution</summary>

```python
# research_report.py — part 2: coordinator — coverage, provenance, conflict labels
claims, coverage = [], {}
for sub in ("visual art", "music", "film"):
    r = search(sub)
    claims += r["claims"]                                     # partial results are kept
    if r["status"] == "partial":
        coverage[sub] = f"PARTIAL: {r['failure_type']} after {r['attempted']}"
    else:
        coverage[sub] = "covered" if r["claims"] else "GAP: searched, no sources found"

by_metric = defaultdict(list)
for c in claims:
    by_metric[c["metric"]].append(c)

print("## Findings")
for metric, cs in by_metric.items():
    values, dates = {c["value"] for c in cs}, {c["date"] for c in cs}
    label = ("single source" if len(cs) == 1 else "agreed" if len(values) == 1
             else "changed over time" if len(dates) > 1 else "CONTESTED")
    print(f"- {metric} [{label}]: " + "; ".join(f"{c['value']} ({c['source']}, {c['date']})" for c in cs))
print("## Coverage")
for sub, note in coverage.items():
    print(f"- {sub}: {note}")
```
Expected output:
```
## Findings
- illustrators using AI weekly [changed over time]: 62% (Survey A, 2026-03); 41% (Poll B, 2024-05)
- stock-music royalty change [CONTESTED]: -9% (Music report p.14, 2025-11); -4% (Label filing, 2025-11)
## Coverage
- visual art: covered
- music: PARTIAL: timeout after 'royalties 2025-2026', 2 retries
- film: GAP: searched, no sources found
```
**Stretch (API):** send this printed text to Claude with "Write a 150-word brief. Keep every value with its source and date. Show conflicts, don't resolve them. End with the coverage gaps." Check that no source got lost.

</details>

## Quiz
Exam style: about 2 minutes each. Then redo official sample questions 3 and 8 (exam guide p.29, exam guide p.32).

**1.** After 30 turns, the agent promises "a refund soon" although the customer was told "$129.40 by Friday". Fix? A) Summarise more often · B) Persistent case-facts block with exact amounts and dates in every prompt · C) Larger context window · D) Ask the customer to repeat details

<details><summary>Answer</summary>

**B.** Exact transactional facts must live outside the lossy summary.

</details>

**2.** A frustrated customer has a standard, in-policy damage case. They haven't asked for a human. What does the agent do?

<details><summary>Answer</summary>

Acknowledge the frustration and offer the resolution; escalate only if the customer then repeats that they want a person.

</details>

**3.** **Choose 2.** Which are anti-patterns for a failed subagent? A) Returning empty results marked as success · B) Returning failure type, attempted query and partial results · C) Ending the whole workflow on one subagent timeout · D) Retrying a transient error locally first

<details><summary>Answer</summary>

**A and C.** Silent suppression and kill-all. B and D are the recommended patterns.

</details>

**4.** During a long codebase investigation, answers start citing "typical patterns" instead of the specific classes found earlier. Best response?

<details><summary>Answer</summary>

Context degradation: move key findings into a scratchpad file the agent reads, delegate further digging to subagents, and `/compact` (or start fresh with a summary).

</details>

**5.** Extraction is 97% accurate overall; the team wants to auto-accept all high-confidence output. What is the risk and the step?

<details><summary>Answer</summary>

The average can hide weak segments (e.g. handwritten docs, date fields). Measure accuracy per document type and field, calibrate thresholds on labeled data, and keep stratified sampling.

</details>

**6.** Two credible sources: "AI adoption 62%" (2026) and "41%" (2024). How should the report show this?

<details><summary>Answer</summary>

As a change over time, with both values, sources and dates — not as a contradiction, and not by picking one.

</details>

**7.** A customer lookup by name returns 2 accounts. What does the agent do?

<details><summary>Answer</summary>

Ask for an additional identifier (email, order number). Never pick by heuristic.

</details>

**8.** A downstream synthesis agent keeps running out of context because upstream agents send their full reasoning. Fix?

<details><summary>Answer</summary>

Make upstream agents return structured data — key facts, citations, relevance scores, dates — instead of verbose content and reasoning chains.

</details>

**9.** *(D1)* A session is resumed after many files changed; the agent cites deleted functions. Best move?

<details><summary>Answer</summary>

Start a new session with a structured summary of the still-valid findings plus the list of changed files — stale tool results mislead.

</details>

**10.** *(D2)* A research subagent's search tool times out and the tool returns `[]` with `isError: false`. Which lesson ideas does that break?

<details><summary>Answer</summary>

Structured tool errors (2.2) and error propagation (5.3): an access failure was reported as a valid empty result, so the coordinator records a false gap.

</details>

## References
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
