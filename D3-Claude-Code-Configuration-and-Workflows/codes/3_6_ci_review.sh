#!/usr/bin/env bash
# ci_review.sh — Claude Code 2.1.x in CI. Needs ANTHROPIC_API_KEY. Run after checkout of the PR branch.
set -euo pipefail
SCHEMA='{"type":"object","required":["findings"],"properties":{"findings":{"type":"array","items":{
 "type":"object","required":["file","line","severity","issue","fix"],"properties":{"file":{"type":"string"},
 "line":{"type":"integer"},"severity":{"enum":["high","medium","low"]},"issue":{"type":"string"},
 "fix":{"type":"string"}}}}}}'
mkdir -p .review
PRIOR=$(cat .review/prior-findings.json 2>/dev/null || echo '{"findings":[]}')

git diff origin/main...HEAD | claude -p "Review the PR diff on stdin with the review criteria in CLAUDE.md.
Report only NEW or still-unfixed issues. Already reported earlier: $PRIOR" \
  --output-format json --json-schema "$SCHEMA" --allowedTools "Read,Grep,Glob" \
  | jq '.structured_output // {"findings": []}' > .review/findings.json

jq -r '.findings[] | "::warning file=\(.file),line=\(.line)::[\(.severity)] \(.issue) Fix: \(.fix)"' .review/findings.json
cp .review/findings.json .review/prior-findings.json   # next run skips these
