"""Radar Eleitoral - Ponto de entrada da aplicação Dash monolítica."""

import dash
from dash import html

CUSTOM_INDEX_STRING = """<!DOCTYPE html>
<html lang="pt-BR" class="h-full bg-[#040f0c]">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.tailwindcss.com"></script>
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
    __name__,
    use_pages=True,
    pages_folder="pages",
    title="Radar Eleitoral | Cobertura de Candidaturas",
    update_title="Carregando...",
    meta_tags=GLOBAL_META_TAGS,
    index_string=CUSTOM_INDEX_STRING,
    suppress_callback_exceptions=True,
)

server = app.server

app.layout = html.Div(
    [
        dash.page_container,
    ],
    className="min-h-full flex flex-col bg-[#040f0c]",
)

if __name__ == "__main__":
    app.run(debug=True)
