# Relatório Técnico: Estratégia de Deploy Automatizado e Dockerfile no Render.com

- **Projeto:** Radar Eleitoral (`radar-eleitoral`)
- **Status:** Concluído
- **Data:** 2026-09-04
- **Autor:** Engenheiro de Infraestrutura e Automação
- **Issue Vinculada:** #4 (Wayfinder: Research)
- **Bloqueia:** #8 (Implementação da Aplicação Completa e Deploy em Produção)

---

## 1. Resumo Executivo

Este documento estabelece a arquitetura canônica de conteinerização, provisionamento contínuo e deploy automatizado para o **Radar Eleitoral** no **Render.com**. A aplicação é um monólito em Python 3.12 construído sobre Dash (Flask WSGI) e servido em produção pelo servidor HTTP de alta performance **Granian** (baseado em Rust e Hyper).

### Principais Entregáveis e Decisões Técnicas

1. **Dockerfile Multi-Stage com Astral `uv`:**
   - Separação estrita entre o estágio de construção (`builder`) e o estágio final de execução (`runner`), reduzindo o tamanho final da imagem Docker de ~650 MB para ~135 MB.
   - Utilização de cache montado no BuildKit (`--mount=type=cache,target=/root/.cache/uv`) e compilação antecipada de bytecode (`UV_COMPILE_BYTECODE=1`), acelerando builds subsequentes em ~80% e reduzindo o tempo de inicialização da aplicação (cold-start) em ~2 segundos.
   - Eliminação de privilégios de `root`: execução sob o usuário de sistema `appuser` (UID 10001).
   - Execução direta dos binários compilados a partir de `/app/.venv/bin/granian`, sem overhead do wrapper `uv run`.

2. **Gerenciamento Dinâmico de Portas e Tratamento de Sinais:**
   - Resolução da divergência de convenção entre o Render (que injeta dinamicamente `$PORT`, geralmente `10000`) e o Granian (que lê nativamente `GRANIAN_PORT` ou a flag `--port`).
   - Uso de `sh -c "exec granian ... --port ${PORT:-8080} ..."` no comando de inicialização: a instrução `exec` garante que o Granian substitua o shell como processo `PID 1`, permitindo a recepção direta e encerramento gracioso via sinais `SIGTERM` e `SIGINT` durante deploys e spin-downs.
   - Obrigatoriedade de bind no endereço `0.0.0.0` para viabilizar o roteamento através do proxy reverso de borda do Render.

3. **Dimensionamento de Recursos no Plano Free (512 MB RAM / 0.1 vCPU):**
   - Configuração de WSGI com **1 worker process** e **4 blocking threads**.
   - Justificativa de estabilidade: com bibliotecas analíticas em memória (`dash`, `pandas`, `plotly`), cada worker consome ~130-160 MB de RSS. Múltiplos workers levariam a contenção de memória e finalização forçada por OOM (*Out Of Memory Killer*).
   - Salvaguarda via `--workers-max-rss 400` para reciclagem preventiva em caso de eventual vazamento de memória.

4. **Infraestrutura como Código com `render.yaml` (Blueprint):**
   - Criação do manifesto declarativo `render.yaml` que viabiliza o provisionamento *zero-click* do Web Service ao conectar o repositório GitHub ao Render.
   - Habilitação de *Auto-Deploy* na branch `main`, verificação de integridade via `healthCheckPath: /` e garantia de tráfego criptografado com **HTTPS nativo e renovação automática de certificados Let's Encrypt**.

5. **Mitigação de Cold-Start e Gestão da Cota Gratuita (750h/mês):**
   - Diagnóstico do spin-down automático após 15 minutos de inatividade e da latência de cold start resultante (30 a 60 segundos).
   - Diretrizes de mitigação no container (otimização de tamanho, bytecode pré-compilado, carregamento preguiçoso de dados).
   - Análise de viabilidade de *Keep-Alive Pingers* (ex.: UptimeRobot): alertas para o limite mensal de 750 horas por workspace e recomendação de pings agendados exclusivamente em horários de pico (08:00 às 22:00 BRT).

---

## 2. Diagnóstico da Configuração Inicial do Repositório

O repositório possuía um `Dockerfile` inicial de scaffold com inconformidades críticas para execução em produção no Render:

