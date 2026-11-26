# handoff.py — Python 3.12+, no API key needed: python3 handoff.py
import json

findings = [  # what the search and document subagents returned
    {
        "claim": "62% of illustrators use AI tools weekly",
        "source": "https://example.org/survey-2026",
        "date": "2026-03",
        "from": "web-search",
    },
    {
        "claim": "Stock-music royalty income fell 9%",
        "source": "music-report.pdf, p.14",
        "date": "2025-11",
        "from": "doc-analysis",
    },
]


def synthesis_prompt(section: str, findings: list[dict]) -> str:
    items = [{"id": i, **f} for i, f in enumerate(findings, start=1)]
    return (
        f"Write the section '{section}'.\n"
        "Use ONLY the findings below. Cite each claim as [id]. Keep dates.\n"
        "If findings disagree, show both with their sources; do not pick one.\n"
        "<findings>\n" + "\n".join(json.dumps(x) for x in items) + "\n</findings>"
    )


print(synthesis_prompt("Creative jobs", findings))


# ---------------------------------------------------------------------------
# Sample output: make run 1_3
# ---------------------------------------------------------------------------
# Write the section 'Creative jobs'.
# Use ONLY the findings below. Cite each claim as [id]. Keep dates.
# If findings disagree, show both with their sources; do not pick one.
# <findings>
# {"id": 1, "claim": "62% of illustrators use AI tools weekly", "source": "https://example.org/survey-2026", "date": "2026-03", "from": "web-search"}
# {"id": 2, "claim": "Stock-music royalty income fell 9%", "source": "music-report.pdf, p.14", "date": "2025-11", "from": "doc-analysis"}
# </findings>
