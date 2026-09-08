# Guia Completo de Estudo e Migração: Plotly Dash para FastHTML + HTMX

Este documento foi elaborado para consolidar o entendimento arquitetural, conceitual e prático da migração do **Radar Eleitoral**, substituindo o monólito em Plotly Dash pelo padrão **FastHTML + HTMX sobre ASGI (Starlette / Granian)**, conforme estabelecido no `pyspecific` ADR-0007.

---

## 1. Visão Geral: Por Que Mudamos?

| Aspecto | Plotly Dash (Antes) | FastHTML + HTMX (Agora) |
|---|---|---|
| **Paradigma** | SPA reativa em Python rodando React no navegador | HTML semântico no servidor + Hipermídia declarativa (HTMX) |
| **Peso do Cliente (JS)** | ~3.5 MB (React, ReactDOM, Plotly.js, Dash renderer) | **~14 KB** (apenas o runtime minimalista do HTMX) |
| **Interface de Servidor** | **WSGI** (Flask síncrono) | **ASGI** assíncrono nativo (Starlette / AnyIO) |
| **Runner de Produção** | `granian --interface wsgi` | `granian --interface asgi` |
| **Gerenciamento de Estado** | In-memory `dcc.Store` no cliente + callbacks em cadeia | URLs expressivas (`?uf=...&cargo=...`) + `history.pushState` |
| **Visualização do Mapa** | Canvas/WebGL via `plotly.express.choropleth` e GeoJSON | **SVG Nativo inline** (<25 KB) com polígonos clicáveis |
| **Dependências Pesadas** | 22 pacotes (`dash`, `plotly`, `pandas`, `numpy`, `flask`...) | Removidos! Apenas `python-fasthtml` e utilitários leves |
| **Tempo de Resposta (TTI)** | 3 a 5 segundos no primeiro carregamento móvel | **Sub-segundo (<300ms)** instantâneo |

---

## 2. Conceitos Fundamentais do FastHTML

### 2.1 FastTags e o Tipo `fh.FT`
No Dash, você utilizava componentes como `html.Div(...)` e `dcc.Link(...)`.
No FastHTML, tags são funções em Python que geram nós de árvore FastTag (`fh.FT`):

```python
from fasthtml import common as fh

# No Dash:
# html.Div([html.H1("Título", className="text-xl")], className="container")

# No FastHTML:
card = fh.Div(
    fh.H1("Título", cls="text-xl font-bold text-white"),
    fh.P("Descrição do card", cls="text-slate-300"),
    cls="p-4 rounded-xl bg-slate-900 border border-white/10",
)
```

**Regras de Sintaxe:**
* Classes CSS usam o argumento **`cls="..."`** (e não `className` ou `class_`).
* Filhos são passados como argumentos posicionais (`*children`), não dentro de uma lista `[...]`.
* Atributos HTML/HTMX são passados como argumentos nomeados (`id="..."`, `href="..."`, `hx_get="..."`).
* Sublinhados em argumentos viram hífens no HTML gerado: `hx_get` vira `hx-get`, `data_uf` vira `data-uf`.

---

### 2.2 O Papel do HTMX: Interatividade Sem Escrever JavaScript
O Dash dependia do decorador `@callback` que serializava estados e despachava JSON para o renderizador React.
Com o HTMX, a interatividade é **declarativa no próprio HTML**:

```python
fh.Button(
    "São Paulo",
    hx_get="/candidaturas?uf=SP&cargo=Governador",  # Faz requisição AJAX GET
    hx_target="#radar-content",  # Onde o HTML retornado será inserido
    hx_swap="outerHTML",  # Como substituir (substitui o nó inteiro)
    hx_push_url="true",  # Atualiza a URL do navegador sem reload
    cls="px-3 py-2 rounded-lg bg-emerald-500 text-black font-bold cursor-pointer",
)
```

**Como o navegador processa isso:**
1. O usuário clica no botão "São Paulo".
2. O HTMX intercepta o clique e faz um `GET /candidaturas?uf=SP&cargo=Governador`.
3. O servidor Python FastHTML processa os dados e retorna apenas o fragmento HTML do elemento `#radar-content` (o Hero Card atualizado e o mapa com o estado destacado).
4. O HTMX substitui o elemento `#radar-content` anterior no DOM pelo novo HTML recebido.
5. O `hx_push_url="true"` chama internamente `window.history.pushState({}, '', '/candidaturas?uf=SP&cargo=Governador')`, atualizando a barra de endereços do navegador instantaneamente (sem recarregar a página).

