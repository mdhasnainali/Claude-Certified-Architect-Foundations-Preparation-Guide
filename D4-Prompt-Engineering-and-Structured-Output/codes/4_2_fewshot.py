# 4_2_fewshot.py — anthropic 2.13. Run: uv run --with anthropic python 4_2_fewshot.py
import anthropic
from pydantic import BaseModel

client = anthropic.Anthropic()


class Qty(BaseModel):
    quantity: float | None  # None when the text gives no number — never invent one
    unit: str | None
    approximate: bool


EXAMPLES = """<examples>
<example>"a couple of eggs" → {"quantity": 2, "unit": "piece", "approximate": true}
Why: "a couple" means about 2; eggs are counted in pieces.</example>
<example>"salt to taste" → {"quantity": null, "unit": null, "approximate": true}
Why: no amount is stated; inventing "1 pinch" would be a hallucination.</example>
<example>"2-3 cups flour" → {"quantity": 2.5, "unit": "cup", "approximate": true}
Why: for a range, use the midpoint and mark it approximate.</example>
</examples>"""
LINES = [
    "a handful of walnuts",
    "pepper, as needed",
    "1/2 lb butter",
    "4-6 cloves garlic",
]

for shots in ("", EXAMPLES):
    print("FEW-SHOT" if shots else "ZERO-SHOT")
    for line in LINES:
        r = client.messages.parse(
            model="claude-haiku-5-5",
            max_tokens=2000,
            output_format=Qty,
            messages=[
                {
                    "role": "user",
                    "content": f"{shots}\nExtract the quantity from: {line!r}",
                }
            ],
        )
        print(f"  {line:22} → {r.parsed_output.model_dump()}")