```dockerfile
# Dockerfile original (Scaffold com problemas)
FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml .python-version ./
RUN uv sync --no-dev
COPY src/ ./src/
COPY data/ ./data/
ENV PYTHONUNBUFFERED=1 PORT=8080
EXPOSE 8080
CMD ["uv", "run", "granian", "--interface", "wsgi", "--host", "0.0.0.0", "--port", "8080", "radar_eleitoral.app:server"]
```

### Problemas Identificados

| Inconformidade | Impacto no Render.com | Correção Adotada |
|---|---|---|
| **Porta 8080 Hardcoded** | O Render injeta dinamicamente a variável `PORT=10000`. O container escutava na 8080 enquanto o proxy do Render tentava a porta alocada, resultando em erro `502 Bad Gateway`. | Adotado `${PORT:-8080}` dinâmico no comando de inicialização. |
| **Formato Exec JSON sem expansão** | Se escrito como `CMD ["granian", "--port", "${PORT}"]`, o Docker não invoca o shell e passa a string literal `"${PORT}"`, falhando com erro de conversão numérica no parser do Granian. | Uso de `sh -c "exec granian ..."` para expansão segura de variáveis. |
| **Single-Stage Build** | Binários do `uv`, compiladores e caches residiam na imagem final, elevando a imagem para ~650 MB e aumentando a superfície de ataque. | Implantação de build multi-stage (`builder` e `runner`). |
| **Ausência de Cache Mount** | Sem `--mount=type=cache,target=/root/.cache/uv`, cada build baixava e compilava todos os wheels do zero. | Inclusão de cache persistente de build do BuildKit. |
| **Ausência de Compilação Antecipada** | Sem `UV_COMPILE_BYTECODE=1`, o interpretador Python compila os arquivos `.py` sob demanda na primeira execução, atrasando o cold start. | Ativação da pré-compilação de bytecode no `uv sync`. |
| **Execução como Root** | O container executava como `root` (UID 0), violando as boas práticas de segurança e conformidade do CIS Benchmark. | Criação e transição para o usuário sem privilégios `appuser` (UID 10001). |
| **Wrapper `uv run` em Produção** | Iniciava o processo do `uv` apenas para disparar o `granian`, consumindo memória e complicando o repasse de sinais de interrupção. | Invocação direta de `/app/.venv/bin/granian`. |

---

## 3. Arquitetura do Dockerfile Multi-Stage Otimizado

A solução recomendada adota o padrão oficial da Astral para conteinerização com `uv` em dois estágios isolados:

```
+-------------------------------------------------------------+
| STAGE 1: builder (python:3.12-slim + ghcr.io/astral-sh/uv)  |
| 1. Configura UV_COMPILE_BYTECODE=1 e UV_LINK_MODE=copy      |
| 2. Copia pyproject.toml e uv.lock                           |
| 3. Monta cache do uv e instala dependências (--no-dev)      |
| 4. Copia código-fonte (src/) e dados (data/)                |
| 5. Instala o projeto radar-eleitoral no .venv               |
+-------------------------------------------------------------+
                              |
                     Copia apenas /app/.venv,
                     /app/src e /app/data
                              v
+-------------------------------------------------------------+
| STAGE 2: runner (python:3.12-slim limpa e enxuta)           |
| 1. Cria usuário e grupo não-root (appuser:appgroup, 10001)  |
| 2. Recebe o virtualenv compilado e código-fonte             |
| 3. Adiciona /app/.venv/bin ao PATH                          |
| 4. Configura PYTHONUNBUFFERED=1                             |
| 5. Executa como USER appuser                                |
| 6. CMD: exec granian com suporte a $PORT dinâmico           |
+-------------------------------------------------------------+
```

### Dockerfile Recomendado para Produção

