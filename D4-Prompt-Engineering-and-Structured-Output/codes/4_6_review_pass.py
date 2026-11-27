# 4_6_review_pass.py — anthropic 2.13. Run: uv run --with anthropic python 4_6_review_pass.py
from typing import Literal
import anthropic
from pydantic import BaseModel

client = anthropic.Anthropic()


class Finding(BaseModel):
    line: int
    issue: str
    severity: Literal["high", "medium", "low"]
    confidence: (
        float  # self-reported: use it for routing only after calibration (lesson 5.5)
    )


class Review(BaseModel):
    findings: list[Finding]


gen = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=4000,
    messages=[
        {
            "role": "user",
            "content": "Write a Python function parse_price(s) that turns '$1,299.50' into 1299.5. Code only.",
        }
    ],
)
code = next(b.text for b in gen.content if b.type == "text")

# Independent reviewer: a NEW request with only the code and the criteria, none of the generator's reasoning
review = client.messages.parse(
    model="claude-haiku-5-5",
    max_tokens=4000,
    output_format=Review,
    messages=[
        {
            "role": "user",
            "content": "Review this code. Report only real bugs: wrong results or crashes on "
            "plausible inputs (negative, empty, no '$', other currencies). Skip style.\n<code>\n"
            + code
            + "\n</code>",
        }
    ],
)
for f in review.parsed_output.findings:
    route = (
        "post as PR comment"
        if f.severity == "high" and f.confidence >= 0.8
        else "human triage queue"
    )
    print(f"line {f.line} [{f.severity}, {f.confidence:.2f}] {f.issue} → {route}")
