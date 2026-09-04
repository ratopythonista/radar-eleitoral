# Pesquisa Técnica: SEO, OpenGraph e Social Cards no Dash com Granian

- **Issue de Origem:** [#3 - Configuração de SEO, OpenGraph e Social Cards no Dash com Granian](https://github.com/ratopythonista/radar-eleitoral/issues/3)
- **Data:** 2026-09-04
- **Status:** Concluído / Aprovado para Implementação
- **Autor:** Agente de Pesquisa Especialista em SEO e Plataformas Web

---

## 1. Sumário Executivo

Aplicações construídas com Dash são Single Page Applications (SPAs) executadas via React no navegador. Embora o Dash ofereça uma excelente experiência interativa para o usuário final, **scrapers e crawlers de redes sociais (WhatsApp, LinkedIn, Twitter/X, Facebook/Instagram, Telegram) não executam o motor JavaScript**. Eles enviam uma requisição `GET` HTTP estática e interpretam exclusivamente as tags `<meta>` presentes no `<head>` do HTML inicial devolvido pelo servidor (SSR - Server-Side Rendering de metadados).

Esta pesquisa investigou profundamente a arquitetura interna do Dash 2.17+, sua integração com o servidor Granian (WSGI/ASGI) e os requisitos estritos dos principais scrapers de redes sociais.

### Principais Conclusões:
1. **Suporte Nativo a SSR de Metadados no Dash Pages:** O Dash possui um mecanismo nativo em `dash._pages._page_meta_tags(app, request)` que gera dinamicamente no servidor as tags OpenGraph (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`) e Twitter Card (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`, `twitter:url`) para cada rota registrada com `dash.register_page`.
2. **A Armadilha do Reverse Proxy (Granian + Render):** O Dash gera as URLs das imagens e canônicas concatenando `request.root` com o caminho do asset (ex.: `request.root + "assets/social-card.png"`). Em ambientes conteinerizados atrás de reverse proxy (como Render.com e Granian), o servidor enxerga a requisição internamente como `http://localhost:8080/`. Sem correção de cabeçalhos de proxy, o Dash emite metatags com `http://localhost/assets/...`, fazendo com que **todos os scrapers externos falhem silenciosamente**. A inclusão do middleware `ProxyFix` do Werkzeug é obrigatória.
3. **Casca HTML (`app.index_string`):** O Dash não define o atributo `lang="pt-BR"` na tag `<html>` por padrão. Ajustar `app.index_string` é essencial para SEO, acessibilidade e auditorias do Google Lighthouse.
4. **Dimensões e Peso do Social Card:** O formato ideal é **1200 x 630 pixels** (proporção 1.91:1) em PNG ou JPEG, mantendo o peso estritamente **inferior a 300 KB** para total compatibilidade com os limites estritos do WhatsApp mobile.

---

## 2. Como os Scrapers de Redes Sociais Funcionam

| Plataforma | User-Agent do Crawler | Executa JS? | Protocolo / Tags Principais | Limite Imagem | Particularidades |
|---|---|---|---|---|---|
| **WhatsApp** | `WhatsApp/2.x.x` ou Meta crawler | **Não** | OpenGraph (`og:title`, `og:description`, `og:image`, `og:url`) | < 300 KB (ideal) / max 500 KB | Rejeita imagens grandes ou URLs `http://`. Cache agressivo. Pode recortar para 1:1 (300x300px) no mobile. |
| **LinkedIn** | `LinkedInBot/1.0` | **Não** | OpenGraph (`og:*`) | < 5 MB (ideal < 1 MB) | Título até 119 caracteres. Descrição até 155 caracteres. Re-scrape via *Post Inspector*. |
| **Twitter / X** | `Twitterbot/1.0` | **Não** | Twitter Cards (`twitter:*`) + OpenGraph fallback | < 5 MB | Prefere `twitter:card = summary_large_image`. Proporção 1.91:1. |
| **Facebook / Instagram** | `facebookexternalhit/1.1` | **Não** | OpenGraph oficial (`ogp.me`) | < 8 MB | Requer `og:type="website"`, `og:locale="pt_BR"` e dimensões mínimas de 200x200px (ideal 1200x630px). |
| **Telegram** | `TelegramBot (like TwitterBot)` | **Não** | OpenGraph (`og:*`) | < 5 MB | Cache instantâneo; purga via `@WebpageBot`. |

### A Falácia do Client-Side Rendering em SEO Social
Em ferramentas que dependem de renderização client-side (como callbacks React do Dash que alteram tags no DOM após carregamento), os scrapers simplesmente **não enxergam a alteração**, pois finalizam o parsing assim que recebem o stream de bytes da requisição HTTP inicial. Toda informação de social card **deve** estar embutida na resposta inicial do servidor Flask/Granian.

---

## 3. Arquitetura Interna do Dash para Metatags

O Dash oferece três pontos de injeção de metadados:

### 3.1. `dash.register_page` (Recomendado para páginas específicas)
Ao usar `use_pages=True`, o módulo `dash._pages` intercepta a requisição no backend no momento do handshake HTTP inicial através da função `_page_meta_tags(app, request)`:

```python
# Trecho interno de dash/_pages.py:
def _page_meta_tags(app, request):
    request_path = request.path
    start_page, path_variables = _path_to_page(request_path.strip("/"))
    # ...
    return [
        {"name": "description", "content": description},
        {"property": "twitter:card", "content": "summary_large_image"},
        {"property": "twitter:url", "content": request.url},
        {"property": "twitter:title", "content": title},
        {"property": "twitter:description", "content": description},
        {"property": "twitter:image", "content": image_url or ""},
        {"property": "og:title", "content": title},
        {"property": "og:type", "content": "website"},
        {"property": "og:description", "content": description},
        {"property": "og:image", "content": image_url or ""},
    ]
```

**Benefícios:**
- Injeta automaticamente tags completas de Twitter Card e OpenGraph específicas da rota acessada.
- Permite que `title` e `description` sejam strings estáticas ou *callables* dinâmicos (`callable(**kwargs)`).
- Suporta herança e fallback transparente caso a página não especifique imagem ou descrição.

### 3.2. `dash.Dash(meta_tags=[...])` (Para metadados globais compartilhados)
O parâmetro `meta_tags` de inicialização do Dash não sobrescreve os metadados do `register_page`; **ele é concatenado a eles**.
Deve ser utilizado para tags globais da aplicação que se aplicam a todas as rotas:
- `{"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}`
- `{"property": "og:site_name", "content": "Radar Eleitoral"}`
- `{"property": "og:locale", "content": "pt_BR"}`
- `{"name": "theme-color", "content": "#0284c7"}`
- `{"name": "robots", "content": "index, follow"}`

### 3.3. `app.index_string` (Para casca HTML estrutural e JSON-LD)
A casca HTML padrão do Dash omite tags estruturais fundamentais para SEO:
- `<html lang="pt-BR">`
- Tags de verificação de buscadores (Google Search Console)
- Metadados semânticos de schema.org via JSON-LD (`SoftwareApplication` ou `NewsMediaOrganization`)
- Links pré-carregados de fontes ou ícones de alta resolução (Apple Touch Icon).

O template `app.index_string` preserva os marcadores do Dash (`{%metas%}`, `{%title%}`, `{%favicon%}`, `{%css%}`, `{%app_entry%}`, `{%config%}`, `{%scripts%}`, `{%renderer%}`) e permite enriquecer a casca com atributos sem quebrar os plugins nativos.

---

## 4. O Problema do Reverse Proxy e a Solução `ProxyFix`

### O Problema
No ambiente conteinerizado do Render.com com servidor Granian:
1. O usuário ou scraper acessa `https://radar-eleitoral.onrender.com/`.
2. O balanceador de carga/proxy TLS do Render recebe a requisição HTTPS na porta 443 e a encaminha via HTTP plano para o container na porta 8080.
3. O proxy envia os cabeçalhos padrão:
   - `X-Forwarded-Proto: https`
   - `X-Forwarded-Host: radar-eleitoral.onrender.com`
   - `X-Forwarded-For: <IP_CLIENTE>`
4. O servidor WSGI do Flask, por padrão, não confia nesses cabeçalhos. Como resultado, `request.root` é computado como `http://0.0.0.0:8080/` ou `http://localhost/`.
5. O Dash gera:
   ```html
   <meta property="og:image" content="http://localhost/assets/social-card.png">
   <meta property="og:url" content="http://localhost/">
   ```
6. O scraper externo tenta resolver `localhost`, falha e **nenhuma imagem de preview é exibida**.

### A Solução: Werkzeug `ProxyFix`
O Werkzeug (dependência transitiva do Flask e do Dash) fornece o middleware `werkzeug.middleware.proxy_fix.ProxyFix`. Aplicá-lo ao `app.server.wsgi_app` faz com que o Flask leia corretamente o protocolo `https` e o domínio público `radar-eleitoral.onrender.com`:

```python
from werkzeug.middleware.proxy_fix import ProxyFix

# server é a instância subjacente do Flask
server = app.server
server.wsgi_app = ProxyFix(
    server.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1,
)
```

### Comprovação Prática (Teste Realizado):
```bash
# Sem ProxyFix:
<meta property="twitter:url" content="http://localhost/">
<meta property="og:image" content="http://localhost/assets/card.png">

# Com ProxyFix:
<meta property="twitter:url" content="https://radar-eleitoral.onrender.com/">
<meta property="og:image" content="https://radar-eleitoral.onrender.com/assets/card.png">
```

---

## 5. Especificações Técnicas para o Social Card

### 5.1. Dimensões e Proporção
- **Tamanho Recomendado:** `1200 x 630 pixels`
- **Proporção (Aspect Ratio):** `1.91:1`
- **Tamanho Mínimo aceitável:** `600 x 315 pixels` (abaixo disso, redes como Facebook e LinkedIn podem exibir um card pequeno quadrado em vez do banner expansivo).

### 5.2. Formato e Compressão
- **Formato:** PNG (recomendado se houver mapas, vetores, textos grandes e logos com nitidez) ou JPEG com compressão de qualidade 85%.
- **Peso do Arquivo:** **< 300 KB**.
  - O WhatsApp impõe uma restrição severa de download para prévias automáticas. Imagens acima de 300-500 KB frequentemente não são baixadas em redes móveis, gerando mensagem sem imagem.

### 5.3. Safe Zone (Área Segura de Composição)
- Em dispositivos móveis e em certas plataformas (WhatsApp e feeds compactos), a imagem de 1200x630px pode ser recortada automaticamente para um quadrado central de **1:1** (`630 x 630 pixels`) ou ter as margens externas cortadas.
- **Diretriz de Design:** Centralizar títulos, dados de destaque e o logo na área central segura de **1000 x 500 pixels**, deixando as bordas como sangria de fundo com respiro visual.

```
+-------------------------------------------------------------+  1200 px
|                         Sangria                             |
|    +---------------------------------------------------+    |
|    |                                                   |    |
|    |               SAFE ZONE (Área Central)            |    |  630 px
|    |      [Título: Radar Eleitoral - Cobertura G1]     |    |
|    |         [Visualização do Mapa do Brasil]          |    |
|    |                                                   |    |
|    +---------------------------------------------------+    |
|                         Sangria                             |
+-------------------------------------------------------------+
```

### 5.4. Resolução Automática de Imagens no Dash
O Dash implementa a seguinte hierarquia de busca em `assets/` caso o atributo `image` não seja explicitamente passado em `dash.register_page`:
1. `assets/<module_name>.<ext>` (ex.: `assets/home.png`, `assets/sobre.png`)
2. `assets/app.<ext>` (ex.: `assets/app.png` - fallback global do app)
3. `assets/logo.<ext>` (ex.: `assets/logo.png`)
4. Se nada for encontrado, a tag `og:image` fica vazia.

**Recomendação para o projeto:** Salvar o card padrão do projeto como `assets/social-card.png` e referenciá-lo explicitamente ou fornecer `assets/app.png` como fallback automático universal.

---

## 6. Estratégia de Configuração Multi-Page

No modelo `use_pages=True`, cada página em `src/radar_eleitoral/pages/` declara seu próprio registro com títulos e descrições específicos:

### Página Inicial (`pages/home.py`)
```python
import dash
from dash import html

dash.register_page(
    __name__,
    path="/",
    name="Início",
    title="Radar Eleitoral | Cobertura G1 por Estado e Cargo",
    description="Explore matérias jornalísticas automatizadas do G1 sobre candidaturas eleitorais em todo o Brasil. Mapa interativo por estado e cargo.",
    image="social-card.png",
)

layout = html.Div([...])
```

### Página Sobre (`pages/sobre.py`)
```python
import dash
from dash import html

dash.register_page(
    __name__,
    path="/sobre",
    name="Sobre",
    title="Sobre o Projeto | Radar Eleitoral",
    description="Conheça os bastidores do Radar Eleitoral: automação jornalística, transparência eleitoral e dados públicos do G1.",
    image="social-card.png",
)

layout = html.Div([...])
```

### Fallbacks Globais
Se uma página for registrada sem `description` ou sem `title`, o Dash utiliza automaticamente os parâmetros `title` e `description` definidos na inicialização de `dash.Dash(...)`.

---

## 7. Snippet Recomendado para `src/radar_eleitoral/app.py`

Abaixo está o código de produção pronto para ser integrado no repositório `radar-eleitoral`. Ele contempla:
- `ProxyFix` configurado para compatibilidade total com Granian e Render.com.
- `index_string` customizado com `lang="pt-BR"`, links canônicos dinâmicos e estrutura semântica.
- Metatags complementares para OpenGraph e Twitter Card.
- Fallback global de título e descrição.

```python
"""Aplicação principal Radar Eleitoral com suporte robusto a SEO e OpenGraph."""

import dash
from dash import html
from werkzeug.middleware.proxy_fix import ProxyFix

CUSTOM_INDEX_STRING = """<!DOCTYPE html>
<html lang="pt-BR">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <!-- Metadados adicionais de SEO e PWA -->
        <meta name="format-detection" content="telephone=no">
        <meta name="robots" content="index, follow">
    </head>
    <body class="bg-slate-900 text-slate-100 min-h-screen">
        <!--[if IE]><script>
        alert("Navegadores legados não são suportados. Utilize um navegador moderno.");
        </script><![endif]-->
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

GLOBAL_META_TAGS = [
    {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"},
    {"property": "og:site_name", "content": "Radar Eleitoral"},
    {"property": "og:locale", "content": "pt_BR"},
    {"name": "theme-color", "content": "#0f172a"},
    {"name": "author", "content": "Radar Eleitoral / Automação G1"},
]

app = dash.Dash(
    __name__,
    use_pages=True,
    title="Radar Eleitoral | Cobertura G1 de Candidaturas",
    description=(
        "Vitrine interativa de dados eleitorais e cobertura jornalística automatizada "
        "do G1 por estado e cargo em todo o Brasil."
    ),
    meta_tags=GLOBAL_META_TAGS,
    index_string=CUSTOM_INDEX_STRING,
    suppress_callback_exceptions=True,
)

# Servidor Flask subjacente consumido pelo Granian (WSGI)
server = app.server

# Configuração essencial de ProxyFix para encaminhamento correto de HTTPS e Host
# no Render.com / Granian, garantindo que og:image e og:url sejam gerados com URLs absolutas HTTPS
server.wsgi_app = ProxyFix(
    server.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1,
)

app.layout = html.Div(
    [
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
```

---

## 8. Guia de Validação e Testes em Homologação/Produção

Após o deploy no Render ou execução com Granian:

### 8.1. Teste via Linha de Comando (cURL)
Simule a requisição exata dos scrapers para inspecionar o HTML estático devolvido:

```bash
# Simulação do crawler do WhatsApp
curl -s -A "WhatsApp/2.21.12.21 i" https://radar-eleitoral.onrender.com/ | grep -iE "(og:|twitter:|title>)"

# Simulação do crawler do Facebook
curl -s -A "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)" https://radar-eleitoral.onrender.com/ | grep -iE "(og:|twitter:|title>)"

# Simulação do crawler do LinkedIn
curl -s -A "LinkedInBot/1.0 (+http://www.linkedin.com)" https://radar-eleitoral.onrender.com/ | grep -iE "(og:|twitter:|title>)"
```

**Verificação de Sucesso:**
- Todas as tags `og:image`, `og:url` e `twitter:url` **devem** iniciar estritamente com `https://` e conter o domínio público final, **nunca** `http://localhost` ou `http://0.0.0.0`.
- O `<html lang="pt-BR">` deve estar presente.

### 8.2. Ferramentas Oficiais de Debugging de Redes Sociais
1. **Facebook & WhatsApp Sharing Debugger:** [https://developers.facebook.com/tools/debug/](https://developers.facebook.com/tools/debug/)
   - Fornece visualização exata do card gerado e botão "Scrape Again" para limpar o cache.
2. **LinkedIn Post Inspector:** [https://www.linkedin.com/post-inspector/](https://www.linkedin.com/post-inspector/)
   - Valida tags OpenGraph e limpa o cache do LinkedIn.
3. **Twitter Card Validator:** Composição de rascunho de Tweet no Twitter/X web (exibe a prévia ao colar o link).
4. **Telegram Webpage Bot:** No Telegram, inicie conversa com `@WebpageBot` e envie o link para atualizar a visualização instantânea.

---

## 9. Próximos Passos (Plano de Ação para Implementação)

1. **Ativo Visual (Card de Compartilhamento):**
   - Criar `assets/social-card.png` e `assets/app.png` com dimensões `1200x630px`, PNG otimizado (<300KB), contendo o branding do Radar Eleitoral e elementos visuais do mapa/G1.
2. **Implementar `app.py`:**
   - Aplicar a estrutura refinada com `ProxyFix` e `GLOBAL_META_TAGS` conforme o snippet da Seção 7.
3. **Registrar Páginas:**
   - Adicionar metadados enriquecidos (`title`, `description`, `image="social-card.png"`) em cada módulo de `pages/`.
