# 4_6_review_pass.py — anthropic 2.13. Run: uv run --with anthropic python 4_6_review_pass.py
from typing import Literal
import anthropic
from pydantic import BaseModel

client = anthropic.Anthropic()


class Finding(BaseModel):
    line: int
    issue: str
    severity: Literal["high", "medium", "low"]
    # self-reported: use it for routing only after calibration (lesson 5.5)
    confidence: float


class Review(BaseModel):
    findings: list[Finding]


generation = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=4000,
    messages=[
        {
            "role": "user",
            "content": "Write a Python function parse_price(s) that turns '$1,299.50' into 1299.5. Code only.",
        }
    ],
)
generated_code = next(
    block.text for block in generation.content if block.type == "text"
)

# Independent reviewer: a NEW request with only the code and the criteria, none of the generator's reasoning
review_response = client.messages.parse(
    model="claude-haiku-5-5",
    max_tokens=4000,
    output_format=Review,
    messages=[
        {
            "role": "user",
            "content": "Review this code. Report only real bugs: wrong results or crashes on "
            "plausible inputs (negative, empty, no '$', other currencies). Skip style.\n<code>\n"
            + generated_code
            + "\n</code>",
        }
    ],
)
for finding in review_response.parsed_output.findings:
    route = (
        "post as PR comment"
        if finding.severity == "high" and finding.confidence >= 0.8
        else "human triage queue"
    )
    print(
        f"line {finding.line} [{finding.severity}, {finding.confidence:.2f}] "
        f"{finding.issue} → {route}"
    )
