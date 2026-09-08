"""Testes unitários para a página /sobre do Radar Eleitoral em FastHTML."""

from fasthtml import common as fh
from starlette.testclient import TestClient

from radar_eleitoral.config import settings
from radar_eleitoral.main import app
from radar_eleitoral.pages.sobre import (
    layout,
    render_author_card,
    render_disclaimer_card,
    render_future_vision,
    render_hero_civico,
    render_pix_support_card,
    render_sobre_header,
)


def test_render_sobre_header() -> None:
    """Header deve conter link de retorno ao mapa e branding."""
    header = render_sobre_header()
    xml = fh.to_xml(header)

    assert "RADAR" in xml
    assert "Eleitoral" in xml
    assert 'href="/"' in xml
    assert "Voltar ao Mapa" in xml


def test_render_hero_civico() -> None:
    """Hero cívico deve apresentar o propósito público do Radar Eleitoral."""
    hero = render_hero_civico()
    xml = fh.to_xml(hero)

    assert "TRANSPARÊNCIA E CIDADANIA" in xml
    assert "Democratizando o Acesso à Cobertura Eleitoral do Brasil" in xml
    assert "Radar Eleitoral" in xml


def test_render_disclaimer_card() -> None:
    """Card de independência deve blindar juridicamente e citar o autor e G1."""
    card = render_disclaimer_card()
    xml = fh.to_xml(card)

    assert "Nota de Transparência e Independência" in xml
    assert "Rodrigo Guimarães Araújo" in xml
    assert "G1" in xml


def test_render_future_vision() -> None:
    """Visão de futuro deve incorporar o teaser 'Vem mais esse ano'."""
    vision = render_future_vision()
    xml = fh.to_xml(vision)

    assert "O radar continua ligado" in xml or "Vem mais" in xml


def test_render_author_card() -> None:
    """Card do autor deve apresentar nome, headline, avatar e os 4 links sociais."""
    card = render_author_card(settings)
    xml = fh.to_xml(card)

    assert settings.author_name in xml
    assert "Tech Lead" in xml
    assert "Engenheiro de Software" in xml
    assert settings.author_avatar_url in xml
    assert settings.github_url in xml
    assert settings.linkedin_url in xml
    assert settings.instagram_url in xml
    assert settings.x_url in xml


def test_render_pix_support_card() -> None:
    """Card do Pix deve renderizar QR Code, chave visível e botão de cópia."""
    card = render_pix_support_card(settings)
    xml = fh.to_xml(card)

    assert "SUSTENTABILIDADE DO PROJETO" in xml
    assert settings.pix_key in xml
    assert "Copiar Chave Pix" in xml
    assert "copyPixKey" in xml
    assert "data:image/svg+xml" in xml


def test_layout_callable() -> None:
    """Garante que a função layout() da página /sobre instancia a árvore sem erros."""
    full_page = layout()
    xml = fh.to_xml(full_page)

    assert "Democratizando o Acesso" in xml
    assert settings.author_name in xml
    assert settings.pix_key in xml


def test_endpoint_sobre_get() -> None:
    """Valida o endpoint HTTP da rota /sobre via TestClient."""
    client = TestClient(app)
    res = client.get("/sobre")
    assert res.status_code == 200
    assert "Democratizando o Acesso" in res.text
    assert settings.pix_key in res.text
