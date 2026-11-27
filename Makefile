# Usage: make run <code>   e.g. make run 1_1  → runs D1-*/codes/1_1_*.py
#        make run 4_5_sla → runs the exact file D4-*/codes/4_5_sla.py

# Agent SDK: skip claude.ai connectors; they're off anyway when an API key is set.
export ENABLE_CLAUDEAI_MCP_SERVERS = false

ifeq (run,$(firstword $(MAKECMDGOALS)))
  CODE := $(word 2,$(MAKECMDGOALS))
  FILE := $(firstword $(wildcard D*/*/$(CODE).py D*/*/$(CODE)_*.py))
  # Make the code a no-op target so make doesn't try to build it.
  .PHONY: $(CODE)
  $(eval $(CODE):;@:)
endif

.PHONY: run
run:
	@test -n "$(CODE)" || { echo "usage: make run <code>   e.g. make run 1_1"; exit 1; }
	@test -n "$(FILE)" || { echo "no file for code $(CODE) (looked for D*/*/$(CODE)_*.py)"; exit 1; }
	@grep -qsE '^(export )?ANTHROPIC_API_KEY=.' .env || { echo "ANTHROPIC_API_KEY missing in .env"; exit 1; }
	uv run --env-file .env python $(FILE)
