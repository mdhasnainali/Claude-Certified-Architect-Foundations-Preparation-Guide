# D3 Review

## Goal
After this you can answer mixed Domain 3 scenario questions in about 2 minutes each, and set up a team repository's Claude Code configuration from scratch.

## Guess first
Warm-up, from memory, before you read anything below:
1. Write one line for each lesson 3.1 → 3.6. Which one feels weakest?
2. Official sample question 6: why do glob rules beat one CLAUDE.md per subdirectory?

## Idea
The whole level on one screen:
1. **Where instructions live** — user `~/.claude/CLAUDE.md` (only you) · project `CLAUDE.md` / `.claude/rules/` (team, in git) · directory `CLAUDE.md` (on demand). Concatenated, not overridden. `@import` for modular standards; `/memory` to debug. *(3.1)*
2. **Commands & skills** — team ones in `.claude/commands/` and `.claude/skills/`, personal ones in `~/.claude/…` with different names. `context: fork` isolates noisy skills; `allowed-tools` limits tools (exam framing); `argument-hint` prompts for arguments. Skills = on demand; CLAUDE.md = always. *(3.2)*
3. **Path rules** — `.claude/rules/*.md` with `paths:` globs load only for matching files; beat directory CLAUDE.md for file types spread everywhere. *(3.3)*
4. **Plan vs direct** — plan mode for big, multi-approach, architectural work; direct for small, clear fixes; Explore subagent for noisy discovery. *(3.4)*
5. **Refine & automate** — I/O examples, tests first, interview pattern, interacting issues in one message. CI: `-p`, `--output-format json` + `--json-schema`, CLAUDE.md as CI context, separate reviewer, prior findings to avoid duplicates. *(3.5, 3.6)*

## Code
Mini-project starter: a **checker** for a team setup. Bash + `jq`, offline. Save as `check_setup.sh` next to your `ci_review.sh` from [3.6 Claude Code in CI](3.6-Claude-Code-in-CI.md).

```bash
#!/usr/bin/env bash
# check_setup.sh — run in the repo root. Checks a team Claude Code setup. Offline, needs jq.
pass=0; fail=0
check() { if eval "$2" >/dev/null 2>&1; then echo "PASS  $1"; pass=$((pass+1)); else echo "FAIL  $1"; fail=$((fail+1)); fi; }

check "project CLAUDE.md names the test command"      'grep -qi "test" CLAUDE.md'
check "CLAUDE.local.md is gitignored"                  'grep -qx "CLAUDE.local.md" .gitignore'
check "a rule is scoped to test files with paths:"     'grep -l "^paths" .claude/rules/*.md | xargs grep -l "test"'
check "a team command exists in .claude/commands/"     'ls .claude/commands/*.md'
check "a project skill runs with context: fork"        'grep -l "^context: fork" .claude/skills/*/SKILL.md'
check ".mcp.json is valid JSON"                        'jq empty .mcp.json'
check ".mcp.json reads secrets from \${ENV} vars"      'grep -q "\${" .mcp.json'
check ".mcp.json has no literal GitHub token"          '[ -f .mcp.json ] && ! grep -qE "gh[pousr]_[A-Za-z0-9]{20,}" .mcp.json'
check "CI runs Claude non-interactively (-p)"          'grep -q "claude -p" scripts/ci_review.sh'
check "CI asks for schema-shaped output"               'grep -q -- "--json-schema" scripts/ci_review.sh'
echo "$pass passed, $fail failed"; exit "$fail"
```
In a fresh, empty git repo it prints `0 passed, 10 failed`.

## When to use · gotchas
Fast mapping from question words to the D3 answer:

| The question says… | Think… |
|---|---|
| new teammate doesn't get the instructions | They're in user-level `~/.claude/CLAUDE.md` → move to project |
| each package needs only some standards | `@import` in each package's CLAUDE.md |
| one giant CLAUDE.md | Split into `.claude/rules/` topic files |
| inconsistent behaviour across sessions | `/memory` to see which files load |
| command for everyone after clone | `.claude/commands/` (or `.claude/skills/`) in the repo |
| skill floods the chat | `context: fork` |
| skill must not do destructive things | Limit its tools (`allowed-tools` on the exam) |
| devs forget the skill's argument | `argument-hint` |
| own variant of a team skill | `~/.claude/skills/` with a different name |
| conventions for test files everywhere | `.claude/rules/` with `paths: ["**/*.test.tsx"]` |
| dozens of files, several approaches | Plan mode (+ Explore subagent) |
| one-file fix with stack trace | Direct execution |
| prose misunderstood | 2–3 input/output examples |
| unfamiliar domain | Interview pattern |
| CI job hangs | `-p` |
| machine-readable CI findings | `--output-format json` + `--json-schema` |
| duplicate PR comments | Pass prior findings; report only new/unfixed |

