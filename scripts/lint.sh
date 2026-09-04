#!/usr/bin/env bash
set -e
#MISE description="uv run ruff check --fix ."
uv run ruff check --fix .
