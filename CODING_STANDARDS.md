# Coding Standards — Radar Eleitoral

These are the standards this repo is written to. `/code-review` (Standards axis) reads this
file to judge whether a diff conforms — cite the specific rule below when flagging a violation.

> Profile: **FastHTML Web App (Monolith)** per `pyspecific` ADR-0007. Deploys via Dockerfile with
> Granian (ASGI) on Render.com.

## Environment

- **Python 3.12.** Pinned in `.python-version` and `mise.toml` (`[tools] python = "3.12"`), and
  declared as the floor in `pyproject.toml` (`requires-python = ">=3.12"`).
- **uv is the only way dependencies are installed or code is run.** Never call `python`, `pip`,
  `pytest`, `ruff`, or `ty` directly — always through `uv run <tool>` or `mise run <task>`.
- **mise drives the tasks.** `mise.toml` delegates to `scripts/*.sh`. Task list:

  | Task              | Script                 | What it does                                    |
  |-------------------|------------------------|-------------------------------------------------|
  | `mise run setup`    | `scripts/setup.sh`     | creates venv + `uv sync` (installs the env)    |
  | `mise run format`   | `scripts/format.sh`    | `uv run ruff format .`                          |
  | `mise run lint`     | `scripts/lint.sh`      | `uv run ruff check --fix .`                     |
  | `mise run typecheck`| `scripts/typecheck.sh` | `uv run ty check`                               |
  | `mise run test`     | `scripts/test.sh`      | `uv run pytest`                                 |
  | `mise run check`    | `scripts/check.sh`     | lint + format-check + typecheck + test          |
  | `mise run server`   | `scripts/server.sh`    | runs dev server via granian                     |
  | `mise run validate` | `scripts/validate.sh`  | check + validate environment                    |

## Dependency stack

- **fasthtml** — frontend UI framework with native HTMX and Starlette ASGI (`python-fasthtml`).
- **granian** — production ASGI HTTP runner (`granian --interface asgi radar_eleitoral.main:app`).
- **pydantic** — data validation and DTOs.
- **pydantic-settings** — application configuration (`BaseSettings`).
- **segno** — QR code generation for Pix.
- **loguru** — logging.
- **ruff** — linting and formatting (line-length 100, double quotes).
- **ty** — static type checking.
- **pytest** — testing under `tests/`.

## Architecture & Layout

- Source code lives strictly under `src/radar_eleitoral/`.
- Entrypoint at `src/radar_eleitoral/main.py:app` via `fast_app()` and Granian ASGI.
- Modular screens under `src/radar_eleitoral/pages/`:
  - `home.py` (`/`): Interactive Brazil SVG map & Regional Cartogram + Cargo filter + Hero result card via HTMX partials (`/candidaturas`), with author contact footer and independence disclaimer.
- Reusable pure FastTag UI components in `src/radar_eleitoral/map_svg.py`, `cartograma.py`, etc.
- Public static assets in `src/radar_eleitoral/static/` (styles, icons, PWA manifest, service worker).
- Offline-safe public data in `data/candidaturas.csv`. No internal Globo secrets or credentials.

## FastHTML & FastTags Conventions

- **No wildcard imports.** Prohibit `from fasthtml.common import *`. Use explicit imports (`from fasthtml.common import Button, Card, Div, Form, Input, P`) or aliased imports (`from fasthtml import common as fh`).
- **FastTag casing and attributes.** Tags use PascalCase (`Div`, `H1`, `Button`). Tailwind classes use `cls="..."`. HTMX attributes use underscores (`hx_get`, `hx_target`, `hx_swap`, `hx_push_url`).
- **Typed components.** Reusable UI components must be pure functions with explicit type signatures returning `fh.FT` (or FastTag objects).
