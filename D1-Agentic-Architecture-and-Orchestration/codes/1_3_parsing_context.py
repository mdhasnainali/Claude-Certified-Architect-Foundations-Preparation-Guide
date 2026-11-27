# 1_3_parsing_context.py — Python 3.13+, no API key needed: python3 1_3_parsing_context.py
import json

subagent_findings = [  # what the search and document subagents returned
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


def build_synthesis_prompt(section: str, findings: list[dict]) -> str:
    numbered = [
        {"id": number, **finding} for number, finding in enumerate(findings, start=1)
    ]
    return (
        f"Write the section '{section}'.\n"
        "Use ONLY the findings below. Cite each claim as [id]. Keep dates.\n"
        "If findings disagree, show both with their sources; do not pick one.\n"
        "<findings>\n"
        + "\n".join(json.dumps(finding) for finding in numbered)
        + "\n</findings>"
    )


print(build_synthesis_prompt("Creative jobs", subagent_findings))


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