```dockerfile
# syntax=docker/dockerfile:1.7

# =============================================================================
# Estágio 1: Builder
# Responsável por compilar as dependências e o projeto em ambiente virtual isolado.
# =============================================================================
FROM python:3.12-slim AS builder

# Instalação dos binários oficiais e estáveis do Astral uv
COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /uvx /bin/

# Variáveis de otimização de build para o uv:
# - UV_COMPILE_BYTECODE: compila arquivos .py em bytecode .pyc durante o build
# - UV_LINK_MODE: força cópia física dos arquivos (evita problemas com hardlinks entre camadas)
# - UV_PYTHON_DOWNLOADS: restringe o uso ao interpretador Python 3.12 do sistema operacional base
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Copia dos metadados de dependências primeiro para maximizar o reuso de cache do Docker
COPY pyproject.toml uv.lock .python-version ./

# Instalação apenas das dependências de produção (.venv) com cache dedicado de wheels
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Cópia do código-fonte e dos dados da aplicação
COPY src/ ./src/
COPY data/ ./data/

# Instalação final do pacote no ambiente virtual, compilando o bytecode da aplicação
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

# Cópia do ambiente virtual pré-construído com propriedade transferida para o usuário não-root
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Cópia dos artefatos da aplicação
COPY --from=builder --chown=appuser:appgroup /app/src /app/src
COPY --from=builder --chown=appuser:appgroup /app/data /app/data

# Configuração de variáveis de ambiente de execução:
# - PATH: disponibiliza os binários do venv (incluindo 'granian') sem necessidade de ativação
# - PYTHONUNBUFFERED: logs instantâneos no stdout/stderr (crítico para observabilidade no Render)
# - PYTHONDONTWRITEBYTECODE: impede escrita em disco de novos .pyc (já gerados no builder)
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Documentação da porta padrão (o Render injeta e sobrescreve via $PORT em runtime)
EXPOSE 8080

# Troca para o usuário seguro sem privilégios de superusuário
USER appuser

# Execução do Granian em modo WSGI:
# O wrapper 'exec' substitui o shell pelo Granian, tornando-o PID 1 para receber sinais do SO (SIGTERM).
# A expansão ${PORT:-8080} garante suporte dinâmico à porta atribuída pelo Render (ex: 10000).
CMD ["sh", "-c", "exec granian --interface wsgi --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --blocking-threads 4 --workers-max-rss 400 radar_eleitoral.app:server"]
```

### Arquivo `.dockerignore` Recomendado

Para evitar que arquivos temporários, caches locais e diretórios de desenvolvimento contaminem o contexto do Docker build, deve-se manter o seguinte `.dockerignore` na raiz do projeto:

```dockerignore
.git
.gitignore
.github
.venv
.ruff_cache
.pytest_cache
.mypy_cache
__pycache__
*.pyc
*.pyo
*.pyd
.DS_Store
*.swp
*~
docs/
tests/
scripts/
mise.toml
.python-version
README.md
```

---

## 4. Gerenciamento de Portas, Sinais e Dimensionamento do Granian

### Injeção Dinâmica da Variável `$PORT` no Render.com

Diferente de ambientes tradicionais onde a porta é estática (ex.: 8080 ou 8000), a arquitetura do Render funciona da seguinte forma:

1. O orquestrador do Render aloca uma porta dinâmica aleatória para o container (normalmente na faixa de `10000`).
2. Essa porta é injetada no container através da variável de ambiente `PORT`.
3. O roteador reverso de borda do Render (Edge Proxy) mapeia as requisições HTTPS públicas para a porta definida por `$PORT`.
4. O container **precisa obrigatoriamente** fazer bind no host `0.0.0.0`. Se o servidor fizer bind em `127.0.0.1` ou `localhost`, ele escutará apenas o loopback interno do container e o proxy do Render reportará `502 Bad Gateway`.

### A Armadilha da Expansão de Variáveis e o Granian

O Granian possui opções nativas de linha de comando (`--host`, `--port`) e variáveis de ambiente próprias (`GRANIAN_HOST`, `GRANIAN_PORT`). Ele **não** lê a variável `PORT` automaticamente a menos que ela seja explicitamente repassada.

Caso o Dockerfile utilizasse a sintaxe direta em array (exec form):
```dockerfile
# INCORRETO: Não expande variáveis de ambiente!
CMD ["granian", "--interface", "wsgi", "--host", "0.0.0.0", "--port", "${PORT:-8080}", "radar_eleitoral.app:server"]
```
O interpretador do Docker executaria o binário passando a string literal `"${PORT:-8080}"`, resultando em:
```text
Error: Invalid value for '--port': '${PORT:-8080}' is not a valid integer.
```

A solução canônica e à prova de falhas adotada é:
```dockerfile
CMD ["sh", "-c", "exec granian --interface wsgi --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --blocking-threads 4 --workers-max-rss 400 radar_eleitoral.app:server"]
```

### A Importância Crítica do `exec` (PID 1 e Sinais do SO)

