# 4_1_fp_report.py — Python 3.13+, offline. Which review categories destroy trust? Measure, then act.
from collections import Counter

# one row per comment the review bot posted last month: (category, what the developer did)
log = (
    [("sql-injection", "fixed")] * 9
    + [("sql-injection", "dismissed")] * 1
    + [("null-deref", "fixed")] * 14
    + [("null-deref", "dismissed")] * 4
    + [("naming-style", "fixed")] * 3
    + [("naming-style", "dismissed")] * 27
    + [("comment-accuracy", "fixed")] * 2
    + [("comment-accuracy", "dismissed")] * 18
)

posted = Counter(cat for cat, _ in log)
fixed = Counter(cat for cat, action in log if action == "fixed")
for cat in posted:
    precision = fixed[cat] / posted[cat]
    action = "keep" if precision >= 0.6 else "PAUSE category, rewrite its criteria"
    print(f"{cat:17} posted={posted[cat]:3}  precision={precision:4.0%}  → {action}")
print(
    f"overall precision {sum(fixed.values()) / len(log):.0%}: most comments are noise, so developers ignore all of them"
)
