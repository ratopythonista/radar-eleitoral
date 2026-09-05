"""Página inicial do Radar Eleitoral - Layout Split-Screen Editorial (Esmeralda)."""

import dash
from dash import ALL, Input, Output, State, callback, ctx, dcc, html

from radar_eleitoral.candidaturas import CARGOS, HeroData, get_hero_data
from radar_eleitoral.map_utils import create_brazil_map

dash.register_page(__name__, path="/", title="Radar Eleitoral - Início")

# Estilos da paleta Esmeralda Transparência
THEME = {
    "bg_page": "bg-[#040f0c] text-slate-100",
    "card_bg": "bg-[#091a15]/85 border-emerald-900/50 shadow-black/60",
    "map_box": "border-emerald-900/40 bg-[#071510]/50",
    "header_bg": "border-emerald-950/80",
    "accent_text": "text-emerald-400",
    "badge_nacional": "bg-teal-500/15 text-teal-300 border-teal-400/30",
    "badge_uf": "bg-emerald-500/15 text-emerald-300 border-emerald-400/30",
    "badge_tag": "bg-emerald-500/20 text-emerald-300 border-emerald-400/30",
    "cta_btn": (
        "bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg "
        "shadow-emerald-950/60 ring-1 ring-emerald-400/40"
    ),
    "pill_active": ("bg-emerald-600 text-white shadow-md shadow-emerald-900/40 border-emerald-500"),
    "pill_inactive": (
        "bg-[#091a15]/80 text-slate-300 hover:bg-[#0e271f] hover:text-white border-emerald-950"
    ),
    "pill_pres_active": (
        "bg-teal-600 text-white shadow-md shadow-teal-900/40 "
        "border-teal-400 ring-2 ring-teal-400/40"
    ),
    "pill_pres_inactive": (
        "bg-[#091a15]/80 text-teal-300 hover:bg-teal-950/40 hover:text-teal-200 border-teal-900/60"
    ),
}

CLS_HERO_WRAPPER = (
    "p-5 sm:p-6 rounded-2xl backdrop-blur-sm border shadow-xl flex flex-col justify-between"
)

CLS_CARD_METRIC = "p-2.5 rounded-lg bg-black/30 border border-white/10"


def render_cargo_pills(selected_cargo: str) -> html.Div:
    """Gera o seletor de cargos com destaque especial para Presidente."""
    buttons = []
    for cargo in CARGOS:
        is_active = cargo == selected_cargo
        is_pres = cargo == "Presidente"

        if is_active:
            btn_class = THEME["pill_pres_active"] if is_pres else THEME["pill_active"]
        else:
            btn_class = THEME["pill_pres_inactive"] if is_pres else THEME["pill_inactive"]

        pad = "px-4 py-2 text-sm"

        btn_content = [html.Span(cargo, className="font-semibold")]
        if is_pres:
            badge_pres_cls = (
                "ml-1.5 text-[10px] uppercase font-bold tracking-wider "
                f"px-1.5 py-0.5 rounded border {THEME['badge_tag']}"
            )
            btn_content.append(html.Span("Nacional", className=badge_pres_cls))

        buttons.append(
            html.Button(
                btn_content,
                id={"type": "cargo-btn", "cargo": cargo},
                n_clicks=0,
                className=(
                    f"{pad} rounded-xl border font-medium transition-all "
                    f"flex items-center whitespace-nowrap {btn_class}"
                ),
            )
        )

    return html.Div(
        buttons,
        className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none",
    )