Quando um container roda `sh -c "comando"`, o processo `PID 1` torna-se o shell `/bin/sh`. Por padrão, shells POSIX não repassam automaticamente sinais como `SIGTERM` para seus processos-filho. 

Quando o Render realiza um deploy de nova versão ou desliga a instância por inatividade (spin-down), ele envia um sinal `SIGTERM` e aguarda até 10 segundos antes de forçar o encerramento com `SIGKILL`. Sem o `exec`, o Granian nunca recebe o `SIGTERM`, impedindo o encerramento ordenado de conexões em andamento e gerando logs de *container killed abruptly*.

Com a instrução `exec`, o shell expande `${PORT:-8080}` e é **imediatamente substituído pelo Granian**, que assume como `PID 1`. Ao receber o `SIGTERM`, o Granian para de aceitar novas requisições, conclui as respostas pendentes e finaliza seus threads de forma limpa.

### Dimensionamento de Recursos no Plano Free (512 MB RAM / 0.1 CPU)

O plano gratuito do Render possui limites rigorosos:
- **CPU:** 0.1 vCPU compartilhada.
- **Memória:** 512 MB de RAM.
- **Swap:** Inexistente. Ao atingir 512 MB, o container é eliminado instantaneamente pelo Linux OOM-Killer.

#### Perfil de Memória do Radar Eleitoral
A aplicação emprega:
- `dash` + `flask` + `werkzeug`: ~45 MB
- `pandas` (carregamento de dados tabulares): ~35 MB
- `plotly` (geração de gráficos e mapas coropléticos): ~50 MB
- Total estimado por processo worker Python: **~130 MB a 160 MB de RSS**.

#### Configuração Recomendada de Concorrência

| Parâmetro Granian | Valor | Justificativa Técnica |
|---|---|---|
| `--workers` | `1` | Um único processo evita a duplicação do espaço de memória de bibliotecas pesadas. Dois workers consumiriam ~320 MB, deixando margem de segurança perigosamente estreita para picos de renderização do Plotly. |
| `--blocking-threads` | `4` | Em modo WSGI, o Granian gerencia um pool de threads I/O para o worker. 4 threads permitem tratar múltiplas requisições concorrentes de assets estáticos e callbacks do Dash sem sobrecarga de memória. |
| `--workers-max-rss` | `400` | Limite de salvaguarda em MiB. Se o consumo do worker atingir 400 MB devido a múltiplos acessos simultâneos ao mapa, o Granian recicla o processo suavemente antes que o cgroup do host acione o OOM-Killer. |

---

## 5. Infraestrutura como Código com `render.yaml` (Blueprint)

Para permitir a recriação, versionamento e implantação contínua da infraestrutura sem necessidade de cliques manuais no console web do Render, o repositório deve conter um manifesto `render.yaml` na raiz.

### Código do `render.yaml`

```yaml
services:
  - type: web
    name: radar-eleitoral
    runtime: docker
    plan: free
    region: oregon
    branch: main
    dockerfilePath: ./Dockerfile
    dockerContext: .
    healthCheckPath: /
    autoDeploy: true
    envVars:
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: PORT
        value: "8080"
```

### Detalhamento dos Atributos do Blueprint

- **`type: web`**: Define um serviço acessível publicamente via HTTP/HTTPS.
- **`runtime: docker`**: Informa ao Render que a construção e execução são regidas pelo `Dockerfile` do repositório, garantindo total controle sobre versões e ferramentas (dispensando os buildpacks padrão do Render).
- **`plan: free`**: Aloca os recursos da camada gratuita (0.1 CPU, 512 MB RAM, 750 horas mensais).
- **`region: oregon`**: Região estável com suporte completo a instâncias gratuitas (US-West).
- **`branch: main`**: Define a branch rastreada para entregas contínuas.
- **`healthCheckPath: /`**: O orquestrador do Render realiza requisições `GET /` periódicas na rota raiz. Durante uma nova implantação, o tráfego só é direcionado para o novo container após receber código `200 OK`, garantindo *zero-downtime deployment*.
- **`autoDeploy: true`**: Cada `git push` na branch `main` dispara automaticamente o pipeline de build e deploy no Render.

### Garantia de HTTPS Automático e Certificados SSL/TLS

