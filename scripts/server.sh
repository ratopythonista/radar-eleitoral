#!/usr/bin/env bash
set -e
#MISE description="run development server via granian"
uv run granian --interface asgi --reload src/radar_eleitoral/main.py:app
