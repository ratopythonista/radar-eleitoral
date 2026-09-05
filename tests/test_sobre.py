"""Testes unitários para a página /sobre do Radar Eleitoral."""

from dash import html

import radar_eleitoral.app  # noqa: F401
from radar_eleitoral.config import settings
from radar_eleitoral.pages.sobre import (
    layout,
    render_author_card,
    render_disclaimer_card,
    render_future_vision,
    render_hero_civico,
    render_pix_support_card,
    render_sobre_header,
)


def _find_strings(component) -> list[str]:
    """Extrai recursivamente todos os textos de uma árvore de componentes Dash."""
    strings = []
    if isinstance(component, str):
        strings.append(component)
    elif hasattr(component, "children"):
        children = component.children
        if isinstance(children, list):
            for child in children:
                strings.extend(_find_strings(child))
        elif children is not None:
            strings.extend(_find_strings(children))
    return strings


def test_render_sobre_header():
    """Header deve conter link de retorno ao mapa e branding."""
    header = render_sobre_header()
    text = " ".join(_find_strings(header))
    assert "RADAR" in text
    assert "Eleitoral" in text

    # Verifica link para a Home
    def _has_home_link(comp):
        if getattr(comp, "href", None) == "/":
            return True
        if hasattr(comp, "children") and isinstance(comp.children, list):
            return any(_has_home_link(c) for c in comp.children)
        return False

    assert _has_home_link(header)


def test_render_hero_civico():
    """Hero cívico deve apresentar o propósito público do Radar Eleitoral."""
    hero = render_hero_civico()
    text = " ".join(_find_strings(hero))
    assert "Democratizando o Acesso" in text or "Transparência" in text
    assert "Radar Eleitoral" in text


def test_render_disclaimer_card():
    """Card de independência deve blindar juridicamente e citar o autor e G1."""
    card = render_disclaimer_card()
    text = " ".join(_find_strings(card))
    assert "Nota de Transparência e Independência" in text
    assert "Rodrigo Guimarães Araújo" in text
    assert "não possui qualquer afiliação institucional" in text
    assert "G1" in text


def test_render_future_vision():
    """Visão de futuro deve incorporar o teaser 'Vem mais esse ano'."""
    vision = render_future_vision()
    text = " ".join(_find_strings(vision))
    assert "O radar continua ligado" in text or "Vem mais" in text


def test_render_author_card():
    """Card do autor deve apresentar nome, headline, avatar e os 4 links sociais."""
    card = render_author_card(settings)
    text = " ".join(_find_strings(card))
    assert "Rodrigo Guimarães Araújo" in text
    assert "Especialista em Inteligência Artificial" in text

    def _collect_hrefs(comp):
        hrefs = []
        if getattr(comp, "href", None):
            hrefs.append(comp.href)
        if hasattr(comp, "children") and isinstance(comp.children, list):
            for c in comp.children:
                hrefs.extend(_collect_hrefs(c))
        elif hasattr(comp, "children") and comp.children is not None:
            hrefs.extend(_collect_hrefs(comp.children))
        return hrefs

    hrefs = _collect_hrefs(card)
    assert settings.github_url in hrefs
    assert settings.linkedin_url in hrefs
    assert settings.instagram_url in hrefs
    assert settings.x_url in hrefs


def test_render_pix_support_card():
    """Card do Pix deve renderizar QR Code, chave visível e botão de cópia."""
    pix_card = render_pix_support_card(settings)
    text = " ".join(_find_strings(pix_card))
    assert settings.pix_key in text
    assert "Copiar Chave Pix" in text

    def _find_img(comp):
        if isinstance(comp, html.Img):
            return comp
        if hasattr(comp, "children"):
            children = comp.children
            if isinstance(children, list):
                for c in children:
                    res = _find_img(c)
                    if res is not None:
                        return res
            elif children is not None:
                return _find_img(children)
        return None

    img = _find_img(pix_card)
    assert img is not None
    assert str(img.src).startswith("data:image/svg+xml")


def test_layout_callable():
    """Garante que a função layout() da página /sobre instancia a árvore sem erros."""
    full_page = layout()
    assert full_page is not None
    assert isinstance(full_page, html.Div)
    assert isinstance(full_page.children, list)
    assert len(full_page.children) == 7
