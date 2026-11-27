# 5_5_calibrate.py — Python 3.13+, offline. Accuracy by segment, threshold calibration, stratified audit sample.
import random
from collections import defaultdict

random.seed(7)
rows = []  # labeled validation set: model confidence vs. the human-checked truth
for doc_type, n, p_ok in (("typed", 900, 0.99), ("handwritten", 100, 0.75)):
    for _ in range(n):
        ok = random.random() < p_ok
        conf = min(1.0, max(0.0, random.gauss(0.93 if ok else 0.72, 0.07)))
        rows.append({"doc_type": doc_type, "conf": conf, "ok": ok})

acc = lambda rs: sum(r["ok"] for r in rs) / len(rs)
by_type = defaultdict(list)
for r in rows:
    by_type[r["doc_type"]].append(r)
print(
    f"overall: {acc(rows):.1%}  |  "
    + "  ".join(f"{t}: {acc(rs):.1%} (n={len(rs)})" for t, rs in by_type.items())
)

for (
    t,
    rs,
) in (
    by_type.items()
):  # per segment: lowest threshold whose auto-accepted rows are >= 98% right
    best = next(
        (
            th / 100
            for th in range(50, 100)
            if (a := [r for r in rs if r["conf"] >= th / 100]) and acc(a) >= 0.98
        ),
        None,
    )
    auto = [r for r in rs if best is not None and r["conf"] >= best]
    print(
        f"{t:12} threshold={best}  auto-accept {len(auto)}/{len(rs)}  → {len(rs) - len(auto)} to human review"
    )

audit = {
    t: random.sample([r for r in rs if r["conf"] >= 0.9], 5)
    for t, rs in by_type.items()
}
print(
    "weekly audit sample (stratified, 5 per type):",
    {t: len(s) for t, s in audit.items()},
)
