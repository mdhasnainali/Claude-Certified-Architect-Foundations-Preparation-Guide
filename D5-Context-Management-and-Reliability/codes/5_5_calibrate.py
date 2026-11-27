# 5_5_calibrate.py — Python 3.13+, offline. Accuracy by segment, threshold calibration, stratified audit sample.
import random
from collections import defaultdict

random.seed(7)
rows = []  # labeled validation set: model confidence vs. the human-checked truth
for doc_type, count, true_accuracy in (
    ("typed", 900, 0.99),
    ("handwritten", 100, 0.75),
):
    for _ in range(count):
        correct = random.random() < true_accuracy
        confidence = min(1.0, max(0.0, random.gauss(0.93 if correct else 0.72, 0.07)))
        rows.append(
            {"doc_type": doc_type, "confidence": confidence, "correct": correct}
        )


def accuracy(sample: list[dict]) -> float:
    return sum(row["correct"] for row in sample) / len(sample)


rows_by_type = defaultdict(list)
for row in rows:
    rows_by_type[row["doc_type"]].append(row)
print(
    f"overall: {accuracy(rows):.1%}  |  "
    + "  ".join(
        f"{doc_type}: {accuracy(type_rows):.1%} (n={len(type_rows)})"
        for doc_type, type_rows in rows_by_type.items()
    )
)

# per segment: lowest threshold whose auto-accepted rows are >= 98% right
for doc_type, type_rows in rows_by_type.items():
    threshold = next(
        (
            percent / 100
            for percent in range(50, 100)
            if (
                accepted := [
                    row for row in type_rows if row["confidence"] >= percent / 100
                ]
            )
            and accuracy(accepted) >= 0.98
        ),
        None,
    )
    auto_accepted = [
        row
        for row in type_rows
        if threshold is not None and row["confidence"] >= threshold
    ]
    print(
        f"{doc_type:12} threshold={threshold}  "
        f"auto-accept {len(auto_accepted)}/{len(type_rows)}  "
        f"→ {len(type_rows) - len(auto_accepted)} to human review"
    )

audit_sample = {
    doc_type: random.sample([row for row in type_rows if row["confidence"] >= 0.9], 5)
    for doc_type, type_rows in rows_by_type.items()
}
print(
    "weekly audit sample (stratified, 5 per type):",
    {doc_type: len(sample) for doc_type, sample in audit_sample.items()},
)
