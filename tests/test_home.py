"""Testes de unidade e integridade para a página Home do Radar Eleitoral."""

import pytest

import radar_eleitoral.app  # noqa: F401
from radar_eleitoral.candidaturas import CARGOS, UF_NAMES, get_hero_data
from radar_eleitoral.map_utils import create_brazil_map, load_brazil_geojson
from radar_eleitoral.pages.home import layout, render_active_content, render_home_content


def test_load_brazil_geojson() -> None:
    """Verifica se a malha GeoJSON do Brasil simplificada carrega corretamente."""
    geojson = load_brazil_geojson()
    assert geojson["type"] == "FeatureCollection"
    features = geojson["features"]
    assert len(features) == 27
    siglas = {f["properties"]["sigla"] for f in features}
    assert "SP" in siglas
    assert "RJ" in siglas
    assert "DF" in siglas


def test_candidaturas_data_presidente() -> None:
    """Valida contrato dos dados reais para Presidente (âmbito nacional)."""
    hero = get_hero_data("BR", "Presidente")
    assert hero.is_nacional is True
    assert hero.uf == "BR"
    assert hero.cargo == "Presidente"
    assert "Presidência da República" in hero.titulo
    assert hero.candidaturas > 0
    assert "g1.globo.com" in hero.url_g1


@pytest.mark.parametrize("uf", ["SP", "RJ", "MG", "BA", "RS"])
def test_candidaturas_data_estados(uf: str) -> None:
    """Valida dados para os estados com dataset real carregado."""
    hero = get_hero_data(uf, "Governador")
    assert hero.is_nacional is False
    assert hero.uf == uf
    assert hero.cargo == "Governador"
    assert hero.uf_nome == UF_NAMES[uf]
    assert hero.candidaturas > 0
    assert "g1.globo.com" in hero.url_g1


def test_candidaturas_data_fallback() -> None:
    """Valida fallback dinâmico determinístico para cargos não cadastrados."""
    hero = get_hero_data("AC", "Cargo Customizado")
    assert hero.uf == "AC"
    assert hero.cargo == "Cargo Customizado"
    assert hero.candidaturas > 0
    assert "Acre" in hero.titulo


def test_create_brazil_map() -> None:
    """Valida criação da figura Plotly na paleta Esmeralda para estados e Presidente."""
    fig_sp = create_brazil_map("SP", "Governador")
    assert fig_sp.data is not None
    assert len(fig_sp.data) > 0

    fig_pres = create_brazil_map("BR", "Presidente")
    assert fig_pres.data is not None
    assert len(fig_pres.data) > 0


def test_render_home_content() -> None:
    """Garante que a Home renderiza com dados ativos sem erros."""
    content_pres = render_home_content("Presidente", "BR")
    assert content_pres is not None

    content_gov = render_home_content("Governador", "SP")
    assert content_gov is not None


def test_layout_structure() -> None:
    """Valida montagem estática do layout da Home."""
    assert layout is not None


def test_render_active_content_callback() -> None:
    """Valida callback que atualiza o conteúdo da Home reativamente."""
    rendered = render_active_content("Governador", "SP")
    assert rendered is not None


def test_cargos_constants() -> None:
    """Valida que todos os cargos esperados estão no catálogo."""
    assert "Presidente" in CARGOS
    assert "Governador" in CARGOS
    assert "Senador" in CARGOS
    assert len(CARGOS) == 5
