#!/usr/bin/env bash
# 3_1_setup.sh — builds a demo repo to see CLAUDE.md layers. Run: bash 3_1_setup.sh
set -euo pipefail
mkdir -p claude-demo/{.claude/rules,docs/standards,packages/api,packages/web} && cd claude-demo && git init -q
cat > CLAUDE.md <<'MD'
# Team instructions (project level — shared via git)
- Run tests with `make test`. Python 3.14, uv for packages.
- Never commit secrets.
MD
cat > packages/api/CLAUDE.md <<'MD'
# API package (directory level — loads when Claude works in packages/api/)
@../../docs/standards/api-conventions.md
MD
cat > docs/standards/api-conventions.md <<'MD'
- Every endpoint validates input with Pydantic and returns errors as {"error": {...}}.
MD
cat > .claude/rules/testing.md <<'MD'
# Testing (rule without paths: loads every session, like CLAUDE.md)
- Tests use pytest fixtures from tests/conftest.py. No network in unit tests.
MD
echo "- I like short answers." > CLAUDE.local.md && echo "CLAUDE.local.md" > .gitignore
find . -name '*.md' -not -path './.git/*' | sort