def render_hero_card(hero: HeroData) -> html.Div:
    """Renderiza o Hero Card com dados contextuais, crédito editorial e CTA estilizado."""
    badge_bg = THEME["badge_nacional"] if hero.is_nacional else THEME["badge_uf"]
    badge_label = "ÂMBITO NACIONAL" if hero.is_nacional else f"ESTADO: {hero.uf_nome} ({hero.uf})"

    cta_class = (
        "w-full inline-flex items-center justify-center gap-2 font-semibold "
        "py-3.5 px-5 rounded-xl transition-all transform hover:-translate-y-0.5 "
        f"active:translate-y-0 text-sm sm:text-base {THEME['cta_btn']}"
    )

    return html.Div(
        [
            # Header do Card com Crédito Editorial Neutro
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-2"
                            ),
                            html.Span(
                                "FONTE: G1 (AUTOMAÇÃO)",
                                className="text-[11px] font-bold text-slate-300 tracking-wider",
                            ),
                        ],
                        className="flex items-center",
                    ),
                    html.Span(
                        badge_label,
                        className=(
                            f"text-xs font-semibold px-2.5 py-0.5 rounded-full border {badge_bg}"
                        ),
                    ),
                ],
                className="flex items-center justify-between border-b border-white/10 pb-3",
            ),
            # Título da Matéria
            html.H2(
                hero.titulo,
                className="text-lg sm:text-xl font-bold text-white leading-snug mt-3 mb-2",
            ),
            # Resumo Editorial
            html.P(
                hero.resumo,
                className="text-sm text-slate-300 leading-relaxed mb-4",
            ),
            # Métricas em Mini Grid
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "Candidaturas Homologadas",
                                className="text-[11px] text-slate-400 block",
                            ),
                            html.Span(
                                f"{hero.candidaturas} concorrentes",
                                className="text-sm font-bold text-slate-100",
                            ),
                        ],
                        className=CLS_CARD_METRIC,
                    ),
                    html.Div(
                        [
                            html.Span(
                                "Cargo em Disputa",
                                className="text-[11px] text-slate-400 block",
                            ),
                            html.Span(
                                hero.cargo,
                                className="text-sm font-bold text-slate-100",
                            ),
                        ],
                        className=CLS_CARD_METRIC,
                    ),
                ],
                className="grid grid-cols-2 gap-2 mb-5",
            ),
            # Botão de Ação Primária (CTA)
            html.A(
                [
                    html.Span("Ler reportagem completa no G1", className="font-bold"),
                    html.Span("↗", className="text-lg leading-none font-bold"),
                ],
                href=hero.url_g1,
                target="_blank",
                rel="noopener noreferrer",
                className=cta_class,
            ),
            # Rodapé informativo
            html.P(
                "Link canônico do G1. Matéria jornalística gerada por automação e IA.",
                className="text-[11px] text-slate-400 text-center mt-3",
            ),
        ],
        className=f"{CLS_HERO_WRAPPER} {THEME['card_bg']}",
    )


