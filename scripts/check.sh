#!/usr/bin/env bash
set -e
#MISE description="lint + format-check + typecheck + test — run before every commit / PR"
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
