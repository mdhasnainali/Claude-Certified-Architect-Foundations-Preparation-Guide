#!/usr/bin/env bash
# 3_2_setup.sh — run inside claude-demo/ (from lesson 3.1). Adds one command and one skill.
set -euo pipefail
mkdir -p .claude/commands .claude/skills/codebase-map
cat > .claude/commands/review.md <<'MD'
---
description: Run the team review checklist on the current branch
argument-hint: [base-branch]
---
Review `git diff $ARGUMENTS...HEAD` (use main if no branch was given) against our checklist:
bugs, missing tests, security. Skip style. Output: file:line · issue · severity · fix.
MD
cat > .claude/skills/codebase-map/SKILL.md <<'MD'
---
name: codebase-map
description: Map an unfamiliar codebase (modules, entry points, where tests live) and return a short summary. Use before large changes.
argument-hint: [folder]
context: fork
agent: Explore
allowed-tools: Read Grep Glob
disallowed-tools: Edit Write
---
Map the code under $ARGUMENTS (the whole repo if empty):
1. Top-level modules, one line each.  2. Entry points.  3. Where tests live.
Return at most 15 lines. Do not change any file.
MD
find .claude -type f | sort