def render_home_content(selected_cargo: str, selected_uf: str) -> html.Div:
    """Renderiza o layout do Modelo A com os dados ativos."""
    hero = get_hero_data(selected_uf, selected_cargo)
    fig = create_brazil_map(selected_uf, selected_cargo)

    box_map_cls = f"rounded-2xl border {THEME['map_box']} overflow-hidden shadow-xl"
    header_map_cls = (
        "flex items-center justify-between px-4 py-2.5 border-b border-white/10 bg-black/30"
    )
    footer_map_cls = (
        "text-[11px] text-slate-400 text-center py-2 bg-black/20 border-t border-white/10"
    )

    label_visao = (
        "Visão Nacional ativa" if selected_cargo == "Presidente" else f"Estado ativo: {selected_uf}"
    )

    return html.Div(
        [
            # Header da Página
            html.Header(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "RADAR",
                                        className=(
                                            "font-black text-xl tracking-tight mr-1.5 "
                                            f"{THEME['accent_text']}"
                                        ),
                                    ),
                                    html.H1(
                                        "Eleitoral",
                                        className=(
                                            "text-xl sm:text-2xl font-black "
                                            "tracking-tight text-white inline-block"
                                        ),
                                    ),
                                    html.Span(
                                        "BETA",
                                        className=(
                                            "ml-2 text-[10px] font-bold uppercase tracking-wider "
                                            "px-1.5 py-0.5 rounded bg-white/10 text-slate-300"
                                        ),
                                    ),
                                ],
                                className="flex items-center",
                            ),
                            html.P(
                                (
                                    "Vitrine interativa de candidaturas e "
                                    "matérias automatizadas do G1."
                                ),
                                className="text-xs sm:text-sm text-slate-400 mt-0.5",
                            ),
                        ]
                    ),
                    dcc.Link(
                        "Sobre o Projeto",
                        href="/sobre",
                        className=(
                            "text-xs sm:text-sm font-medium text-slate-400 hover:text-white "
                            "px-3 py-1.5 rounded-lg hover:bg-white/5 transition-colors "
                            "whitespace-nowrap shrink-0"
                        ),
                    ),
                ],
                className=(
                    f"flex items-center justify-between gap-4 border-b {THEME['header_bg']} pb-4 mb-6"
                ),
            ),
            # Barra de Seleção de Cargos
            html.Section(
                [
                    html.Div(
                        [
                            html.Span(
                                "Escolha o cargo:",
                                className=(
                                    "text-xs font-bold uppercase tracking-wider "
                                    "text-slate-400 block mb-2"
                                ),
                            ),
                            render_cargo_pills(selected_cargo),
                        ],
                        className="mb-6",
                    ),
                ]
            ),
            # Grid Principal Split-Screen (Desktop: 2 colunas; Mobile: empilhado)
            html.Main(
                [
                    # Coluna do Mapa (Esquerda em Desktop / 2ª em Mobile)
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "MAPA INTERATIVO DO BRASIL",
                                                className=(
                                                    "text-xs font-bold "
                                                    "text-slate-400 tracking-wider"
                                                ),
                                            ),
                                            html.Span(
                                                label_visao,
                                                className="text-xs font-medium text-slate-300",
                                            ),
                                        ],
                                        className=header_map_cls,
                                    ),
                                    dcc.Graph(
                                        id="map-graph",
                                        figure=fig,
                                        config={
                                            "displayModeBar": False,
                                            "responsive": True,
                                            "scrollZoom": False,
                                        },
                                        className="w-full h-[380px] sm:h-[480px] lg:h-[540px]",
                                    ),
                                    html.Div(
                                        (
                                            "Toque ou clique em um estado no mapa "
                                            "para ver a cobertura regional."
                                        ),
                                        className=footer_map_cls,
                                    ),
                                ],
                                className=box_map_cls,
                            ),
                        ],
                        className="order-2 lg:order-1 lg:w-7/12",
                    ),
                    # Coluna do Hero Card (Direita em Desktop / 1ª em Mobile)
                    html.Div(
                        [
                            render_hero_card(hero),
                        ],
                        className="order-1 lg:order-2 lg:w-5/12 flex flex-col justify-start",
                    ),
                ],
                className="flex flex-col lg:flex-row gap-6 mb-16",
            ),
        ],
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6",
    )


# -------------------------------------------------------------------------------------------------
# Layout Principal da Página
# -------------------------------------------------------------------------------------------------
layout = html.Div(
    [
        dcc.Store(id="store-cargo", data="Presidente"),
        dcc.Store(id="store-uf", data="SP"),
        html.Div(id="home-content-container"),
    ],
    className=f"min-h-screen {THEME['bg_page']} flex flex-col relative",
)


# -------------------------------------------------------------------------------------------------
# Callbacks de Interatividade e Sincronização
# -------------------------------------------------------------------------------------------------


@callback(
    Output("store-cargo", "data"),
    Output("store-uf", "data"),
    Input({"type": "cargo-btn", "cargo": ALL}, "n_clicks"),
    Input("map-graph", "clickData"),
    State("store-cargo", "data"),
    State("store-uf", "data"),
    prevent_initial_call=True,
)
def update_filters(
    _cargo_clicks: list[int],
    map_click_data: dict | None,
    cargo_state: str,
    uf_state: str,
) -> tuple[str, str]:
    """Gerencia seleção de cargo e clique no mapa."""
    triggered = ctx.triggered_id

    # Se foi clique em botão de cargo
    if isinstance(triggered, dict) and triggered.get("type") == "cargo-btn":
        novo_cargo = triggered.get("cargo", cargo_state)
        if novo_cargo == "Presidente":
            return "Presidente", "BR"
        return novo_cargo, uf_state if uf_state != "BR" else "SP"

    # Se foi clique no mapa
    if triggered == "map-graph" and map_click_data:
        points = map_click_data.get("points", [])
        if points:
            clicked_uf = points[0].get("location")
            if clicked_uf:
                novo_cargo = "Governador" if cargo_state == "Presidente" else cargo_state
                return novo_cargo, clicked_uf

    return cargo_state, uf_state


@callback(
    Output("home-content-container", "children"),
    Input("store-cargo", "data"),
    Input("store-uf", "data"),
)
def render_active_content(cargo: str, uf: str) -> html.Div:
    """Renderiza o conteúdo da página com o estado selecionado."""
    return render_home_content(cargo, uf)