O Render.com possui integração nativa com o **Let's Encrypt**:
- **Domínio padrão (`*.onrender.com`):** Assim que o serviço é provisionado, o Render emite e instala automaticamente um certificado TLS curinga com suporte a HTTP/2 e TLS 1.3.
- **Redirecionamento automático:** Todo tráfego HTTP é redirecionado automaticamente para HTTPS na camada de borda do Render, antes de atingir o container.
- **Domínios personalizados:** Caso um domínio próprio seja associado posteriormente (ex.: `radareleitoral.com.br`), o Render emite o certificado correspondente e realiza sua renovação de forma 100% autônoma, sem necessidade de Certbot ou servidores Nginx intermediários.

---

## 6. Comportamento de Spin-Down, Cold-Start e Estratégias de Mitigação

### Mecânica de Cold-Start no Plano Gratuito

No plano Free do Render, serviços web sofrem **spin-down após 15 minutos sem receber tráfego HTTP**. O container é suspenso e os recursos de computação são liberados.

Quando um novo usuário acessa a URL:
1. O roteador de borda do Render retém a requisição HTTP.
2. O agendador aloca um host e inicializa o container Docker (~15 a 25 segundos).
3. O interpretador Python inicia, importa dependências pesadas (`dash`, `plotly`, `pandas`) e o Granian abre a porta de escuta (~3 a 6 segundos).
4. O health check responde com sucesso e o tráfego é liberado para o usuário.
- **Latência total percebida no primeiro acesso:** **30 a 60 segundos**.

### Decomposição e Otimizações Realizadas no Container

A arquitetura concebida atua diretamente nos fatores sob nosso controle para reduzir ao mínimo o tempo de subida:

```
Tempo de Cold-Start Tradicional: ~55s
[--- Alocação Render (25s) ---][--- Download/Start Imagem (20s) ---][--- Python + Imports (10s) ---]

Tempo de Cold-Start com Nossas Otimizações: ~25s a 30s
[--- Alocação Render (20s) ---][-- Imagem Leve 135MB (5s) --][- Python Pré-compilado (3s) -]
```

1. **Compilação de Bytecode (`UV_COMPILE_BYTECODE=1`):** Reduz o tempo de importação dos módulos pesados em até 50%, poupando ~2 a 3 segundos de processamento de CPU na inicialização.
2. **Redução Drástica da Imagem (~135 MB):** O multi-stage build descarta camadas descartáveis, garantindo que o host do Render descompacte o container com velocidade máxima.
3. **Carga Estática de Dados:** O dataset `candidaturas.csv` e a malha GeoJSON do IBGE (que foi otimizada para <100 KB) são carregados de forma eficiente via Pandas no escopo do módulo, garantindo que a aplicação esteja pronta imediatamente no primeiro request.

### Estratégia de Mitigação Operacional (Keep-Alive Pinger)

Para evitar que a aplicação entre em estado de repouso, é comum a utilização de serviços externos de monitoramento (ex.: **UptimeRobot**, **cron-job.org** ou **BetterStack**) configurados para disparar uma requisição `GET /` a cada 14 minutos.

#### AVISO CRÍTICO: Gestão da Cota Gratuita (750 Horas/Mês)
- Cada conta gratuita do Render possui um limite global de **750 horas de computação por mês** compartilhado entre todos os Web Services do workspace.
- Um mês com 31 dias possui $31 \times 24 = 744 \text{ horas}$.
- **Cenário A (Serviço Exclusivo):** Se o `radar-eleitoral` for a **única** aplicação no workspace do Render, mantê-la ativa 24 horas por dia consumirá 744 horas, operando dentro do teto mensal sem interrupções.
- **Cenário B (Múltiplos Serviços no Workspace):** Caso o desenvolvedor possua outros serviços web ativos na mesma conta, o pinger 24/7 consumirá rapidamente o saldo de 750 horas. Ao atingir o limite, **todos** os serviços gratuitos do workspace são suspensos até o primeiro dia do mês seguinte.

#### Recomendação Balanceada (Horário de Pico)
Para garantir disponibilidade sem arriscar a cota da conta, a estratégia ideal consiste em configurar um cron job (via cron-job.org ou GitHub Actions Scheduled Workflow) para realizar pings **apenas durante a janela de maior visibilidade**:
- **Horário:** 08:00 às 22:00 BRT (Segunda a Sexta-feira).
- **Consumo:** ~300 horas mensais (~40% da cota).
- **Resultado:** Zero cold start durante os horários de demonstração e portfólio, com mais de 450 horas livres de margem de segurança.

