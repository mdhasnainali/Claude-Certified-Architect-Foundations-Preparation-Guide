# 4_4_validate_retry.py — part 1: schema + semantic checks. pydantic 2, offline.
import json
from pydantic import BaseModel, ValidationError, field_validator, model_validator


class LineItem(BaseModel):
    description: str
    amount: float


class Invoice(BaseModel):
    invoice_date: str
    items: list[LineItem]
    stated_total: float
    # computed here, then compared with the total the document states
    calculated_total: float | None = None
    conflict_detected: bool = False

    @field_validator("invoice_date")
    @classmethod
    def check_iso_date(cls, value: str) -> str:
        if len(value) != 10 or value[4] != "-" or value[7] != "-":
            raise ValueError("must be YYYY-MM-DD")
        return value

    @model_validator(mode="after")
    def check_totals(self):
        self.calculated_total = round(sum(item.amount for item in self.items), 2)
        self.conflict_detected = abs(self.calculated_total - self.stated_total) > 0.01
        return self


# 4_4_validate_retry.py — part 2: build the retry prompt, then check the fixed extraction
DOCUMENT = "Invoice, 3 Nov 2026. Hosting $120.00. Support $80.00. TOTAL DUE: $210.00"
first_extraction = {
    "invoice_date": "3 Nov 2026",
    "stated_total": 210,
    "items": [
        {"description": "Hosting", "amount": 120},
        {"description": "Support", "amount": 80},
    ],
}
try:
    Invoice(**first_extraction)
except ValidationError as validation_error:
    error_lines = [
        f"{'.'.join(map(str, error['loc']))}: {error['msg']}"
        for error in validation_error.errors()
    ]
    print(
        f"<document>\n{DOCUMENT}\n</document>\n<previous_extraction>\n{json.dumps(first_extraction)}\n"
        "</previous_extraction>\nFix ONLY these errors and return the full extraction:\n- "
        + "\n- ".join(error_lines)
    )

retried_extraction = {
    **first_extraction,
    "invoice_date": "2026-11-03",
}  # what the retry returns
invoice = Invoice(**retried_extraction)
print(
    f"\nvalid. calculated_total={invoice.calculated_total} stated_total={invoice.stated_total} "
    f"conflict_detected={invoice.conflict_detected}"
)
