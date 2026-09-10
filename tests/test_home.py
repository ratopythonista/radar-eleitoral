"""Testes de unidade e integridade para a página Home do Radar Eleitoral em FastHTML."""

import pytest
from fasthtml import common as fh
from starlette.testclient import TestClient

from radar_eleitoral.candidaturas import CARGOS, get_hero_data
from radar_eleitoral.config import Settings
from radar_eleitoral.main import app
from radar_eleitoral.pages.home import (
    home_page,
    render_home_content,
    render_home_footer,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_candidaturas_data_presidente() -> None:
    """Valida contrato dos dados reais para Presidente (âmbito nacional)."""
    hero = get_hero_data(uf="BR", cargo="Presidente")
    assert hero.is_nacional is True
    assert hero.uf == "BR"
    assert hero.cargo == "Presidente"
    assert hero.candidaturas > 0
    assert "g1.globo.com" in hero.url_g1


@pytest.mark.parametrize("uf", ["SP", "RJ", "MG", "BA", "RS"])
def test_candidaturas_data_estados(uf: str) -> None:
    """Valida dados para os estados com dataset real carregado."""
    hero = get_hero_data(uf=uf, cargo="Governador")
    assert hero.is_nacional is False
    assert hero.uf == uf
    assert hero.cargo == "Governador"
    assert hero.candidaturas > 0
    assert "g1.globo.com" in hero.url_g1


def test_candidaturas_data_fallback() -> None:
    """Valida fallback dinâmico determinístico para cargos não cadastrados."""
    hero = get_hero_data(uf="AC", cargo="Deputado Estadual")
    assert hero.uf == "AC"
    assert hero.cargo == "Deputado Estadual"
    assert "g1.globo.com" in hero.url_g1
    assert "Acre" in hero.titulo


def test_render_home_content_mapa_view() -> None:
    """Garante que a Home renderiza com o mapa SVG na visão padrão."""
    content = render_home_content("Governador", "SP", desktop_view="mapa")
    xml = fh.to_xml(content)
    assert "São Paulo" in xml
    assert "container-visual-mapa" in xml
    assert "svg-uf-SP" in xml


def test_render_home_content_grade_view() -> None:
    """Garante que a Home renderiza com a visão de grade regional no desktop."""
    content = render_home_content("Governador", "SP", desktop_view="grade")
    xml = fh.to_xml(content)
    assert "São Paulo" in xml
    assert "container-visual-grade" in xml
    assert "Norte" in xml


def test_render_home_footer_custom_and_defaults() -> None:
    """Valida renderização do rodapé com assinatura, canais de contato e disclaimer."""
    custom_cfg = Settings(
        author_name="Fulano de Tal",
        author_email="fulano@exemplo.com",
        github_url="https://github.com/fulano",
        linkedin_url="https://linkedin.com/in/fulano",
    )
    footer = render_home_footer(custom_cfg)
    xml = fh.to_xml(footer)

    assert "Desenvolvido por" in xml
    assert "Fulano de Tal" in xml
    assert "mailto:fulano@exemplo.com" in xml
    assert "https://github.com/fulano" in xml
    assert "https://linkedin.com/in/fulano" in xml
    assert "sem vínculo institucional com o Grupo Globo ou portal G1" in xml
    assert "Cobertura automatizada via portal G1" in xml


def test_home_page_full_structure() -> None:
    """Valida a estrutura completa da página inicial."""
    page = home_page("SP", "Governador", "mapa")
    xml = fh.to_xml(page)
    assert "RADAR" in xml
    assert "Eleitoral" in xml
    # Botão da página sobre não deve mais existir no cabeçalho
    assert "Sobre o Projeto" not in xml
    assert 'href="/sobre"' not in xml
    # Novo rodapé com autoria, contatos e disclaimer
    assert "Desenvolvido por" in xml
    assert "Rodrigo Guimarães Araújo" in xml
    assert "mailto:ratopythonista@gmail.com" in xml
    assert "https://github.com/ratopythonista" in xml
    assert "https://www.linkedin.com/in/ratopythonista/" in xml
    assert "sem vínculo institucional com o Grupo Globo ou portal G1" in xml


def test_endpoint_home_get(client: TestClient) -> None:
    """Valida a resposta HTTP da rota raiz."""
    res = client.get("/")
    assert res.status_code == 200
    assert "<!doctype html>" in res.text.lower()
    assert "RADAR" in res.text
    assert "radar-content" in res.text


def test_endpoint_candidaturas_fragment(client: TestClient) -> None:
    """Valida o endpoint HTMX de fragmento parcial e fallback para página completa."""
    # Requisição com header HTMX retorna o fragmento
    res_htmx = client.get("/candidaturas?uf=RJ&cargo=Governador", headers={"HX-Request": "true"})
    assert res_htmx.status_code == 200
    assert "Rio de Janeiro" in res_htmx.text
    assert "svg-uf-RJ" in res_htmx.text
    assert "<!doctype html>" not in res_htmx.text.lower()

    # Requisição direta sem HTMX retorna a página completa
    res_direct = client.get("/candidaturas?uf=RJ&cargo=Governador")
    assert res_direct.status_code == 200
    assert "Rio de Janeiro" in res_direct.text
    assert "<!doctype html>" in res_direct.text.lower()


def test_endpoint_view_toggle(client: TestClient) -> None:
    """Valida a alternância de visão via endpoint HTMX."""
    res = client.get("/view-toggle?view=grade&uf=SP&cargo=Governador")
    assert res.status_code == 200
    assert "container-visual-grade" in res.text


def test_cargos_constants() -> None:
    """Valida que todos os cargos esperados estão no catálogo."""
    expected_cargos = [
        "Presidente",
        "Governador",
        "Senador",
        "Deputado Federal",
        "Deputado Estadual",
    ]
    assert expected_cargos == CARGOS
    assert len(CARGOS) == 5
