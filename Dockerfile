FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency definition
COPY pyproject.toml uv.lock .python-version ./

# Install dependencies into project virtual environment
RUN uv sync --frozen --no-dev

# Copy application code and data
COPY src/ ./src/
COPY data/ ./data/

ENV PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "exec uv run granian --interface wsgi --host 0.0.0.0 --port ${PORT:-8080} radar_eleitoral.app:server"]
