# 0001. Cartograma Regional, Bifurcação Mobile e Otimização de Performance

## Contexto

A aplicação apresentava dois problemas críticos de experiência do usuário em produção:
1. **Tempo de carregamento excessivo no Render.com (free tier)**: Containers hibernavam após 15 minutos de inatividade (cold start de 50 a 90 segundos). Além disso, a inclusão do compilador JavaScript em tempo de execução (`cdn.tailwindcss.com`) e o bundle do Dash com Plotly.js (~3.5 MB) penalizavam conexões móveis.
2. **Ergonomia tátil e mira do mapa geográfico no mobile e desktop**: O mapa coroplético tradicional (`px.choropleth` com GeoJSON) gerava polígonos microscópicos para estados de menor extensão territorial (especialmente Distrito Federal, Sergipe, Alagoas, Paraíba e Rio Grande do Norte), provocando erros de clique ("fat-finger") e conflitos de gesto entre rolagem da página e arrasto do gráfico no smartphone.

## Decisão

1. **Bifurcação de Interface**:
   - **Mobile (<1024px)**: Exclusão total do mapa coroplético do Plotly. Uso exclusivo do **Cartograma por Macrorregião** (painel contínuo organizado pelas 5 macrorregiões oficiais do Brasil), com alvos de toque confortáveis e todas as 27 UFs visíveis em menos de 280px de altura.
   - **Desktop (≥1024px)**: Disponibilização de um seletor no cabeçalho do componente (`[ 🗺️ Mapa | 🧭 Grade Regional ]`) com preferência persistida em `localStorage`. O mapa permanece como padrão visual inicial, mas o usuário pode alternar para a grade para selecionar com precisão estados pequenos como o DF.
2. **Fluxo de Filtro e Escopo Presidencial**:
   - Reordenação da hierarquia móvel para `Cargo → UF → Hero Card`.
   - Adição do botão explícito "🇧🇷 Brasil (Nacional)" para o cargo de Presidente. Ao clicar em uma UF com Presidente ativo, a interface efetua troca inteligente automática para Governador (ou Deputado Distrital se DF).
3. **Mitigação de Infraestrutura e Assets**:
   - Implementação de um endpoint leve `/healthz` no servidor Flask/Granian para pings periódicos de serviços externos de keep-alive (evitando o cold start).
   - Eliminação do script do Tailwind CDN em favor de folha de estilos estática compilada localmente em `assets/`.

## Opções Consideradas

- **Substituição total do mapa pelo cartograma em todas as telas**: Rejeitada para manter o apelo cartográfico institucional no desktop.
- **Migração para site estático (Astro/Next.js)**: Rejeitada para preservar a arquitetura e a vitrine em Python/Dash especificada no projeto.
- **Abas horizontais de macrorregião no mobile**: Rejeitada em favor do painel contínuo para evitar cliques adicionais para trocar de região.

## Consequências

- **Positivas**: Eliminação do atrito de toque no mobile, resolução definitiva da seleção do DF em qualquer tela, redução drástica do tempo de resposta percebido e prevenção da hibernação do servidor.
- **Trade-off**: Manutenção de dois componentes de seleção geográfica (o mapa Plotly e a grade de botões HTML/CSS) sincronizados pelo mesmo `dcc.Store` de estado.