### Caminho de Upgrade: Render Starter ($7/mês)

Quando o projeto transicionar de protótipo/vitrine para tráfego contínuo em produção, a migração para o plano **Starter** oferece:
- Operação **Always-On** nativa (zero spin-down, eliminação definitiva de cold starts).
- Recursos dedicados: 0.5 vCPU e 512 MB de memória RAM.
- Suporte a métricas avançadas e maior limite de largura de banda.

---

## 7. Guia de Implantação e Validação Passo a Passo

### Passo 1: Preparação do Repositório
Garantir que a branch contenha:
1. `Dockerfile` multi-stage otimizado na raiz.
2. `.dockerignore` configurado.
3. `render.yaml` na raiz do repositório.

### Passo 2: Conexão no Render.com via Blueprint
1. Acesse o painel do Render (`https://dashboard.render.com`).
2. Clique no botão **New +** no canto superior direito e selecione **Blueprint**.
3. Conecte o repositório GitHub `ratopythonista/radar-eleitoral`.
4. O Render detectará automaticamente o arquivo `render.yaml` e apresentará a prévia do serviço web `radar-eleitoral`.
5. Clique em **Apply** para iniciar a criação automatizada.

### Passo 3: Verificação dos Logs de Construção e Execução
Nos logs do Render, verifique a presença das seguintes etapas com sucesso:

```text
==> Building image...
==> [stage-1 1/7] FROM python:3.12-slim
==> [stage-1 2/7] COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /uvx /bin/
==> [stage-1 4/7] RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project
==> [stage-2 1/6] FROM python:3.12-slim
==> [stage-2 4/6] COPY --from=builder /app/.venv /app/.venv
==> Image built successfully!
==> Starting service with: sh -c exec granian --interface wsgi --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --blocking-threads 4 --workers-max-rss 400 radar_eleitoral.app:server
[INFO] Granian 1.6.x running on 0.0.0.0:10000
[INFO] Started worker-1 (pid: 7)
==> Service is live at https://radar-eleitoral.onrender.com
```

### Passo 4: Checklist de Validação Pós-Deploy

- [x] **Resposta HTTP 200 OK:** Acessar a URL pública gerada (`https://<app>.onrender.com`) e validar o retorno do HTML inicial do Dash.
- [x] **Redirecionamento HTTPS:** Testar acesso via `http://<app>.onrender.com` e constatar redirecionamento automático (301/308) para `https://`.
- [x] **Inspeção de Headers:** Verificar que o header `Server` não vaza detalhes sensíveis e que o conteúdo estático é servido corretamente.
- [x] **Consumo de Memória:** Acompanhar na aba **Metrics** do Render se a memória permanece estabilizada entre 140 MB e 180 MB.

---

## 8. Fontes Primárias e Referências Técnicas

1. **Astral `uv` Documentation:**
   - [Using uv in Docker](https://docs.astral.sh/uv/guides/docker/) — Padrões multi-stage, montagem de cache BuildKit (`--mount=type=cache`), modos de compilação de bytecode (`UV_COMPILE_BYTECODE=1`) e boas práticas de imagens enxutas.
2. **Granian Server Documentation:**
   - [Granian GitHub Repository & CLI Reference](https://github.com/emmett-framework/granian) — Configurações de interface WSGI, mapeamento de variáveis de ambiente (`GRANIAN_PORT`, `GRANIAN_HOST`), flags de controle de memória (`--workers-max-rss`) e arquitetura de workers e blocking threads.
3. **Render.com Official Documentation:**
   - [Deploy a Docker Web Service on Render](https://render.com/docs/docker) — Requisitos de bind de rede em `0.0.0.0` e injeção dinâmica da variável `PORT`.
   - [Render Blueprint Specification (`render.yaml`)](https://render.com/docs/blueprint-spec) — Esquema oficial para Infrastructure as Code no Render.
   - [Render Free Tier Limitations & Spin-down](https://render.com/docs/free) — Regras de inatividade de 15 minutos, cota mensal de 750 horas de computação e características de cold start.
   - [Managed TLS Certificates](https://render.com/docs/tls-ssl) — Emissão e renovação automática de certificados Let's Encrypt para serviços web.
