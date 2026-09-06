"""Componente de Cartograma Regional e regras de seleção de UFs."""

from typing import Final

from dash import html

from radar_eleitoral.candidaturas import UF_NAMES

# Divisão oficial das 27 Unidades da Federação pelas 5 Macrorregiões do Brasil
REGIOES_BRASIL: Final[dict[str, list[str]]] = {
    "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"],
}

# Estilos reutilizáveis do tema Esmeralda Transparência
CLS_REGION_BOX = "p-3 rounded-xl bg-black/30 border border-white/10 flex flex-col justify-start"
CLS_REGION_TITLE = "text-[11px] font-bold text-emerald-400/90 uppercase tracking-wider mb-2 flex items-center gap-1.5"


def resolve_smart_selection(clicked_uf: str, current_cargo: str) -> tuple[str, str]:
    """Resolve a seleção inteligente ao clicar em uma UF ou no botão nacional.

    Regras:
    - Clicar em 'BR' seleciona o cargo 'Presidente'.
    - Se 'Presidente' estiver ativo e uma UF for clicada, migra para 'Deputado Distrital' (se DF) ou 'Governador'.
    - Se 'Deputado Estadual' estiver ativo e DF for clicado, migra para 'Deputado Distrital'.
    - Se 'Deputado Distrital' estiver ativo e outra UF for clicada, migra para 'Deputado Estadual'.
    - Em outros cenários, preserva o cargo atual e atualiza a UF.
    """
    uf_clean = clicked_uf.strip().upper()

    if uf_clean == "BR":
        return "Presidente", "BR"

    target_cargo = current_cargo
    if current_cargo == "Presidente":
        target_cargo = "Deputado Distrital" if uf_clean == "DF" else "Governador"
    elif current_cargo == "Deputado Estadual" and uf_clean == "DF":
        target_cargo = "Deputado Distrital"
    elif current_cargo == "Deputado Distrital" and uf_clean != "DF":
        target_cargo = "Deputado Estadual"

    return target_cargo, uf_clean


def resolve_cargo_selection(new_cargo: str, current_uf: str) -> tuple[str, str]:
    """Resolve transição ao selecionar um novo cargo."""
    if new_cargo == "Presidente":
        return "Presidente", "BR"
    if new_cargo == "Deputado Distrital":
        return "Deputado Distrital", "DF"
    if new_cargo == "Deputado Estadual" and current_uf == "DF":
        return "Deputado Estadual", "SP"
    return new_cargo, current_uf if current_uf != "BR" else "SP"


def render_nacional_button(selected_cargo: str) -> html.Button:
    """Renderiza o botão compacto 'Brasil (Nacional)' para o Cartograma."""
    is_active = selected_cargo == "Presidente"

    active_cls = (
        "bg-gradient-to-r from-emerald-600 to-emerald-500 text-white border-emerald-400 "
        "shadow-[0_0_12px_rgba(52,211,153,0.3)]"
    )
    inactive_cls = (
        "bg-[#0a261e] text-slate-300 border-white/10 hover:border-emerald-600/40 hover:bg-[#103a2e]"
    )

    style_cls = active_cls if is_active else inactive_cls

    badge_status = (
        html.Span(
            "ATIVO",
            className=(
                "ml-2 text-[9px] font-black uppercase tracking-widest px-1.5 py-0.5 "
                "rounded bg-emerald-950 text-emerald-300 border border-emerald-400/40"
            ),
        )
        if is_active
        else None
    )

    return html.Button(
        [
            html.Span("🇧🇷", className="text-sm mr-2 select-none"),
            html.Span("Brasil (Âmbito Nacional)", className="font-bold text-xs"),
            badge_status,
        ],
        id={"type": "cartograma-uf-btn", "index": "BR"},
        n_clicks=0,
        className=(
            f"w-full py-2 px-3 rounded-lg border font-medium transition-all duration-150 "
            f"flex items-center justify-center cursor-pointer {style_cls}"
        ),
    )


def render_cartograma_regional(selected_uf: str, selected_cargo: str) -> html.Div:
    """Gera o painel contínuo das 5 macrorregiões com as 27 UFs para seleção tátil rápida."""
    is_pres = selected_cargo == "Presidente"
    selected_clean = selected_uf.strip().upper() if selected_uf else "SP"

    region_cards = []
    for regiao, ufs in REGIOES_BRASIL.items():
        buttons = []
        for uf in ufs:
            is_active = not is_pres and uf == selected_clean
            uf_nome = UF_NAMES.get(uf, uf)

            if is_active:
                btn_cls = (
                    "bg-gradient-to-br from-emerald-500 to-emerald-600 text-white "
                    "border-emerald-300 shadow-[0_0_12px_rgba(52,211,153,0.4)] scale-105 z-10"
                )
            else:
                btn_cls = (
                    "bg-[#0a261e] hover:bg-[#103a2e] text-slate-200 border-emerald-800/30 "
                    "hover:border-emerald-500/40"
                )

            buttons.append(
                html.Button(
                    [
                        html.Span(uf, className="font-black text-xs sm:text-sm tracking-wide"),
                    ],
                    id={"type": "cartograma-uf-btn", "index": uf},
                    title=f"{uf_nome} ({uf})",
                    n_clicks=0,
                    className=(
                        f"px-2.5 py-1.5 sm:px-3 sm:py-2 rounded-lg border font-bold text-center "
                        f"transition-all duration-150 cursor-pointer min-w-[40px] sm:min-w-[44px] {btn_cls}"
                    ),
                )
            )

        region_cards.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(regiao, className="font-extrabold"),
                            html.Span(
                                f"({len(ufs)})", className="text-[10px] text-slate-400 font-normal"
                            ),
                        ],
                        className=CLS_REGION_TITLE,
                    ),
                    html.Div(buttons, className="flex flex-wrap gap-1.5 sm:gap-2"),
                ],
                className=CLS_REGION_BOX,
            )
        )

    return html.Div(
        [
            # Botão de âmbito nacional integrado de forma limpa no topo do Cartograma
            html.Div(
                render_nacional_button(selected_cargo),
                className="mb-3",
            ),
            # Grade responsiva das macrorregiões
            html.Div(
                region_cards,
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3",
            ),
        ],
        className="w-full select-none",
    )


def render_view_toggle(active_view: str) -> html.Div:
    """Renderiza o seletor [ 🗺️ Mapa | 🧭 Grade Regional ] para o layout Desktop."""
    is_mapa = active_view == "mapa"

    active_cls = "bg-emerald-500 text-black font-bold border-emerald-400 shadow-sm"
    inactive_cls = (
        "bg-black/30 text-slate-400 hover:text-slate-200 border-transparent hover:bg-white/5"
    )

    cls_mapa = active_cls if is_mapa else inactive_cls
    cls_grade = inactive_cls if is_mapa else active_cls

    return html.Div(
        [
            html.Button(
                [
                    html.Span("🗺️", className="mr-1 text-xs select-none"),
                    html.Span("Mapa"),
                ],
                id="btn-view-mapa",
                n_clicks=0,
                className=f"px-2.5 py-1 rounded-md text-[11px] border transition-all cursor-pointer {cls_mapa}",
            ),
            html.Button(
                [
                    html.Span("🧭", className="mr-1 text-xs select-none"),
                    html.Span("Grade Regional"),
                ],
                id="btn-view-grade",
                n_clicks=0,
                className=f"px-2.5 py-1 rounded-md text-[11px] border transition-all cursor-pointer {cls_grade}",
            ),
        ],
        className="flex items-center p-0.5 rounded-lg bg-black/40 border border-white/10 gap-1",
    )
