# Context: Radar Eleitoral

Aplicação web pública em Dash monolítico para divulgação de matérias jornalísticas automatizadas do G1 por estado e cargo, destacando feitos de automação jornalística e servindo como vitrine profissional.

## Glossário

### Candidatura
Registro eleitoral público de um indivíduo concorrendo a um cargo político em determinada Unidade da Federação ou em âmbito nacional.
_Avoid: Político, Eleito._

### Cargo
Posto eletivo em disputa (ex.: Governador, Senador, Deputado Federal, Deputado Estadual, Presidente). Possui abrangência estadual ou nacional.
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

- **radar-eleitoral → data/candidaturas.csv**: Aplicação consome dataset tabular local estático (contrato: colunas `uf`, `cargo`, `url_g1`, `resumo`).
- **radar-eleitoral → G1 (Globo)**: Aplicação redireciona o usuário para links canônicos públicos do portal G1 via navegação web nativa (`target="_blank"`).
- **radar-eleitoral → IBGE / GeoJSON**: Renderização do mapa consome malha vetorial simplificada dos estados brasileiros em GeoJSON (<100KB).
- **radar-eleitoral → Render.com**: Deploy contínuo automatizado do container Docker gerenciado pelo Granian.
