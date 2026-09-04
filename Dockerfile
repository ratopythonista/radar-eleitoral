# syntax=docker/dockerfile:1.7

# =============================================================================
# Estágio 1: Builder
# Responsável por compilar as dependências e o projeto em ambiente virtual isolado.
# =============================================================================
FROM python:3.12-slim AS builder

# Instalação dos binários oficiais do Astral uv
COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /uvx /bin/

# Variáveis de otimização de build para o uv:
# - UV_COMPILE_BYTECODE: compila arquivos .py em bytecode .pyc durante o build
# - UV_LINK_MODE: força cópia física dos arquivos (evita problemas com hardlinks entre camadas)
# - UV_PYTHON_DOWNLOADS: restringe o uso ao interpretador Python 3.12 do sistema base
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Copia dos metadados de dependências primeiro para maximizar o reuso de cache do Docker
COPY pyproject.toml uv.lock .python-version ./

# Instalação apenas das dependências de produção (.venv) com cache montado do uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Cópia do código-fonte e dados da aplicação
COPY src/ ./src/
COPY data/ ./data/

# Instalação final do projeto no ambiente virtual, pré-compilando todo o bytecode
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# =============================================================================
# Estágio 2: Runner
# Imagem final de produção: mínima, sem ferramentas de build, não-root e de alta performance.
# =============================================================================
FROM python:3.12-slim AS runner

# Criação de usuário e grupo de sistema com privilégios reduzidos (UID/GID 10001)
RUN groupadd --system --gid 10001 appgroup && \
    useradd --system --uid 10001 --gid appgroup --create-home --home-dir /app appuser

WORKDIR /app

# Cópia do ambiente virtual pré-construído com permissões para o usuário não-root
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Cópia dos artefatos da aplicação
COPY --from=builder --chown=appuser:appgroup /app/src /app/src
COPY --from=builder --chown=appuser:appgroup /app/data /app/data

# Configuração de variáveis de ambiente de execução:
# - PATH: disponibiliza os binários do venv (incluindo 'granian') sem overhead de 'uv run'
# - PYTHONUNBUFFERED: logs instantâneos no stdout/stderr para o painel do Render
# - PYTHONDONTWRITEBYTECODE: impede escrita de arquivos .pyc em disco em runtime
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Documentação da porta padrão (Render injeta e sobrescreve via $PORT em runtime)
EXPOSE 8080

# Troca para o usuário seguro sem privilégios de superusuário
USER appuser

# Execução do Granian em modo WSGI:
# O wrapper 'exec' substitui o shell pelo Granian, tornando-o PID 1 para receber sinais do SO (SIGTERM).
# A expansão ${PORT:-8080} garante suporte dinâmico à porta atribuída pelo Render (ex: 10000).
CMD ["sh", "-c", "exec granian --interface wsgi --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --blocking-threads 4 --workers-max-rss 400 radar_eleitoral.app:server"]
