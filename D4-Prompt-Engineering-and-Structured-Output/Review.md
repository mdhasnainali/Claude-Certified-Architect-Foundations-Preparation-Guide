# D4 Review

## Goal
After this you can answer mixed Domain 4 scenario questions in about 2 minutes each, and build an extraction loop that validates, retries with feedback, and routes what retries can't fix.

## Guess first
Warm-up, from memory, before you read anything below:
1. Write one line for each lesson 4.1 → 4.6. Which one feels weakest?
2. Official sample question 11: why batch the overnight report but not the pre-merge check?

## Idea
The whole level on one screen:
1. **Explicit criteria** beat "be conservative": say what to report and what to skip; anchor severity with examples; pause noisy categories to rebuild trust. *(4.1)*
2. **Few-shot** (2–4 targeted examples, with reasons) fixes inconsistent format and teaches judgment on ambiguous cases; show absent data as null. *(4.2)*
3. **Tool use + strict JSON schema** guarantees shape, not truth. `any` = some tool, forced = that tool. Nullable fields stop invented values; `other` + detail, `unclear`. *(4.3)*
4. **Validate in code, retry with feedback** (document + failed output + exact errors). Retries fix format, not missing data. `calculated_total` vs `stated_total`; `detected_pattern`. *(4.4)*
5. **Batches** = 50% cheaper, ≤ 24 h, no SLA, `custom_id`, resubmit failures only — for non-blocking work. **Independent reviewer** > self-review; per-file + integration passes; confidence for routing. *(4.5, 4.6)*

## Code
Mini-project starter. Python 3.13+, `pydantic` 2, offline. At the top of `pipeline.py`, paste **part 1 of `4_4_validate_retry.py`** (the `Invoice` model) and your **`should_retry`** from [4.4 Validation and Retry Loops](4.4-Validation-and-Retry-Loops.md). Then add:

```python
# pipeline.py — part 1: documents and a fake extractor (stands in for messages.parse). Offline.
DOCS = {
    "inv-1": "Invoice 3 Nov 2026. Hosting $120.00. Support $80.00. TOTAL: $200.00",
    "inv-2": "Invoice 5 Nov 2026. Licences $1,440.00. TOTAL: $1,500.00",
    "inv-3": "Invoice 9 Nov 2026. Training $300.00. TOTAL: see attached statement",
}

def fake_extract(doc_id: str, feedback: str | None = None) -> dict:
    """First try makes a format mistake on inv-1; the retry (with feedback) fixes it."""
    base = {"inv-1": {"invoice_date": "3 Nov 2026", "stated_total": 200,
                      "items": [{"desc": "Hosting", "amount": 120}, {"desc": "Support", "amount": 80}]},
            "inv-2": {"invoice_date": "2026-11-05", "stated_total": 1500,
                      "items": [{"desc": "Licences", "amount": 1440}]},
            "inv-3": {"invoice_date": "2026-11-09", "items": [{"desc": "Training", "amount": 300}]}}[doc_id]
    if doc_id == "inv-1" and feedback:
        base = {**base, "invoice_date": "2026-11-03"}
    return base
```

## When to use · gotchas
Fast mapping from question words to the D4 answer:

| The question says… | Think… |
|---|---|
| too many false positives; "be conservative" didn't help | Explicit report/skip criteria with examples |
| developers ignore all bot comments | Pause high-FP categories, fix their criteria |
| inconsistent format despite detailed rules | 2–4 few-shot examples of the exact format |
| extraction invents missing values | Nullable fields + an example with null |
| JSON parse errors | Tool use / structured output with a strict schema |
| must get structured output, unknown doc type | `tool_choice: any` |
| X must run before enrichment | Forced tool choice for X, then `auto` |
| valid JSON but totals don't add up | Semantic validation in code + retry with feedback |
| info only in a document you don't have | Retry won't help → null + human review |
| cheaper, overnight / weekly work | Message Batches API |
| blocking pre-merge check | Synchronous API |
| results order, failed items | `custom_id`; resubmit failures only (chunk oversized docs) |
| self-review misses bugs | Independent reviewer instance |
| big PR, uneven review | Per-file passes + integration pass |

