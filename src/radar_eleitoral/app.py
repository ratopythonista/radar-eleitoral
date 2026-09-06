"""Radar Eleitoral - Ponto de entrada da aplicação Dash monolítica."""

import dash
from dash import html
from werkzeug.middleware.proxy_fix import ProxyFix

CUSTOM_INDEX_STRING = """<!DOCTYPE html>
<html lang="pt-BR" class="h-full bg-[#040f0c]">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <link rel="icon" type="image/png" sizes="32x32" href="/assets/icon-32.png">
        <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
        <link rel="apple-touch-icon" href="/assets/icon-192.png">
        <link rel="manifest" href="/assets/manifest.json">
        {%css%}
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="format-detection" content="telephone=no">
        <meta name="robots" content="index, follow">
        <style>
            .choroplethlocation {
                pointer-events: all !important;
                cursor: pointer !important;
                transition: filter 0.15s ease, opacity 0.15s ease;
            }
            .choroplethlocation:hover {
                filter: brightness(1.25) drop-shadow(0 0 6px rgba(110,231,183,0.4)) !important;
                opacity: 0.95;
            }
        </style>
        <script>
            document.addEventListener('click', function(e) {
                var target = e.target;
                var path = target && target.closest ? target.closest('.choroplethlocation') : null;
                if (!path || !path.__data__) return;
                var loc = path.__data__.loc;
                if (!loc) return;
                var mapEl = document.querySelector('#map-graph');
                if (!mapEl) return;
                var gd = mapEl.querySelector('.js-plotly-plot') || mapEl;
                if (gd && typeof gd.emit === 'function') {
                    gd.emit('plotly_click', {
                        points: [{
                            location: loc,
                            pointNumber: path.__data__.index || 0,
                            pointIndex: path.__data__.index || 0,
                            customdata: [loc, 0, path.__data__.htx || '']
                        }]
                    });
                }
            });
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                    navigator.serviceWorker.register('/assets/sw.js').catch(function() {});
                });
            }
        </script>
    </head>
    <body class="h-full bg-[#040f0c] text-slate-100 antialiased">
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
    {"name": "theme-color", "content": "#040f0c"},
]

app = dash.Dash(
    "radar_eleitoral",
    use_pages=True,
    title="Radar Eleitoral | Cobertura de Candidaturas",
    description=(
        "Vitrine interativa de candidaturas e matérias jornalísticas automatizadas "
        "do G1 por estado e cargo em todo o Brasil."
    ),
    update_title="Carregando...",
    meta_tags=GLOBAL_META_TAGS,
    index_string=CUSTOM_INDEX_STRING,
    suppress_callback_exceptions=True,
)

server = app.server

# Configuração de ProxyFix essencial para o Render.com e Granian:
# Garante URLs absolutas HTTPS em og:image, og:url e canonical quando atrás de reverse proxy
server.wsgi_app = ProxyFix(  # type: ignore[method-assign]
    server.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1,
)


@server.route("/healthz")
def healthz() -> tuple[str, int, dict[str, str]]:
    """Health check endpoint ultra-leve para pings de keep-alive externos."""
    return "OK", 200, {"Content-Type": "text/plain; charset=utf-8"}


app.layout = html.Div(
    [
        dash.page_container,
    ],
    className="min-h-full flex flex-col bg-[#040f0c]",
)

if __name__ == "__main__":
    app.run(debug=True)
