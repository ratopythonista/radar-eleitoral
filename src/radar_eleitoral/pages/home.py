"""Página inicial do Radar Eleitoral em FastHTML + HTMX - Layout Split-Screen Editorial."""

from typing import Final

from fasthtml import common as fh
from fasthtml.fastapp import FastHTML

from radar_eleitoral.candidaturas import CARGOS, HeroData, get_hero_data
from radar_eleitoral.cartograma import (
    render_cartograma_regional,
    render_view_toggle,
    resolve_cargo_selection,
    resolve_smart_selection,
)
from radar_eleitoral.map_svg import render_brazil_svg_map

# Estilos da paleta Esmeralda Transparência
THEME: Final[dict[str, str]] = {
    "bg_page": "bg-[#040f0c]",
    "header_bg": "border-white/10",
    "accent": "bg-emerald-500",
    "accent_text": "text-emerald-400",
    "accent_border": "border-emerald-500/30",
    "card_bg": "bg-slate-900/60",
    "card_border": "border-white/10",
    "map_box": "border-white/10 bg-slate-900/40",
    "badge_tag": "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
    "badge_uf": "bg-white/5 text-slate-300 border-white/10",
    "badge_nacional": "bg-emerald-500/20 text-emerald-300 border-emerald-400/40",
    "pill_active": "bg-emerald-500 text-black font-bold border-emerald-400 shadow-md shadow-emerald-500/20",
    "pill_inactive": "bg-white/5 text-slate-300 border-white/10 hover:bg-white/10 hover:text-white",
    "pill_pres_active": "bg-gradient-to-r from-emerald-600 to-emerald-500 text-white font-bold border-emerald-400 shadow-md shadow-emerald-500/20",
    "pill_pres_inactive": "bg-emerald-950/40 text-emerald-300 border-emerald-800/40 hover:bg-emerald-900/50 hover:border-emerald-600/50",
    "cta_btn": "bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold shadow-lg shadow-emerald-500/20 hover:shadow-emerald-400/30",
}

CLS_HERO_WRAPPER = (
    "p-5 sm:p-6 rounded-2xl backdrop-blur-sm border shadow-xl flex flex-col justify-between"
)

CLS_CARD_METRIC = "p-2.5 rounded-lg bg-black/30 border border-white/10"


def render_cargo_pills(
    selected_cargo: str, current_uf: str = "SP", desktop_view: str = "mapa"
) -> fh.FT:
    """Gera o seletor de cargos com botões instrumentados via HTMX."""
    buttons = []
    for cargo in CARGOS:
        is_active = cargo == selected_cargo
        is_pres = cargo == "Presidente"

        btn_class = (
            THEME["pill_pres_active"]
            if (is_active and is_pres)
            else THEME["pill_active"]
            if is_active
            else THEME["pill_pres_inactive"]
            if is_pres
            else THEME["pill_inactive"]
        )

        pad = "px-4 py-2 text-sm"
        target_cargo, target_uf = resolve_cargo_selection(cargo, current_uf)

        btn_content = [fh.Span(cargo, cls="font-semibold")]
        if is_pres:
            badge_pres_cls = (
                "ml-1.5 text-[10px] uppercase font-bold tracking-wider "
                f"px-1.5 py-0.5 rounded border {THEME['badge_tag']}"
            )
            btn_content.append(fh.Span("Nacional", cls=badge_pres_cls))

        buttons.append(
            fh.Button(
                *btn_content,
                id=f"cargo-btn-{cargo.lower().replace(' ', '-')}",
                cls=f"{pad} rounded-xl border font-medium transition-all flex items-center whitespace-nowrap cursor-pointer {btn_class}",
                hx_get=f"/candidaturas?uf={target_uf}&cargo={target_cargo}&desktop_view={desktop_view}",
                hx_target="#radar-content",
                hx_swap="outerHTML",
                hx_push_url=f"/?uf={target_uf}&cargo={target_cargo}&desktop_view={desktop_view}",
            )
        )

    return fh.Div(
        *buttons,
        cls="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none",
    )


