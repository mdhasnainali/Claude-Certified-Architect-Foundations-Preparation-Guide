# 5_6_provenance.py — Python 3.13+, offline. Merge findings without losing sources; label agreement and conflict.
from collections import defaultdict

findings = [  # claim-source mappings returned by two subagents
    {
        "metric": "illustrators using AI weekly",
        "value": "62%",
        "source": "Survey A (example.org)",
        "date": "2026-03",
    },
    {
        "metric": "illustrators using AI weekly",
        "value": "41%",
        "source": "Poll B (example.net)",
        "date": "2024-05",
    },
    {
        "metric": "stock-music royalty change",
        "value": "-9%",
        "source": "Music report p.14",
        "date": "2025-11",
    },
    {
        "metric": "stock-music royalty change",
        "value": "-4%",
        "source": "Label filing",
        "date": "2025-11",
    },
    {
        "metric": "VFX artists using AI",
        "value": "1 in 3",
        "source": "Guild study",
        "date": "2026-01",
    },
    {
        "metric": "VFX artists using AI",
        "value": "1 in 3",
        "source": "Studio survey",
        "date": "2026-02",
    },
    {
        "metric": "novelists drafting with AI",
        "value": "18%",
        "source": "Author blog",
        "date": "2026-05",
    },
]
by_metric = defaultdict(list)
for f in findings:
    by_metric[f["metric"]].append(f)

sections = {
    "Well-established": [],
    "Single source": [],
    "Changed over time": [],
    "Contested": [],
}
for metric, fs in by_metric.items():
    cites = "; ".join(f"{f['value']} ({f['source']}, {f['date']})" for f in fs)
    if len(fs) == 1:
        sections["Single source"].append(f"{metric}: {cites}")
    elif len({f["value"] for f in fs}) == 1:  # 2+ sources agree
        sections["Well-established"].append(f"{metric}: {cites}")
    elif (
        len({f["date"] for f in fs}) > 1
    ):  # different dates → a trend, not a contradiction
        sections["Changed over time"].append(f"{metric}: {cites}")
    else:  # same period, different values → keep both
        sections["Contested"].append(f"{metric}: sources disagree: {cites}")

for title, items in sections.items():
    print(f"## {title}\n" + "\n".join(f"- {i}" for i in items))
