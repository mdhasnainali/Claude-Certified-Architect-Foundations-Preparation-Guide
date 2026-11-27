# 4_1_fp_report.py — Python 3.13+, offline. Which review categories destroy trust? Measure, then act.
from collections import Counter

# one row per comment the review bot posted last month: (category, what the developer did)
review_log = (
    [("sql-injection", "fixed")] * 9
    + [("sql-injection", "dismissed")] * 1
    + [("null-deref", "fixed")] * 14
    + [("null-deref", "dismissed")] * 4
    + [("naming-style", "fixed")] * 3
    + [("naming-style", "dismissed")] * 27
    + [("comment-accuracy", "fixed")] * 2
    + [("comment-accuracy", "dismissed")] * 18
)

posted_count = Counter(category for category, _ in review_log)
fixed_count = Counter(
    category for category, developer_action in review_log if developer_action == "fixed"
)
for category in posted_count:
    precision = fixed_count[category] / posted_count[category]
    recommendation = (
        "keep" if precision >= 0.6 else "PAUSE category, rewrite its criteria"
    )
    print(
        f"{category:17} posted={posted_count[category]:3}  "
        f"precision={precision:4.0%}  → {recommendation}"
    )
print(
    f"overall precision {sum(fixed_count.values()) / len(review_log):.0%}: most comments are noise, so developers ignore all of them"
)