def render_hero_card(hero: HeroData) -> fh.FT:
    """Renderiza o Hero Card com dados contextuais, crédito editorial e CTA estilizado."""
    badge_bg = THEME["badge_nacional"] if hero.is_nacional else THEME["badge_uf"]
    badge_label = "ÂMBITO NACIONAL" if hero.is_nacional else f"ESTADO: {hero.uf_nome} ({hero.uf})"

    cta_class = (
        "w-full inline-flex items-center justify-center gap-2 font-semibold "
        "py-3.5 px-5 rounded-xl transition-all transform hover:-translate-y-0.5 "
        f"active:translate-y-0 text-sm sm:text-base {THEME['cta_btn']}"
    )

    return fh.Div(
        # Header do Card com Crédito Editorial Neutro
        fh.Div(
            fh.Div(
                fh.Span(cls="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-2"),
                fh.Span(
                    "FONTE: G1 (AUTOMAÇÃO)",
                    cls="text-[11px] font-bold text-slate-300 tracking-wider",
                ),
                cls="flex items-center",
            ),
            fh.Span(
                badge_label,
                cls=f"text-xs font-semibold px-2.5 py-0.5 rounded-full border {badge_bg}",
            ),
            cls="flex items-center justify-between border-b border-white/10 pb-3",
        ),
        # Título da Matéria
        fh.H2(
            hero.titulo,
            cls="text-lg sm:text-xl font-bold text-white leading-snug mt-3 mb-2",
        ),
        # Resumo Editorial
        fh.P(
            hero.resumo,
            cls="text-sm text-slate-300 leading-relaxed mb-4",
        ),
        # Métricas em Mini Grid
        fh.Div(
            fh.Div(
                fh.Span("Candidaturas Homologadas", cls="text-[11px] text-slate-400 block"),
                fh.Span(
                    f"{hero.candidaturas} concorrentes", cls="text-sm font-bold text-slate-100"
                ),
                cls=CLS_CARD_METRIC,
            ),
            fh.Div(
                fh.Span("Cargo em Disputa", cls="text-[11px] text-slate-400 block"),
                fh.Span(hero.cargo, cls="text-sm font-bold text-slate-100"),
                cls=CLS_CARD_METRIC,
            ),
            cls="grid grid-cols-2 gap-2 mb-5",
        ),
        # Botão de Ação Primária (CTA)
        fh.A(
            fh.Span("Ler reportagem completa no G1", cls="font-bold"),
            fh.Span("↗", cls="text-lg leading-none font-bold"),
            href=hero.url_g1,
            target="_blank",
            rel="noopener noreferrer",
            cls=cta_class,
        ),
        # Rodapé informativo
        fh.P(
            "Link canônico do G1. Matéria jornalística gerada por automação e IA.",
            cls="text-[11px] text-slate-400 text-center mt-3",
        ),
        id="hero-card",
        cls=f"{CLS_HERO_WRAPPER} {THEME['card_bg']}",
    )


def render_home_content(
    selected_cargo: str,
    selected_uf: str,
    desktop_view: str = "mapa",
) -> fh.FT:
    """Renderiza o miolo interativo do Radar Eleitoral (Pills + Mapa/Grade + Hero Card)."""
    hero = get_hero_data(selected_uf, selected_cargo)

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

    is_mapa = desktop_view == "mapa"

    visual_component = (
        fh.Div(
            render_brazil_svg_map(selected_uf, selected_cargo),
            fh.Div(
                "Toque ou clique em um estado no mapa para ver a cobertura regional.",
                cls=footer_map_cls,
            ),
            id="container-visual-mapa",
            cls="p-2 sm:p-4 flex flex-col justify-center items-center min-h-[360px]",
        )
        if is_mapa
        else fh.Div(
            fh.Div(
                render_cartograma_regional(selected_uf, selected_cargo, desktop_view),
                cls="p-3 sm:p-5",
            ),
            fh.Div(
                "Toque ou clique em uma UF para ver a cobertura regional.",
                cls=footer_map_cls,
            ),
            id="container-visual-grade",
        )
    )

    return fh.Div(
        # Barra de Seleção de Cargos
        fh.Section(
            fh.Div(
                fh.Span(
                    "Escolha o cargo:",
                    cls="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2",
                ),
                render_cargo_pills(selected_cargo, selected_uf, desktop_view),
                cls="mb-6",
            )
        ),
        # Grid Principal Responsivo (Split-screen Desktop / Vertical Mobile)
        fh.Main(
            # Coluna Visual (Esquerda Desktop / 1ª Mobile)
            fh.Div(
                fh.Div(
                    fh.Div(
                        fh.Div(
                            fh.Span(
                                "VISÃO GEOGRÁFICA",
                                cls="text-xs font-bold text-slate-400 tracking-wider mr-3",
                            ),
                            fh.Span(label_visao, cls="text-xs font-medium text-slate-300"),
                            cls="flex items-center",
                        ),
                        render_view_toggle(desktop_view, selected_uf, selected_cargo),
                        cls=header_map_cls,
                    ),
                    visual_component,
                    cls=box_map_cls,
                ),
                cls="order-1 lg:order-1 lg:w-7/12",
            ),
            # Coluna do Hero Card (Direita Desktop / 2ª Mobile)
            fh.Div(
                render_hero_card(hero),
                cls="order-2 lg:order-2 lg:w-5/12 flex flex-col justify-start",
            ),
            cls="flex flex-col lg:flex-row gap-6 mb-16",
        ),
        id="radar-content",
        cls="w-full",
    )