## Try it
*≤ 30 min, offline.* Write **part 2** of `pipeline.py`: for each document, extract → validate with `Invoice` → on a validation error, retry **once** with feedback if `should_retry` says so → route to human review when the retry can't help or the source totals conflict → print one outcome line per document.

<details><summary>Solution</summary>

```python
# pipeline.py — part 2: validate → retry with feedback → route
results = {}
for doc_id, doc in DOCS.items():
    feedback = None
    for attempt in (1, 2):                                   # at most one retry
        data = fake_extract(doc_id, feedback)
        try:
            inv = Invoice(**data)
        except ValidationError as e:
            errors = [f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in e.errors()]
            if not should_retry(errors, doc) or attempt == 2:
                results[doc_id] = f"HUMAN REVIEW: {errors}"    # missing data or repeated error
                break
            feedback = "Fix these errors: " + "; ".join(errors)  # sent with the doc + failed extraction
            continue
        results[doc_id] = ("HUMAN REVIEW: source totals disagree "
                           f"(items {inv.calculated_total} vs stated {inv.stated_total})"
                           if inv.conflict_detected else f"OK after {attempt} attempt(s)")
        break
for doc_id, outcome in results.items():
    print(doc_id, "→", outcome)
```
Expected output:
```
inv-1 → OK after 2 attempt(s)
inv-2 → HUMAN REVIEW: source totals disagree (items 1440.0 vs stated 1500.0)
inv-3 → HUMAN REVIEW: ['stated_total: Field required']
```
**Stretch (API):** replace `fake_extract` with `client.messages.parse(..., output_format=...)` and put the document, the failed extraction and `feedback` into the retry message.

</details>

## Quiz
Exam style: about 2 minutes each. Then redo official sample questions 11 and 12 (exam guide p.34, exam guide p.35).

**1.** A CI review bot posts many false positives. The team adds "only report high-confidence findings". Nothing improves. Next step? A) Lower the threshold further · B) Write explicit criteria: report bugs/security, skip style and repo-wide patterns, with severity examples · C) Use a larger model · D) Run the review twice

<details><summary>Answer</summary>

**B.** Confidence-based filtering is vague; explicit categorical criteria change behaviour.

</details>

**2.** Detailed formatting instructions still give inconsistent finding formats. Most effective fix?

<details><summary>Answer</summary>

Add 2–4 few-shot examples that show the exact output format (location, issue, severity, suggested fix).

</details>

**3.** **Choose 2.** Which problems does a strict JSON schema via tool use remove? A) JSON syntax errors · B) Line items not summing to the total · C) Missing required keys · D) Values put in the wrong field

<details><summary>Answer</summary>

**A and C.** B and D are semantic errors — validate them in code.

</details>

**4.** Unknown document types, three extraction tools, sometimes prose instead of a tool call. Which `tool_choice`?

<details><summary>Answer</summary>

`{"type": "any"}` (on models that support it).

</details>

**5.** A retry loop keeps failing for invoices whose payment terms are "see contract". Why, and what instead?

<details><summary>Answer</summary>

The information isn't in the document, so retries can't produce it. Use a nullable field, accept null, and route to review or fetch the contract.

</details>

**6.** Nightly test generation for 2,000 files and a 10-minute pre-merge check. Which APIs?

<details><summary>Answer</summary>

Batches for the nightly job (non-blocking, 50% cheaper); synchronous API for the pre-merge check.

</details>

**7.** Batch results seem "shuffled" relative to the input list. Problem?

<details><summary>Answer</summary>

No — order isn't guaranteed. Match results by `custom_id`.

</details>

**8.** A generated migration script is reviewed by the same session that wrote it; edge cases slip through. Fix?

<details><summary>Answer</summary>

Review with an independent instance that sees only the script and the criteria, not the generator's reasoning.

</details>

**9.** *(D5)* Extraction accuracy is 97% overall. Before cutting human review, what do you check?

<details><summary>Answer</summary>

Accuracy by document type and field, with calibrated confidence thresholds and stratified sampling.

</details>

**10.** *(D1)* A 14-file PR review in one pass contradicts itself. Fix?

<details><summary>Answer</summary>

Per-file passes for local issues plus a separate cross-file integration pass (attention dilution).

</details>

## References
- [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
