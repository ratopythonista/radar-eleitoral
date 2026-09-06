"""Testes para o Cartograma Regional e regras de seleção inteligente."""

from dash import html

from radar_eleitoral.candidaturas import UF_NAMES
from radar_eleitoral.cartograma import (
    REGIOES_BRASIL,
    render_cartograma_regional,
    render_nacional_button,
    render_view_toggle,
    resolve_smart_selection,
)


def test_regioes_brasil_completeness() -> None:
    """Garante que as 5 macrorregiões contêm exatamente as 27 UFs brasileiras sem duplicidade."""
    assert set(REGIOES_BRASIL.keys()) == {
        "Norte",
        "Nordeste",
        "Centro-Oeste",
        "Sudeste",
        "Sul",
    }

    all_ufs: list[str] = []
    for ufs in REGIOES_BRASIL.values():
        all_ufs.extend(ufs)

    # 26 estados + 1 DF = 27 UFs
    assert len(all_ufs) == 27
    assert len(set(all_ufs)) == 27
    expected_ufs = set(UF_NAMES.keys()) - {"BR"}
    assert set(all_ufs) == expected_ufs


def test_resolve_smart_selection_from_presidente() -> None:
    """Ao clicar em uma UF com Presidente ativo, troca para Governador (ou Deputado Distrital se DF)."""
    cargo, uf = resolve_smart_selection(clicked_uf="SP", current_cargo="Presidente")
    assert cargo == "Governador"
    assert uf == "SP"

    cargo_df, uf_df = resolve_smart_selection(clicked_uf="DF", current_cargo="Presidente")
    assert cargo_df == "Deputado Distrital"
    assert uf_df == "DF"


def test_resolve_smart_selection_nacional_click() -> None:
    """Ao clicar no botão nacional BR, seleciona Presidente e BR."""
    cargo, uf = resolve_smart_selection(clicked_uf="BR", current_cargo="Governador")
    assert cargo == "Presidente"
    assert uf == "BR"


def test_resolve_smart_selection_df_deputado() -> None:
    """Alternância automática entre Deputado Estadual e Deputado Distrital."""
    # Se estiver em Deputado Estadual e clicar no DF -> Deputado Distrital
    cargo, uf = resolve_smart_selection(clicked_uf="DF", current_cargo="Deputado Estadual")
    assert cargo == "Deputado Distrital"
    assert uf == "DF"

    # Se estiver em Deputado Distrital e clicar em SP -> Deputado Estadual
    cargo_sp, uf_sp = resolve_smart_selection(clicked_uf="SP", current_cargo="Deputado Distrital")
    assert cargo_sp == "Deputado Estadual"
    assert uf_sp == "SP"


def test_resolve_smart_selection_regular() -> None:
    """Seleção normal preserva o cargo atual."""
    cargo, uf = resolve_smart_selection(clicked_uf="RJ", current_cargo="Senador")
    assert cargo == "Senador"
    assert uf == "RJ"


def test_render_cartograma_regional_structure() -> None:
    """Gera componente com as 5 macrorregiões e 27 botões de UF."""
    comp = render_cartograma_regional(selected_uf="SP", selected_cargo="Governador")
    assert isinstance(comp, html.Div)


def test_render_nacional_button() -> None:
    """Gera o botão de destaque Brasil (Nacional)."""
    btn_active = render_nacional_button(selected_cargo="Presidente")
    assert isinstance(btn_active, html.Button)

    btn_inactive = render_nacional_button(selected_cargo="Governador")
    assert isinstance(btn_inactive, html.Button)


def test_render_view_toggle() -> None:
    """Gera os botões de alternância Mapa vs Grade."""
    toggle = render_view_toggle(active_view="mapa")
    assert isinstance(toggle, html.Div)
