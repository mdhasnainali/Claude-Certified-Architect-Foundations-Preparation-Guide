# Usage: make run <file>   — name, name.py, or full path (e.g. make run 1_1_agentic_loop)

ifeq (run,$(firstword $(MAKECMDGOALS)))
  ARG  := $(word 2,$(MAKECMDGOALS))
  FILE := $(or $(wildcard $(ARG)),$(shell find . -path ./.venv -prune -o -name '$(basename $(notdir $(ARG))).py' -print -quit))
  # Make the filename a no-op target so make doesn't try to build it.
  .PHONY: $(ARG)
  $(eval $(ARG):;@:)
endif

.PHONY: run
run:
	@test -n "$(ARG)" || { echo "usage: make run <file>"; exit 1; }
	@test -n "$(FILE)" || { echo "not found: $(ARG)"; exit 1; }
	uv run --env-file .env python $(FILE)