---

## 3. O Que Mudou Arquivo por Arquivo

### 1. `src/radar_eleitoral/app.py` → `src/radar_eleitoral/main.py`
* **Antes**: Inicializava `dash.Dash(...)`, configurava `server.wsgi_app = ProxyFix(...)` e gerenciava layouts com `dcc.Location`.
* **Agora**: Cria a aplicação ASGI via `fast_app(pico=False, ...)`, monta os arquivos estáticos com `app.mount("/static", StaticFiles(...))` e registra os módulos de páginas explicitamente (`home.register(app)`, `sobre.register(app)`).

### 2. `src/radar_eleitoral/assets/` → `src/radar_eleitoral/static/`
* Seguindo o padrão de projetos Starlette/FastHTML e a convenção do `pyspecific` ADR-0007, a pasta de ativos estáticos foi padronizada como `static/`.
* `manifest.json` e `sw.js` foram atualizados para apontar para `/static/*`.

### 3. `src/radar_eleitoral/map_utils.py` → `src/radar_eleitoral/map_svg.py`
* **Antes**: Carregava um GeoJSON de 100KB do IBGE via Pandas e gerava uma figura Plotly Choropleth de alta complexidade.
* **Agora**: Renderiza um componente SVG puro (`render_brazil_svg_map`) de apenas 25KB contendo as 27 UFs em `<polygon>` e `<path>`. Cada estado possui seu próprio `hx-get` e `<title>` de acessibilidade/tooltip.

### 4. `src/radar_eleitoral/cartograma.py`
* Migrado de `from dash import html` para `from fasthtml import common as fh`.
* As funções de lógica pura (`resolve_smart_selection`, `resolve_cargo_selection`, `REGIOES_BRASIL`) foram preservadas 100% intactas.
* Os botões de UFs e de escopo nacional ("Brasil") receberam atributos HTMX nativos.

### 5. `src/radar_eleitoral/pages/home.py`
* Eliminados os 3 callbacks imperativos do Dash e as instâncias de `dcc.Store`.
* As rotas são registradas via `register(app: FastHTML)`:
  * `GET /`: Retorna a página completa com cabeçalho e layout.
  * `GET /candidaturas`: Endpoint de fragmento HTMX que retorna apenas o miolo interativo `#radar-content`.
  * `GET /view-toggle`: Endpoint de fragmento HTMX que alterna entre o Mapa SVG e a Grade Regional.

### 6. `src/radar_eleitoral/pages/sobre.py`
* Migrado para FastTags FastHTML.
* O `clientside_callback` do Dash em JavaScript foi substituído por uma função limpa vanilla em JavaScript embutida (`copyPixKey`), que copia a chave Pix e exibe feedback visual imediato na tela.

### 7. Infraestrutura (`scripts/server.sh` e `Dockerfile`)
* O comando de execução foi atualizado de WSGI para ASGI:
  ```bash
  # Antes (WSGI):
  granian --interface wsgi radar_eleitoral.app:server

  # Agora (ASGI):
  granian --interface asgi radar_eleitoral.main:app
  ```

---

## 4. Como Testar Aplicações FastHTML

No Dash, os testes precisavam inspecionar árvores de objetos Python (`isinstance(comp, html.Div)`, `comp.children`).
No FastHTML, testamos diretamente o **comportamento HTTP e o HTML gerado**:

```python
from starlette.testclient import TestClient
from radar_eleitoral.main import app


def test_home_page_renders_successfully():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "RADAR" in response.text
    assert "radar-content" in response.text


def test_htmx_fragment_endpoint():
    client = TestClient(app)
    response = client.get("/candidaturas?uf=RJ&cargo=Governador")
    assert response.status_code == 200
    assert "Rio de Janeiro" in response.text
    # Garante que é o fragmento, não a página inteira com tags <html> duplicadas
    assert "<html" not in response.text
```

---

## 5. Roteiro Prático de Comandos

Para exercitar e validar a aplicação no seu dia a dia:

```bash
# Rodar servidor de desenvolvimento (FastHTML + Granian ASGI com hot-reload)
mise run server
# ou: uv run granian --interface asgi --reload src/radar_eleitoral/main.py:app

# Rodar a suíte completa de testes
mise run test
# ou: uv run pytest

# Executar checagem de tipos estáticos
mise run typecheck
# ou: uv run ty check

# Executar formatação e linting
mise run format
mise run lint

# Validação geral de qualidade antes de commits/PRs
mise run check
```
