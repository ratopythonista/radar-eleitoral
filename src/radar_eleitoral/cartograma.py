"""Componente de Cartograma Regional e regras de seleção de UFs para FastHTML."""

from typing import Final

from fasthtml import common as fh

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

    Regras editoriais:
    1. Clicar em 'BR' seleciona 'Presidente' e escopo 'BR'.
    2. Clicar em qualquer UF com 'Presidente' ativo faz fallback automático para 'Governador'
       (ou 'Deputado Distrital' caso a UF seja o DF).
    3. Clicar no DF estando em 'Deputado Estadual' troca para 'Deputado Distrital'.
    4. Clicar em qualquer outro estado estando em 'Deputado Distrital' troca para 'Deputado Estadual'.
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

    return new_cargo, current_uf if current_uf != "BR" else "SP"


def render_nacional_button(selected_cargo: str, desktop_view: str = "grade") -> fh.FT:
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
        fh.Span(
            "ATIVO",
            cls=(
                "ml-2 text-[9px] font-black uppercase tracking-widest px-1.5 py-0.5 "
                "rounded bg-emerald-950 text-emerald-300 border border-emerald-400/40"
            ),
        )
        if is_active
        else None
    )

    return fh.Button(
        fh.Span("🇧🇷", cls="text-sm mr-2 select-none"),
        fh.Span("Brasil (Âmbito Nacional)", cls="font-bold text-xs"),
        badge_status,
        id="cartograma-uf-btn-BR",
        cls=(
            f"w-full py-2 px-3 rounded-lg border font-medium transition-all duration-150 "
            f"flex items-center justify-center cursor-pointer {style_cls}"
        ),
        hx_get=f"/candidaturas?uf=BR&cargo=Presidente&desktop_view={desktop_view}",
        hx_target="#radar-content",
        hx_swap="outerHTML",
        hx_push_url=f"/?uf=BR&cargo=Presidente&desktop_view={desktop_view}",
    )


def render_cartograma_regional(
    selected_uf: str, selected_cargo: str, desktop_view: str = "grade"
) -> fh.FT:
    """Gera o painel contínuo das 5 macrorregiões com as 27 UFs para seleção tátil rápida."""
    is_pres = selected_cargo == "Presidente"
    selected_clean = selected_uf.strip().upper() if selected_uf else "SP"

    region_cards = []
    for regiao, ufs in REGIOES_BRASIL.items():
        buttons = []
        for uf in ufs:
            is_active = not is_pres and uf == selected_clean
            uf_nome = UF_NAMES.get(uf, uf)

            target_cargo, target_uf = resolve_smart_selection(uf, selected_cargo)

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
                fh.Button(
                    fh.Span(uf, cls="font-black text-xs sm:text-sm tracking-wide"),
                    id=f"cartograma-uf-btn-{uf}",
                    title=f"{uf_nome} ({uf})",
                    cls=(
                        f"px-2.5 py-1.5 sm:px-3 sm:py-2 rounded-lg border font-bold text-center "
                        f"transition-all duration-150 cursor-pointer min-w-[40px] sm:min-w-[44px] {btn_cls}"
                    ),
                    hx_get=f"/candidaturas?uf={target_uf}&cargo={target_cargo}&desktop_view={desktop_view}",
                    hx_target="#radar-content",
                    hx_swap="outerHTML",
                    hx_push_url=f"/?uf={target_uf}&cargo={target_cargo}&desktop_view={desktop_view}",
                )
            )

        region_cards.append(
            fh.Div(
                fh.Div(
                    fh.Span(regiao, cls="font-extrabold"),
                    fh.Span(f"({len(ufs)})", cls="text-[10px] text-slate-400 font-normal"),
                    cls=CLS_REGION_TITLE,
                ),
                fh.Div(*buttons, cls="flex flex-wrap gap-1.5 sm:gap-2"),
                cls=CLS_REGION_BOX,
            )
        )

    return fh.Div(
        # Botão de âmbito nacional integrado de forma limpa no topo do Cartograma
        fh.Div(render_nacional_button(selected_cargo, desktop_view), cls="mb-3"),
        # Grade responsiva das macrorregiões
        fh.Div(*region_cards, cls="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3"),
        cls="w-full select-none",
    )


def render_view_toggle(
    active_view: str, current_uf: str = "SP", current_cargo: str = "Governador"
) -> fh.FT:
    """Renderiza o seletor [ 🗺️ Mapa | 🧭 Grade Regional ] para o layout Desktop."""
    is_mapa = active_view == "mapa"

    active_cls = "bg-emerald-500 text-black font-bold border-emerald-400 shadow-sm"
    inactive_cls = (
        "bg-black/30 text-slate-400 hover:text-slate-200 border-transparent hover:bg-white/5"
    )

    cls_mapa = active_cls if is_mapa else inactive_cls
    cls_grade = inactive_cls if is_mapa else active_cls

    return fh.Div(
        fh.Button(
            fh.Span("🗺️", cls="mr-1 text-xs select-none"),
            fh.Span("Mapa"),
            id="btn-view-mapa",
            cls=f"px-2.5 py-1 rounded-md text-[11px] border transition-all cursor-pointer {cls_mapa}",
            hx_get=f"/view-toggle?view=mapa&uf={current_uf}&cargo={current_cargo}",
            hx_target="#radar-content",
            hx_swap="outerHTML",
            hx_push_url=f"/?uf={current_uf}&cargo={current_cargo}&desktop_view=mapa",
        ),
        fh.Button(
            fh.Span("🧭", cls="mr-1 text-xs select-none"),
            fh.Span("Grade Regional"),
            id="btn-view-grade",
            cls=f"px-2.5 py-1 rounded-md text-[11px] border transition-all cursor-pointer {cls_grade}",
            hx_get=f"/view-toggle?view=grade&uf={current_uf}&cargo={current_cargo}",
            hx_target="#radar-content",
            hx_swap="outerHTML",
            hx_push_url=f"/?uf={current_uf}&cargo={current_cargo}&desktop_view=grade",
        ),
        cls="flex items-center p-0.5 rounded-lg bg-black/40 border border-white/10 gap-1",
    )