def home_page(
    selected_uf: str = "SP",
    selected_cargo: str = "Governador",
    desktop_view: str = "mapa",
) -> fh.FT:
    """Renderiza a página inicial completa com cabeçalho de navegação e miolo interativo."""
    return fh.Div(
        fh.Div(
            # Header da Aplicação
            fh.Header(
                fh.Div(
                    fh.Div(
                        fh.Div(
                            fh.Span(
                                "RADAR",
                                cls=f"font-black text-xl tracking-tight mr-1.5 {THEME['accent_text']}",
                            ),
                            fh.H1(
                                "Eleitoral",
                                cls="text-xl sm:text-2xl font-black tracking-tight text-white inline-block",
                            ),
                            fh.Span(
                                "BETA",
                                cls="ml-2 text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-white/10 text-slate-300",
                            ),
                            cls="flex items-center",
                        ),
                        fh.P(
                            "Vitrine interativa de candidaturas e matérias automatizadas do G1.",
                            cls="text-xs sm:text-sm text-slate-400 mt-0.5",
                        ),
                    ),
                    fh.A(
                        "Sobre o Projeto",
                        href="/sobre",
                        cls="text-xs sm:text-sm font-medium text-slate-400 hover:text-white px-3 py-1.5 rounded-lg hover:bg-white/5 transition-colors whitespace-nowrap shrink-0",
                    ),
                    cls=f"flex items-center justify-between gap-4 border-b {THEME['header_bg']} pb-4 mb-6",
                ),
            ),
            # Miolo Interativo HTMX
            render_home_content(selected_cargo, selected_uf, desktop_view),
            cls="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6",
        ),
        cls=f"min-h-screen {THEME['bg_page']} flex flex-col relative",
    )


def register(app: FastHTML) -> None:
    """Registra as rotas e endpoints da página inicial no aplicativo FastHTML."""

    @app.route("/", methods=["GET"])
    def get_home(uf: str = "SP", cargo: str = "Governador", desktop_view: str = "mapa") -> fh.FT:
        """Ponto de entrada HTML completo da página inicial."""
        target_cargo, target_uf = resolve_smart_selection(uf, cargo)
        return home_page(target_uf, target_cargo, desktop_view)

    @app.route("/candidaturas", methods=["GET"])
    def get_candidaturas(
        request: fh.Request, uf: str = "SP", cargo: str = "Governador", desktop_view: str = "mapa"
    ) -> fh.FT:
        """Endpoint de fragmento HTMX; retorna página completa se acessado diretamente sem HTMX."""
        target_cargo, target_uf = resolve_smart_selection(uf, cargo)
        if request.headers.get("hx-request") == "true":
            return render_home_content(target_cargo, target_uf, desktop_view)
        return home_page(target_uf, target_cargo, desktop_view)

    @app.route("/view-toggle", methods=["GET"])
    def get_view_toggle(
        request: fh.Request, view: str = "mapa", uf: str = "SP", cargo: str = "Governador"
    ) -> fh.FT:
        """Endpoint de alternância da visão [Mapa | Grade Regional] via HTMX."""
        if request.headers.get("hx-request") == "true":
            return render_home_content(cargo, uf, desktop_view=view)
        return home_page(uf, cargo, desktop_view=view)
