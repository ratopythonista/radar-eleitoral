"""Página Sobre do Radar Eleitoral em FastHTML - Narrativa, Autoria e Apoio Pix."""

from typing import Final

from fasthtml import common as fh
from fasthtml.fastapp import FastHTML

from radar_eleitoral.config import Settings, settings
from radar_eleitoral.pix import generate_pix_payload, generate_pix_qr_data_uri

THEME: Final[dict[str, str]] = {
    "accent": "bg-emerald-500",
    "accent_text": "text-emerald-400",
    "accent_border": "border-emerald-500/30",
    "card_bg": "bg-slate-900/60",
    "card_border": "border-white/10",
}


def render_sobre_header() -> fh.FT:
    """Header da página com navegação de retorno à Home."""
    return fh.Header(
        fh.Div(
            fh.A(
                fh.Span(
                    "RADAR", cls=f"font-black text-xl tracking-tight mr-1.5 {THEME['accent_text']}"
                ),
                fh.Span(
                    "Eleitoral", cls="text-xl font-black tracking-tight text-white inline-block"
                ),
                href="/",
                cls="flex items-center hover:opacity-90 transition-opacity",
            ),
            cls="flex items-center",
        ),
        fh.A(
            fh.Span("←", cls="mr-1.5 text-emerald-400 font-bold"),
            fh.Span("Voltar ao Mapa"),
            href="/",
            cls="text-xs sm:text-sm font-medium text-slate-300 hover:text-white px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all flex items-center whitespace-nowrap shrink-0",
        ),
        cls="flex items-center justify-between border-b border-white/10 pb-5 mb-8",
    )


def render_hero_civico() -> fh.FT:
    """Apresenta o propósito cívico e a proposta de valor do Radar Eleitoral."""
    return fh.Section(
        fh.Div(
            fh.Span(
                "TRANSPARÊNCIA E CIDADANIA",
                cls="text-[11px] font-extrabold uppercase tracking-widest px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30",
            ),
            fh.H1(
                "Democratizando o Acesso à Cobertura Eleitoral do Brasil",
                cls="text-2xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white mt-4 mb-4",
            ),
            fh.P(
                "O Radar Eleitoral é uma plataforma cívica e interativa projetada para transformar "
                "a consulta de candidaturas e eleições gerais em uma experiência visual, acessível e direta. "
                "Ao integrar mapas interativos com o acervo de reportagens automatizadas do portal G1, a plataforma "
                "permite que cidadãos, jornalistas e pesquisadores explorem os cenários eleitorais de todos os "
                "estados brasileiros com facilidade e agilidade.",
                cls="text-sm sm:text-base text-slate-300 leading-relaxed max-w-3xl",
            ),
            cls="flex flex-col items-start",
        ),
        cls="mb-8",
    )


def render_disclaimer_card() -> fh.FT:
    """Card contendo a declaração explícita de independência e blindagem jurídica."""
    return fh.Div(
        fh.Div(
            fh.Span("🛡️", cls="text-xl sm:text-2xl mr-3 select-none"),
            fh.Div(
                fh.H2(
                    "Nota de Transparência e Independência",
                    cls="text-sm font-bold text-amber-300 uppercase tracking-wider mb-1",
                ),
                fh.P(
                    "O Radar Eleitoral é um projeto cívico e de código aberto desenvolvido de "
                    "forma estritamente pessoal e independente por Rodrigo Guimarães Araújo. "
                    "Este projeto não possui qualquer afiliação institucional, vínculo oficial, endosso "
                    "ou incentivo financeiro do Grupo Globo ou do portal G1. Todas as matérias jornalísticas "
                    "exibidas pertencem ao G1 e são acessadas exclusivamente por links públicos canônicos.",
                    cls="text-xs sm:text-sm text-amber-200/90 leading-relaxed",
                ),
                cls="flex-1",
            ),
            cls="flex items-start",
        ),
        cls="p-5 rounded-2xl bg-amber-500/5 border border-amber-500/30 shadow-lg backdrop-blur-sm mb-10",
    )


