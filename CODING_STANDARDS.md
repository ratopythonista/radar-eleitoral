# Coding Standards — Radar Eleitoral

These are the standards this repo is written to. `/code-review` (Standards axis) reads this
file to judge whether a diff conforms — cite the specific rule below when flagging a violation.

> Profile: **Dash Web App (Monolith)** per `pyspecific` ADR-0004. Deploys via Dockerfile with
> Granian (WSGI) on Render.com.

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

- **dash** — frontend UI framework with native Dash Pages (`src/radar_eleitoral/pages/`).
- **granian** — production WSGI HTTP runner (`granian --interface wsgi radar_eleitoral.app:server`).
- **pydantic** — data validation and DTOs.
- **pydantic-settings** — application configuration (`BaseSettings`).
- **plotly** — interactive map rendering (`px.choropleth` with optimized IBGE GeoJSON).
- **pandas** — tabular dataset loading and filtering.
- **loguru** — logging.
- **ruff** — linting and formatting (line-length 100, double quotes).
- **ty** — static type checking.
- **pytest** — testing under `tests/`.

## Architecture & Layout

- Source code lives strictly under `src/radar_eleitoral/`.
- Multi-page Dash layout under `src/radar_eleitoral/pages/`:
  - `home.py` (`/`): Interactive Brazil map (desktop) & Regional Cartogram (mobile/desktop) + Cargo filter + Hero result card.
  - `sobre.py` (`/sobre`): Bio, achievements, social links, Pix QR Code & Buy Me a Coffee.
- Public static assets in `src/radar_eleitoral/assets/` (styles, icons, PWA manifest).
- Offline-safe public data in `data/candidaturas.csv`. No internal Globo secrets or credentials.
