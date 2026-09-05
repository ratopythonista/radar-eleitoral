"""Página Sobre do Radar Eleitoral - Narrativa, Autoria e Apoio Pix."""

import dash
from dash import Input, Output, State, clientside_callback, dcc, html

from radar_eleitoral.config import Settings, settings
from radar_eleitoral.pix import generate_pix_payload, generate_pix_qr_data_uri

dash.register_page(__name__, path="/sobre", title="Radar Eleitoral - Sobre o Projeto")

THEME = {
    "accent": "bg-emerald-500",
    "accent_text": "text-emerald-400",
    "accent_border": "border-emerald-500/30",
    "card_bg": "bg-slate-900/60",
    "card_border": "border-white/10",
}


def render_sobre_header() -> html.Header:
    """Header da página com navegação de retorno à Home."""
    return html.Header(
        [
            html.Div(
                [
                    html.A(
                        [
                            html.Span(
                                "RADAR",
                                className=f"font-black text-xl tracking-tight mr-1.5 {THEME['accent_text']}",
                            ),
                            html.Span(
                                "Eleitoral",
                                className="text-xl font-black tracking-tight text-white inline-block",
                            ),
                        ],
                        href="/",
                        className="flex items-center hover:opacity-90 transition-opacity",
                    ),
                ],
                className="flex items-center",
            ),
            html.A(
                [
                    html.Span("←", className="mr-1.5 text-emerald-400 font-bold"),
                    html.Span("Voltar ao Mapa"),
                ],
                href="/",
                className=(
                    "text-xs sm:text-sm font-medium text-slate-300 hover:text-white "
                    "px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 "
                    "border border-white/10 transition-all flex items-center"
                ),
            ),
        ],
        className="flex items-center justify-between border-b border-white/10 pb-5 mb-8",
    )


def render_hero_civico() -> html.Section:
    """Apresenta o propósito cívico e a proposta de valor do Radar Eleitoral."""
    return html.Section(
        [
            html.Div(
                [
                    html.Span(
                        "TRANSPARÊNCIA E CIDADANIA",
                        className=(
                            "text-[11px] font-extrabold uppercase tracking-widest px-3 py-1 "
                            "rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30"
                        ),
                    ),
                    html.H1(
                        "Democratizando o Acesso à Cobertura Eleitoral do Brasil",
                        className="text-2xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white mt-4 mb-4",
                    ),
                    html.P(
                        "O Radar Eleitoral é uma plataforma cívica e interativa projetada para transformar "
                        "a consulta de candidaturas e eleições gerais em uma experiência visual, acessível e direta. "
                        "Ao integrar mapas interativos com o acervo de reportagens automatizadas do portal G1, a plataforma "
                        "permite que cidadãos, jornalistas e pesquisadores explorem os cenários eleitorais de todos os "
                        "estados brasileiros com facilidade e agilidade.",
                        className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-3xl",
                    ),
                ],
                className="flex flex-col items-start",
            )
        ],
        className="mb-8",
    )


def render_disclaimer_card() -> html.Div:
    """Card contendo a declaração explícita de independência e blindagem jurídica."""
    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        "🛡️",
                        className="text-xl sm:text-2xl mr-3 select-none",
                    ),
                    html.Div(
                        [
                            html.H2(
                                "Nota de Transparência e Independência",
                                className="text-sm font-bold text-amber-300 uppercase tracking-wider mb-1",
                            ),
                            html.P(
                                "O Radar Eleitoral é um projeto cívico e de código aberto desenvolvido de "
                                "forma estritamente pessoal e independente por Rodrigo Guimarães Araújo. "
                                "Este projeto não possui qualquer afiliação institucional, vínculo oficial, endosso "
                                "ou incentivo financeiro do Grupo Globo ou do portal G1. Todas as matérias jornalísticas "
                                "exibidas pertencem ao G1 e são acessadas exclusivamente por links públicos canônicos.",
                                className="text-xs sm:text-sm text-slate-300 leading-relaxed",
                            ),
                        ],
                        className="flex-1",
                    ),
                ],
                className="flex items-start",
            )
        ],
        className="p-5 rounded-2xl bg-amber-500/5 border border-amber-500/30 shadow-lg backdrop-blur-sm mb-10",
    )


def render_future_vision() -> html.Section:
    """Card de Roadmap Cívico destacando o teaser 'Vem mais esse ano'."""
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "🚀",
                                className="text-2xl mr-3 select-none",
                            ),
                            html.Div(
                                [
                                    html.H3(
                                        "O radar continua ligado: o que vem por aí",
                                        className="text-lg font-bold text-white",
                                    ),
                                    html.P(
                                        "A tecnologia cívica não para. Estamos preparando a expansão da "
                                        "cobertura para novos pleitos, novas visualizações analíticas de dados e "
                                        "ferramentas enriquecidas de comparação pública. Vem mais esse ano — "
                                        "continue acompanhando a evolução do código aberto.",
                                        className="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed",
                                    ),
                                ]
                            ),
                        ],
                        className="flex items-start",
                    )
                ],
                className=(
                    "p-6 rounded-2xl bg-gradient-to-r from-emerald-950/40 to-slate-900/80 "
                    "border border-emerald-500/30 shadow-xl mb-12"
                ),
            )
        ]
    )