def render_future_vision() -> fh.FT:
    """Card de Roadmap Cívico destacando o teaser 'Vem mais esse ano'."""
    return fh.Section(
        fh.Div(
            fh.Div(
                fh.Span("🚀", cls="text-2xl mr-3 select-none"),
                fh.Div(
                    fh.H3(
                        "O radar continua ligado: o que vem por aí",
                        cls="text-lg font-bold text-white",
                    ),
                    fh.P(
                        "A tecnologia cívica não para. Estamos preparando a expansão da "
                        "cobertura para novos pleitos, novas visualizações analíticas de dados e "
                        "ferramentas enriquecidas de comparação pública. Vem mais esse ano — "
                        "continue acompanhando a evolução do código aberto.",
                        cls="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed",
                    ),
                ),
                cls="flex items-start",
            ),
            cls="p-6 rounded-2xl bg-gradient-to-r from-emerald-950/40 to-slate-900/80 border border-emerald-500/30 shadow-xl mb-12",
        )
    )


def render_author_card(cfg: Settings) -> fh.FT:
    """Apresenta a autoria profissional com biografia e links de redes sociais."""
    return fh.Section(
        fh.Div(
            fh.Div(
                fh.Img(
                    src=cfg.author_avatar_url,
                    alt=f"Foto de {cfg.author_name}",
                    cls="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl object-cover border-2 border-emerald-500/40 shadow-lg mb-4 sm:mb-0 sm:mr-6",
                ),
                fh.Div(
                    fh.Span(
                        "DESENVOLVEDOR & AUTOR",
                        cls="text-[10px] font-extrabold uppercase tracking-widest text-emerald-400",
                    ),
                    fh.H3(
                        cfg.author_name, cls="text-xl sm:text-2xl font-black text-white mt-0.5 mb-1"
                    ),
                    fh.P(
                        cfg.author_headline,
                        cls="text-xs sm:text-sm font-medium text-emerald-300/90 mb-3",
                    ),
                    fh.P(
                        "Engenheiro apaixonado por arquiteturas escaláveis, inteligência artificial "
                        "e tecnologia a serviço da transparência cívica. Idealizou e desenvolveu o "
                        "Radar Eleitoral como iniciativa de código aberto para aproximar dados e sociedade.",
                        cls="text-xs sm:text-sm text-slate-400 leading-relaxed max-w-2xl",
                    ),
                    fh.Div(
                        fh.A(
                            "GitHub",
                            href=cfg.github_url,
                            target="_blank",
                            rel="noopener noreferrer",
                            cls="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center",
                        ),
                        fh.A(
                            "LinkedIn",
                            href=cfg.linkedin_url,
                            target="_blank",
                            rel="noopener noreferrer",
                            cls="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center",
                        ),
                        fh.A(
                            "Instagram",
                            href=cfg.instagram_url,
                            target="_blank",
                            rel="noopener noreferrer",
                            cls="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center",
                        ),
                        fh.A(
                            "X (Twitter)",
                            href=cfg.x_url,
                            target="_blank",
                            rel="noopener noreferrer",
                            cls="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center",
                        ),
                        cls="flex flex-wrap gap-2.5 mt-4",
                    ),
                    cls="flex-1",
                ),
                cls="flex flex-col sm:flex-row items-start sm:items-center",
            ),
            cls=f"p-6 sm:p-8 rounded-2xl {THEME['card_bg']} border {THEME['card_border']} shadow-xl mb-12",
        )
    )


