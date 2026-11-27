# 5_3_propagate.py — Python 3.13+, offline. Subagents report failures as data; the coordinator decides.
import json


def search_subagent(subtopic: str) -> dict:
    if subtopic == "music":  # timed out twice, kept what it had
        return {
            "status": "partial",
            "failure_type": "timeout",
            "attempted": "'AI music royalties 2025-2026', 2 retries",
            "partial_results": [
                {
                    "claim": "AI-made tracks on streaming tripled",
                    "source": "https://example.org/a",
                }
            ],
            "alternatives": ["search trade-press archive", "narrow to 2026"],
        }
    if subtopic == "film":  # search worked, nothing relevant exists
        return {"status": "ok", "results": []}
    return {
        "status": "ok",
        "results": [
            {
                "claim": f"AI tools are common in {subtopic}",
                "source": "https://example.org/b",
            }
        ],
    }


findings, coverage = [], {}
for subtopic in ("visual art", "music", "film"):
    report = search_subagent(subtopic)
    if report["status"] == "partial":  # failure WITH context → recover, don't crash
        findings += report["partial_results"]
        coverage[subtopic] = (
            f"PARTIAL ({report['failure_type']}; tried {report['attempted']}). "
            f"Next: {report['alternatives'][0]}"
        )
    elif not report["results"]:  # valid empty result → a real gap, not an error
        coverage[subtopic] = "GAP: searched successfully, no sources found"
    else:
        findings += report["results"]
        coverage[subtopic] = "covered"

print(json.dumps(coverage, indent=1))
print(len(findings), "findings kept for synthesis")