## Try it
*≤ 30 min, offline.* In a **new** folder `team-repo/` (not `claude-demo`), build a team setup that makes `check_setup.sh` print `10 passed, 0 failed`: project CLAUDE.md with the test command, gitignored `CLAUDE.local.md`, a test rule with `paths:`, a team command, a forked skill, a `.mcp.json` with `${GITHUB_TOKEN}`, and `scripts/ci_review.sh`. Then open `claude` there and check `/memory`, `/` and `/mcp` by eye.

<details><summary>Solution</summary>

Run from the folder that holds `check_setup.sh` and `ci_review.sh`:
```bash
#!/usr/bin/env bash
# team_setup.sh — builds a complete team Claude Code setup in a new repo. Offline.
set -euo pipefail
mkdir -p team-repo/{.claude/rules,.claude/commands,.claude/skills/codebase-map,scripts} && cd team-repo && git init -q
printf '# Team\n- Run tests: `uv run pytest -q`\n- Never commit secrets.\n' > CLAUDE.md
echo "CLAUDE.local.md" > .gitignore
printf -- '---\npaths: ["**/test_*.py", "**/*_test.py"]\n---\n- Tests use fixtures from tests/conftest.py; no network.\n' > .claude/rules/tests.md
printf -- '---\ndescription: Team review checklist\nargument-hint: [base-branch]\n---\nReview git diff $ARGUMENTS...HEAD: bugs, missing tests, security. Skip style.\n' > .claude/commands/review.md
printf -- '---\nname: codebase-map\ndescription: Map modules, entry points and tests; 15 lines max\ncontext: fork\nagent: Explore\n---\nMap the repo. Do not edit files.\n' > .claude/skills/codebase-map/SKILL.md
cat > .mcp.json <<'JSON'
{"mcpServers": {"github": {"type": "http", "url": "https://api.githubcopilot.com/mcp/",
  "headers": {"Authorization": "Bearer ${GITHUB_TOKEN}"}}}}
JSON
cp ../ci_review.sh scripts/ci_review.sh   # from lesson 3.6
bash ../check_setup.sh
```
Expected last line: `10 passed, 0 failed`.

</details>

## Quiz
Exam style: about 2 minutes each. Then redo official sample questions 4, 5, 6 and 10 (exam guide p.30–31, exam guide p.34).

**1.** Only one developer gets Claude to follow the team's error-handling rules. They live in that developer's `~/.claude/CLAUDE.md`. Fix? A) Each dev copies the file · B) Move the rules into the project CLAUDE.md or `.claude/rules/` · C) Put them in `CLAUDE.local.md` · D) Add them to a skill

<details><summary>Answer</summary>

**B.** User-level files aren't shared via version control.

</details>

**2.** A `/release-notes` command should exist for everyone after `git pull`. Where?

<details><summary>Answer</summary>

`.claude/commands/release-notes.md` (or `.claude/skills/release-notes/SKILL.md`) in the repo.

</details>

**3.** A codebase-analysis skill dumps thousands of lines into the conversation. Which frontmatter fixes it?

<details><summary>Answer</summary>

`context: fork` — the skill runs in an isolated subagent and returns only its result.

</details>

**4.** Terraform conventions must apply to files under `infra/terraform/` only, without costing context elsewhere. How?

<details><summary>Answer</summary>

`.claude/rules/terraform.md` with `paths: ["infra/terraform/**/*"]`.

</details>

**5.** Migrate 45+ files to a new HTTP library; two approaches are possible. Mode?

<details><summary>Answer</summary>

Plan mode first (explore, compare, plan), then execute the approved plan.

</details>

**6.** Claude's output keeps missing your intended transformation from a prose description. Next step?

<details><summary>Answer</summary>

Give 2–3 concrete input/output examples.

</details>

**7.** **Choose 2.** For a CI review job that posts inline comments: A) `-p` · B) `--output-format json` with `--json-schema` · C) `CLAUDE_HEADLESS=true` · D) `--batch`

<details><summary>Answer</summary>

**A and B.** C and D don't exist.

</details>

**8.** Re-runs after each commit repeat the same review comments. Fix?

<details><summary>Answer</summary>

Include the prior findings in the prompt; ask for only new or still-unaddressed issues.

</details>

**9.** *(D2)* Where do personal, experimental MCP servers go so teammates aren't affected?

<details><summary>Answer</summary>

User scope — `~/.claude.json` (`claude mcp add --scope user …`).

</details>

**10.** *(D4)* Why is a separate Claude run a better reviewer of generated code than the session that wrote it?

<details><summary>Answer</summary>

The generating session keeps its reasoning context and tends to confirm its own decisions; an independent instance catches subtle issues more often.

</details>

## References
- [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Run Claude Code programmatically](https://code.claude.com/docs/en/headless)