def render_pix_support_card(cfg: Settings) -> fh.FT:
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

    copy_script = """
    function copyPixKey(key, btn) {
        navigator.clipboard.writeText(key).then(function() {
            var fb = document.getElementById('copy-pix-feedback');
            if (fb) {
                fb.textContent = 'Chave Pix copiada com sucesso!';
                setTimeout(function() { fb.textContent = ''; }, 3000);
            }
        }).catch(function() {
            var fb = document.getElementById('copy-pix-feedback');
            if (fb) fb.textContent = 'Erro ao copiar. Selecione o texto manualmente.';
        });
    }
    """

    return fh.Section(
        fh.Div(
            fh.Div(
                fh.Span(
                    "SUSTENTABILIDADE DO PROJETO",
                    cls="text-[11px] font-extrabold uppercase tracking-widest text-emerald-400",
                ),
                fh.H2(
                    "Apoie a Continuidade do Radar Eleitoral",
                    cls="text-xl sm:text-3xl font-black text-white mt-1 mb-3",
                ),
                fh.P(
                    "O Radar Eleitoral é 100% gratuito, aberto e sem anúncios. "
                    "Para manter a infraestrutura de servidores em nuvem (Render.com), "
                    "o registro de domínio e as horas de manutenção contínua, você pode "
                    "fazer uma contribuição voluntária de qualquer valor via Pix.",
                    cls="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-xl",
                ),
                # Custos discriminados
                fh.Div(
                    fh.Div(
                        fh.Span("⚡", cls="mr-2 text-emerald-400"),
                        fh.Span(
                            "Hospedagem em contêiner em nuvem (Render.com)",
                            cls="text-xs text-slate-300 font-medium",
                        ),
                        cls="flex items-center",
                    ),
                    fh.Div(
                        fh.Span("🌐", cls="mr-2 text-emerald-400"),
                        fh.Span(
                            "Registro de domínio e conectividade segura",
                            cls="text-xs text-slate-300 font-medium",
                        ),
                        cls="flex items-center",
                    ),
                    fh.Div(
                        fh.Span("🛠️", cls="mr-2 text-emerald-400"),
                        fh.Span(
                            "Manutenção técnica e evolução do código aberto",
                            cls="text-xs text-slate-300 font-medium",
                        ),
                        cls="flex items-center",
                    ),
                    cls="space-y-2 mt-4 mb-6",
                ),
                cls="flex-1 pr-0 lg:pr-8",
            ),
            # Bloco do QR Code e Copia-e-Cola
            fh.Div(
                fh.Div(
                    fh.Img(
                        src=qr_data_uri,
                        alt="QR Code Pix para apoio ao Radar Eleitoral",
                        cls="w-48 h-48 sm:w-52 sm:h-52 rounded-xl bg-white p-2 shadow-2xl",
                    ),
                    cls="flex justify-center mb-4",
                ),
                fh.Div(
                    fh.Span(
                        "Chave Pix (E-mail):",
                        cls="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1",
                    ),
                    fh.Code(
                        cfg.pix_key,
                        cls="px-3 py-1.5 rounded-lg bg-black/40 border border-white/15 text-xs sm:text-sm font-mono text-emerald-300 select-all block text-center break-all",
                    ),
                    cls="mb-3",
                ),
                fh.Button(
                    fh.Span("📋", cls="mr-1.5"),
                    fh.Span("Copiar Chave Pix", cls="whitespace-nowrap"),
                    id="btn-copy-pix",
                    cls="w-full py-2.5 px-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs sm:text-sm shadow-lg shadow-emerald-500/20 hover:shadow-emerald-400/30 transition-all cursor-pointer flex items-center justify-center",
                    onclick=f"copyPixKey('{cfg.pix_key}', this)",
                ),
                fh.Div(
                    id="copy-pix-feedback",
                    cls="text-center text-xs font-semibold text-emerald-400 mt-2 min-h-[1.25rem] transition-all",
                ),
                fh.Script(copy_script),
                cls="w-full lg:w-72 p-5 rounded-2xl bg-black/40 border border-emerald-500/30 shadow-inner flex flex-col justify-center",
            ),
            cls="flex flex-col lg:flex-row items-center lg:items-start justify-between",
        ),
        cls=f"p-6 sm:p-8 rounded-3xl {THEME['card_bg']} border {THEME['accent_border']} shadow-2xl mb-12",
    )


def render_sobre_footer() -> fh.FT:
    """Rodapé limpo e informativo da página Sobre."""
    return fh.Footer(
        fh.Div(
            fh.P(
                "Radar Eleitoral • Plataforma Cívica Independente de Código Aberto",
                cls="text-xs text-slate-400",
            ),
            fh.P(
                "Cobertura automatizada via portal G1 (Globo) • Eleições Gerais do Brasil",
                cls="text-[11px] text-slate-400 mt-1",
            ),
            cls="flex flex-col sm:flex-row items-center justify-between gap-2 border-t border-white/10 pt-6",
        ),
        cls="mt-12",
    )


def layout(cfg: Settings | None = None) -> fh.FT:
    """Renderiza a estrutura completa da página /sobre."""
    active_cfg = cfg or settings

    return fh.Div(
        fh.Div(
            render_sobre_header(),
            render_hero_civico(),
            render_disclaimer_card(),
            render_future_vision(),
            render_author_card(active_cfg),
            render_pix_support_card(active_cfg),
            render_sobre_footer(),
            cls="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
        ),
        cls="min-h-screen bg-[#040f0c] text-slate-100 antialiased relative selection:bg-emerald-500 selection:text-black",
    )


def register(app: FastHTML) -> None:
    """Registra a rota /sobre no aplicativo FastHTML."""

    @app.route("/sobre", methods=["GET"])
    def get_sobre() -> fh.FT:
        """Ponto de entrada HTML completo da página /sobre."""
        return layout(settings)
