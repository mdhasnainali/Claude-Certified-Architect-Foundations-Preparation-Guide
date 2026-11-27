# 4_4_validate_retry.py — part 1: schema + semantic checks. pydantic 2, offline.
import json
from pydantic import BaseModel, ValidationError, field_validator, model_validator


class Item(BaseModel):
    desc: str
    amount: float


class Invoice(BaseModel):
    invoice_date: str
    items: list[Item]
    stated_total: float
    calculated_total: float | None = (
        None  # computed here, compared with what the document states
    )
    conflict_detected: bool = False

    @field_validator("invoice_date")
    @classmethod
    def iso_date(cls, v: str) -> str:
        if len(v) != 10 or v[4] != "-" or v[7] != "-":
            raise ValueError("must be YYYY-MM-DD")
        return v

    @model_validator(mode="after")
    def check_totals(self):
        self.calculated_total = round(sum(i.amount for i in self.items), 2)
        self.conflict_detected = abs(self.calculated_total - self.stated_total) > 0.01
        return self


# 4_4_validate_retry.py — part 2: build the retry prompt, then check the fixed extraction
DOC = "Invoice, 3 Nov 2026. Hosting $120.00. Support $80.00. TOTAL DUE: $210.00"
first_try = {
    "invoice_date": "3 Nov 2026",
    "stated_total": 210,
    "items": [{"desc": "Hosting", "amount": 120}, {"desc": "Support", "amount": 80}],
}
try:
    Invoice(**first_try)
except ValidationError as e:
    errors = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()]
    print(
        f"<document>\n{DOC}\n</document>\n<previous_extraction>\n{json.dumps(first_try)}\n"
        "</previous_extraction>\nFix ONLY these errors and return the full extraction:\n- "
        + "\n- ".join(errors)
    )

second_try = {**first_try, "invoice_date": "2026-11-03"}  # what the retry returns
inv = Invoice(**second_try)
print(
    f"\nvalid. calculated_total={inv.calculated_total} stated_total={inv.stated_total} "
    f"conflict_detected={inv.conflict_detected}"
)
