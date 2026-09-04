"""Radar Eleitoral - Ponto de entrada da aplicação Dash monolítica."""

import dash
from dash import html

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    title="Radar Eleitoral",
    update_title="Carregando...",
    suppress_callback_exceptions=True,
)

server = app.server

app.layout = html.Div(
    [
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
