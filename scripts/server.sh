#!/usr/bin/env bash
set -e
#MISE description="run development server via granian"
uv run granian --interface wsgi --reload --blocking-threads 4 radar_eleitoral.app:server