def render_author_card(cfg: Settings) -> html.Section:
    """Apresenta a autoria profissional com biografia e links de redes sociais."""
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src=cfg.author_avatar_url,
                                alt=f"Foto de {cfg.author_name}",
                                className=(
                                    "w-20 h-20 sm:w-24 sm:h-24 rounded-2xl object-cover "
                                    "border-2 border-emerald-500/40 shadow-lg mb-4 sm:mb-0 sm:mr-6"
                                ),
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "DESENVOLVEDOR & AUTOR",
                                        className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-400",
                                    ),
                                    html.H3(
                                        cfg.author_name,
                                        className="text-xl sm:text-2xl font-black text-white mt-0.5 mb-1",
                                    ),
                                    html.P(
                                        cfg.author_headline,
                                        className="text-xs sm:text-sm font-medium text-emerald-300/90 mb-3",
                                    ),
                                    html.P(
                                        "Engenheiro apaixonado por arquiteturas escaláveis, inteligência artificial "
                                        "e tecnologia a serviço da transparência cívica. Idealizou e desenvolveu o "
                                        "Radar Eleitoral como iniciativa de código aberto para aproximar dados e sociedade.",
                                        className="text-xs sm:text-sm text-slate-400 leading-relaxed max-w-2xl",
                                    ),
                                    # Links Sociais
                                    html.Div(
                                        [
                                            html.A(
                                                "GitHub",
                                                href=cfg.github_url,
                                                target="_blank",
                                                rel="noopener noreferrer",
                                                className=(
                                                    "px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 "
                                                    "border border-white/10 text-xs font-semibold text-slate-300 "
                                                    "hover:text-white transition-all flex items-center"
                                                ),
                                            ),
                                            html.A(
                                                "LinkedIn",
                                                href=cfg.linkedin_url,
                                                target="_blank",
                                                rel="noopener noreferrer",
                                                className=(
                                                    "px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 "
                                                    "border border-white/10 text-xs font-semibold text-slate-300 "
                                                    "hover:text-white transition-all flex items-center"
                                                ),
                                            ),
                                            html.A(
                                                "Instagram",
                                                href=cfg.instagram_url,
                                                target="_blank",
                                                rel="noopener noreferrer",
                                                className=(
                                                    "px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 "
                                                    "border border-white/10 text-xs font-semibold text-slate-300 "
                                                    "hover:text-white transition-all flex items-center"
                                                ),
                                            ),
                                            html.A(
                                                "X (Twitter)",
                                                href=cfg.x_url,
                                                target="_blank",
                                                rel="noopener noreferrer",
                                                className=(
                                                    "px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 "
                                                    "border border-white/10 text-xs font-semibold text-slate-300 "
                                                    "hover:text-white transition-all flex items-center"
                                                ),
                                            ),
                                        ],
                                        className="flex flex-wrap gap-2.5 mt-4",
                                    ),
                                ],
                                className="flex-1",
                            ),
                        ],
                        className="flex flex-col sm:flex-row items-start sm:items-center",
                    )
                ],
                className=f"p-6 sm:p-8 rounded-2xl {THEME['card_bg']} border {THEME['card_border']} shadow-xl mb-12",
            )
        ]
    )


