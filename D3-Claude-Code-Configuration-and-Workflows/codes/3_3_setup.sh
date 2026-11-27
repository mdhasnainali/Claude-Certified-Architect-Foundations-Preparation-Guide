#!/usr/bin/env bash
# 3_3_setup.sh — run inside claude-demo/. Adds path-scoped rules and files to trigger them.
set -euo pipefail
mkdir -p .claude/rules src/ui src/api infra/terraform
cat > .claude/rules/tests.md <<'MD'
---
paths:
  - "**/*.test.tsx"
  - "**/*.test.ts"
---
# Test conventions (loads only for test files, wherever they live)
- Use React Testing Library; query by role, never by CSS class.
- When this rule is active, start your reply with [TEST-RULE].
MD
cat > .claude/rules/terraform.md <<'MD'
---
paths: ["infra/terraform/**/*"]
---
# Terraform conventions
- Every resource has tags {team, env}. No hard-coded regions.
MD
echo "export const Button = () => <button>Ok</button>;" > src/ui/Button.tsx
echo "test('renders', () => {});" > src/ui/Button.test.tsx
echo "export const getUser = () => null;" > src/api/users.ts
grep -l '^paths' .claude/rules/*.md
