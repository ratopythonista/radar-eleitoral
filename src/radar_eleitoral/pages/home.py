"""Página inicial do Radar Eleitoral."""

import dash
from dash import html

dash.register_page(__name__, path="/", title="Radar Eleitoral - Início")

layout = html.Div(
    [
        html.H1("Radar Eleitoral", className="text-2xl font-bold"),
        html.P("Vitrine interativa de candidaturas e matérias automatizadas do G1."),
    ],
    className="p-4",
)