def render_pix_support_card(cfg: Settings) -> html.Section:
    """Card de Sustentabilidade e Mecanismo de Apoio voluntário via Pix."""
    payload = generate_pix_payload(
        key=cfg.pix_key,
        name=cfg.pix_receiver_name,
        city=cfg.pix_city,
        txid="***",
    )
    qr_data_uri = generate_pix_qr_data_uri(
        payload=payload,
        scale=6,
        border=2,
        dark="#000000",
        light="#ffffff",
    )

    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "SUSTENTABILIDADE DO PROJETO",
                                className="text-[11px] font-extrabold uppercase tracking-widest text-emerald-400",
                            ),
                            html.H2(
                                "Apoie a Continuidade do Radar Eleitoral",
                                className="text-xl sm:text-3xl font-black text-white mt-1 mb-3",
                            ),
                            html.P(
                                "O Radar Eleitoral é 100% gratuito, aberto e sem anúncios. "
                                "Para manter a infraestrutura de servidores em nuvem (Render.com), "
                                "o registro de domínio e as horas de manutenção contínua, você pode "
                                "fazer uma contribuição voluntária de qualquer valor via Pix.",
                                className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-xl",
                            ),
                            # Custos discriminados
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "⚡",
                                                className="mr-2 text-emerald-400",
                                            ),
                                            html.Span(
                                                "Hospedagem em contêiner em nuvem (Render.com)",
                                                className="text-xs text-slate-300 font-medium",
                                            ),
                                        ],
                                        className="flex items-center",
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                "🌐",
                                                className="mr-2 text-emerald-400",
                                            ),
                                            html.Span(
                                                "Registro de domínio e conectividade segura",
                                                className="text-xs text-slate-300 font-medium",
                                            ),
                                        ],
                                        className="flex items-center",
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                "🛠️",
                                                className="mr-2 text-emerald-400",
                                            ),
                                            html.Span(
                                                "Manutenção técnica e evolução do código aberto",
                                                className="text-xs text-slate-300 font-medium",
                                            ),
                                        ],
                                        className="flex items-center",
                                    ),
                                ],
                                className="space-y-2 mt-4 mb-6",
                            ),
                        ],
                        className="flex-1 pr-0 lg:pr-8",
                    ),
                    # Bloco do QR Code e Copia-e-Cola
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Img(
                                        src=qr_data_uri,
                                        alt="QR Code Pix para apoio ao Radar Eleitoral",
                                        className="w-48 h-48 sm:w-52 sm:h-52 rounded-xl bg-white p-2 shadow-2xl",
                                    ),
                                ],
                                className="flex justify-center mb-4",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "Chave Pix (E-mail):",
                                        className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1",
                                    ),
                                    html.Code(
                                        cfg.pix_key,
                                        className=(
                                            "px-3 py-1.5 rounded-lg bg-black/40 border border-white/15 "
                                            "text-xs sm:text-sm font-mono text-emerald-300 select-all block text-center break-all"
                                        ),
                                    ),
                                ],
                                className="mb-3",
                            ),
                            html.Button(
                                [
                                    html.Span("📋", className="mr-1.5"),
                                    html.Span("Copiar Chave Pix"),
                                ],
                                id="btn-copy-pix",
                                n_clicks=0,
                                className=(
                                    "w-full py-2.5 px-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 "
                                    "text-slate-950 font-bold text-xs sm:text-sm shadow-lg shadow-emerald-500/20 "
                                    "hover:shadow-emerald-400/30 transition-all cursor-pointer flex items-center justify-center"
                                ),
                            ),
                            html.Div(
                                id="copy-pix-feedback",
                                className="text-center text-xs font-semibold text-emerald-400 mt-2 min-h-[1.25rem] transition-all",
                            ),
                            dcc.Store(id="store-pix-key", data=cfg.pix_key),
                        ],
                        className=(
                            "w-full lg:w-72 p-5 rounded-2xl bg-black/40 border border-emerald-500/30 "
                            "shadow-inner flex flex-col justify-center"
                        ),
                    ),
                ],
                className="flex flex-col lg:flex-row items-center lg:items-start justify-between",
            )
        ],
        className=f"p-6 sm:p-8 rounded-3xl {THEME['card_bg']} border {THEME['accent_border']} shadow-2xl mb-12",
    )


def render_sobre_footer() -> html.Footer:
    """Rodapé limpo e informativo da página Sobre."""
    return html.Footer(
        [
            html.Div(
                [
                    html.P(
                        "Radar Eleitoral — Projeto cívico independente de código aberto.",
                        className="text-xs text-slate-400",
                    ),
                    html.A(
                        "← Voltar ao Início",
                        href="/",
                        className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold transition-colors",
                    ),
                ],
                className="flex flex-col sm:flex-row items-center justify-between gap-2 border-t border-white/10 pt-6",
            )
        ],
        className="mt-auto",
    )


def layout() -> html.Div:
    """Renderiza a estrutura completa da página /sobre."""
    return html.Div(
        [
            render_sobre_header(),
            render_hero_civico(),
            render_disclaimer_card(),
            render_future_vision(),
            render_author_card(settings),
            render_pix_support_card(settings),
            render_sobre_footer(),
        ],
        className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full",
    )


# Clientside callback nativo para cópia instantânea da chave Pix na área de transferência
clientside_callback(
    """
    function(n_clicks, key) {
        if (!n_clicks || n_clicks === 0) {
            return window.dash_clientside.no_update;
        }
        const pixKey = key || "ratopythonista@noh.pix";
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(pixKey);
        } else {
            const input = document.createElement('textarea');
            input.value = pixKey;
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
        }
        return "✓ Chave Pix copiada com sucesso!";
    }
    """,
    Output("copy-pix-feedback", "children"),
    Input("btn-copy-pix", "n_clicks"),
    State("store-pix-key", "data"),
    prevent_initial_call=True,
)
