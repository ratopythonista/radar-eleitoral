# Context: Radar Eleitoral

Aplicação web pública em FastHTML monolítico com HTMX e Granian ASGI para divulgação de matérias jornalísticas automatizadas do G1 por estado e cargo, destacando feitos de automação jornalística e servindo como vitrine profissional.

## Glossário

### Candidatura
Registro eleitoral público de um indivíduo concorrendo a um cargo político em determinada Unidade da Federação ou em âmbito nacional.
_Avoid: Político, Eleito._

### Cargo
Posto eletivo em disputa (ex.: Governador, Senador, Deputado Federal, Deputado Estadual, Deputado Distrital, Presidente). Possui abrangência distrital, estadual ou nacional.
_Avoid: Função, Emprego._

### UF (Unidade da Federação)
Estado brasileiro representado por sigla de 2 letras (ex: SP, RJ, MG) ou o identificador especial de abrangência nacional (BR).
_Avoid: Região, Município (para o escopo v1)._

### Matéria Automatizada
Página ou reportagem oficial do G1 gerada por algoritmos de inteligência artificial e pipelines editoriais automatizados, contendo a relação de concorrentes para um dado par (UF, Cargo).
_Avoid: Notícia interna, Scraping, Raw data._

### Hero Card
Painel lateral/inferior de destaque na interface do mapa que exibe a introdução, o estado/cargo selecionado e um Call to Action claro para abrir a matéria correspondente no G1.
_Avoid: Pop-up invasivo, Tooltip simples._


### Mapa Vetorial SVG
Representação cartográfica vetorial interativa do Brasil renderizada diretamente como SVG inline no DOM, onde cada Unidade da Federação é um polígono/caminho clicável instrumentado com atributos HTMX (`hx-get`, `hx-target`), eliminando a sobrecarga de runtimes JavaScript pesados (como Plotly.js/React).
_Avoid: Canvas fechado, WebGL, Mapa coroplético em biblioteca gráfica pesada._

### Cartograma de UFs
Representação visual esquemática do Brasil estruturada em grade retangular uniforme (tile grid map) por macrorregiões, onde cada Unidade da Federação possui peso visual e alvo de clique equivalentes, viabilizando a seleção tátil acessível especialmente em telas menores ou como alternativa à mira do mapa.
_Avoid: Mapa distorcido ilegível, Lista suspensa simples._
### Apoio
Mecanismo voluntário de doação financeira de apoiadores exclusivamente via Pix (QR Code dinâmico/estático e chave copia-e-cola) na página `/sobre`.
_Avoid: Cobrança, Assinatura, Paywall, Buy Me a Coffee._

### Human-in-the-Loop
Princípio editorial e arquitetural em que reportagens geradas por inteligência artificial a partir de dados públicos oficiais são obrigatoriamente revisadas e chanceladas por jornalistas antes da publicação.
_Avoid: Autonomia total, Publicação cega, Geração desassistida._

### Código Pix Copia-e-Cola
Cadeia textual no padrão EMVCo (BR Code) estabelecido pelo Banco Central contendo payload padronizado para efetivação de transferências instantâneas via aplicativos bancários.
_Avoid: Link de pagamento, Boleto, Checkout externo._

### Disclaimer de Independência
Declaração explícita de isenção institucional, assegurando a natureza estritamente pessoal, cívica e de código aberto do projeto, sem vínculo financeiro, comercial ou patrocínio com o Grupo Globo ou G1.
_Avoid: Termos de Uso genéricos, Nota de rodapé oculta._

## Dependências

- **radar-eleitoral → data/candidaturas.csv**: Aplicação consome dataset tabular local estático (contrato: colunas `uf`, `cargo`, `url_g1`, `resumo`, `candidaturas`).
- **radar-eleitoral → G1 (Globo)**: Aplicação redireciona o usuário para links canônicos públicos do portal G1 via navegação web nativa (`target="_blank"`).
- **radar-eleitoral → SVG Map**: Renderização cartográfica consome malha vetorial SVG nativa inline leve (<25KB) com identificadores oficiais das 27 UFs.
- **radar-eleitoral → Render.com**: Deploy contínuo automatizado do container Docker gerenciado pelo Granian.
