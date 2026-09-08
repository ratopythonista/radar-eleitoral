# 0002. Migração Arquitetural de Dash para FastHTML com HTMX e Granian ASGI

## Status

Aceito (supersedes ADR 0001 no tocante ao bundle Plotly)

## Contexto

A aplicação original foi construída sobre Plotly Dash (WSGI / Flask), atendendo à primeira versão do padrão `pyspecific` (ADR-0004).
Embora o Dash tenha permitido prototipação rápida em Python puro, a operação em produção no Render.com revelou restrições severas:

1. **Sobrecarga de Bundle JavaScript e Latência Móvel**: O Dash exige o download e parsing de ~3.5 MB de JavaScript no cliente (React runtime, Plotly.js e o Dash renderer). Em redes móveis 3G/4G, isso gerava alto Time-To-Interactive (TTI) e consumo desnecessário de dados.
2. **Restrição de Modelo de Concorrência (WSGI)**: O backend rodava em Flask sob WSGI síncrono. Embora o Granian mitigasse o servidor HTTP em Rust, a aplicação permanecia bloqueada fora das capacidades modernas do ecossistema assíncrono (ASGI Starlette/AnyIO).
3. **Complexidade de Callbacks e Estado Virtual**: A sincronização entre componentes (mapa, cartograma, botões de cargo e hero card) dependia de callbacks encadeados, `dcc.Store` em memória do cliente e injeção de scripts JavaScript para capturar cliques no mapa coroplético do Plotly.

Com a publicação do **ADR-0007 do `pyspecific`** (*FastHTML com HTMX e Granian ASGI como padrão de monólitos web*), abriu-se o caminho para uma modernização definitiva da vitrine.

## Decisão

1. **Adoção do FastHTML + HTMX**:
   - Substituição total do Dash pelo FastHTML (`python-fasthtml`).
   - O servidor agora renderiza HTML semântico puro diretamente via FastTags (`from fasthtml import common as fh`), enviando fragmentos leves (<10 KB) para o cliente.
   - O cliente executa exclusivamente a biblioteca minimalista do HTMX (~14 KB compactado), dispensando React e Plotly.js.
2. **Mapa Vetorial SVG Nativo**:
   - O mapa do Brasil deixa de ser um gráfico Canvas/WebGL do Plotly e passa a ser uma malha vetorial SVG nativa inline (`map_svg.py`, baseada em geometria aberta do IBGE sob licença MIT, com ~25 KB).
   - Cada uma das 27 Unidades da Federação é representada por um elemento `<polygon>` ou `<path>` instrumentado diretamente com atributos declarativos HTMX (`hx-get`, `hx-target="#radar-content"`, `hx-swap="outerHTML"`, `hx-push-url="true"`).
   - Mantém-se o **Cartograma Regional** por macrorregiões como alternativa de alta acessibilidade tátil para mobile e desktop via toggle.
3. **Servidor ASGI de Alta Performance (Granian)**:
   - O servidor de desenvolvimento e produção é unificado no Granian com `--interface asgi radar_eleitoral.main:app`.
   - Ponto de entrada migrado para `src/radar_eleitoral/main.py` com a função `fast_app(pico=False)`.
4. **Organização de Ativos Estáticos e PWA**:
   - Ativos renomeados de `src/radar_eleitoral/assets/` para `src/radar_eleitoral/static/`, montados de forma canônica no Starlette via `StaticFiles`.
   - Manifest PWA e Service Worker ajustados para servir `/static/*` mantendo instalabilidade em telas iniciais de smartphones.
5. **Rigor de Código e Tipagem**:
   - Proibição de wildcard imports (`from fasthtml.common import *`).
   - Componentes tipados retornando `fh.FT`.

## Opções Consideradas

- **Manter Plotly standalone via CDN dentro do FastHTML**: Rejeitada porque manteria a sobrecarga de ~3 MB de JavaScript no cliente, contrariando o benefício central do FastHTML.
- **Estado efêmero de DOM sem alterar URL (`hx-push-url="false"`)**: Rejeitada após análise de UX e engenharia. A alteração de URL via `pushState` nativo do navegador tem custo nulo (<0,02ms), viabiliza compartilhamento direto de links e garante navegação funcional no botão "Voltar" do navegador.

## Consequências

- **Positivas**:
  - Redução de mais de 98% no payload transferido ao cliente (de ~3.5 MB para <40 KB).
  - Remoção de 22 dependências pesadas do ambiente (`dash`, `flask`, `plotly`, `pandas`, `numpy`, `werkzeug`, etc.), acelerando builds e reduzindo a superfície de vulnerabilidades.
  - Inicialização sub-segundo e navegação instantânea.
  - Alinhamento total com a esteira técnica do `pyspecific`.
- **Trade-off**:
  - Os testes de UI deixam de inspecionar objetos Dash (`html.Div.children`) e passam a validar contratos de fragmentos HTML semânticos via `TestClient` Starlette.
