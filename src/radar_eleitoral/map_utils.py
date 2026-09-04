"""Utilitários de geração do mapa coroplético do Brasil para o Dash."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from radar_eleitoral.mock_data import UF_NAMES

GEOJSON_PATH = Path("data/brazil_states.json")


@lru_cache(maxsize=1)
def load_brazil_geojson() -> dict[str, Any]:
    """Carrega malha GeoJSON otimizada dos estados brasileiros (<100KB, RFC 7946)."""
    if not GEOJSON_PATH.exists():
        raise FileNotFoundError(f"Arquivo GeoJSON não encontrado em {GEOJSON_PATH}")

    with open(GEOJSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def create_brazil_map(selected_uf: str, cargo: str) -> go.Figure:
    """Gera a figura interativa Plotly do mapa do Brasil na paleta Esmeralda Transparência."""
    geojson = load_brazil_geojson()

    is_presidente = cargo == "Presidente"
    selected_clean = selected_uf.upper() if selected_uf else "SP"

    records = []
    for sigla, nome in UF_NAMES.items():
        if is_presidente:
            destaque = 0.5
            status_text = "Âmbito Nacional (Presidente)"
        elif sigla == selected_clean:
            destaque = 1.0
            status_text = "Estado Ativo"
        else:
            destaque = 0.0
            status_text = "Clique para selecionar"

        records.append(
            {
                "uf": sigla,
                "nome": nome,
                "destaque": destaque,
                "status": status_text,
            }
        )

    df = pd.DataFrame(records)

    # Escala de cores Esmeralda Transparência
    if is_presidente:
        color_scale = [
            [0.0, "#064e3b"],
            [0.5, "#047857"],
            [1.0, "#059669"],
        ]
        border_color = "#34d399"
    else:
        color_scale = [
            [0.0, "#0f291e"],
            [0.1, "#1a382b"],
            [0.9, "#047857"],
            [1.0, "#10b981"],
        ]
        border_color = "#1e4a38"

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="uf",
        featureidkey="properties.sigla",
        color="destaque",
        color_continuous_scale=color_scale,
        range_color=[0.0, 1.0],
        hover_name="nome",
        hover_data={"uf": True, "destaque": False, "status": True},
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
    )

    fig.update_traces(
        marker_line_width=1.2,
        marker_line_color=border_color,
        hovertemplate=(
            "<b>%{hovertext} (%{customdata[0]})</b><br>"
            "<span style='color:#94a3b8;'>%{customdata[2]}</span>"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        uirevision="constant",
        clickmode="event",
    )

    return fig
