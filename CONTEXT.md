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
Mecanismo voluntário de doação de apoiadores via Pix (QR Code) ou Buy Me a Coffee na página `/sobre`.
_Avoid: Cobrança, Assinatura, Paywall._

## Dependências

- **radar-eleitoral → data/candidaturas.csv**: Aplicação consome dataset tabular local estático (contrato: colunas `uf`, `cargo`, `url_g1`, `resumo`).
- **radar-eleitoral → G1 (Globo)**: Aplicação redireciona o usuário para links canônicos públicos do portal G1 via navegação web nativa (`target="_blank"`).
- **radar-eleitoral → IBGE / GeoJSON**: Renderização do mapa consome malha vetorial simplificada dos estados brasileiros em GeoJSON (<100KB).
- **radar-eleitoral → Render.com**: Deploy contínuo automatizado do container Docker gerenciado pelo Granian.
