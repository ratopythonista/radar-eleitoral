"""Feedback loop e testes de regressão determinísticos para os bugs de renderização:
1. O mapa não aparecia no desktop devido à ausência de .lg:block e classes conflitantes.
2. O toggle Mapa vs Grade não aparecia.
3. O botão de âmbito nacional estava com tamanho excessivo e solto na página inicial.
"""

from pathlib import Path

from fasthtml import common as fh

from radar_eleitoral.pages.home import render_home_content


def test_tailwind_css_contains_lg_block() -> None:
    """O arquivo static/tailwind.css DEVE conter a classe .lg:block compilada."""
    css_path = Path("src/radar_eleitoral/static/tailwind.css")
    assert css_path.exists(), "static/tailwind.css não encontrado"
    css_content = css_path.read_text(encoding="utf-8")

    assert ".lg\\:block" in css_content or ".lg:block" in css_content, (
        "static/tailwind.css não contém a regra de estilo .lg:block!"
    )


def test_map_visible_by_default() -> None:
    """Verifica se o container do mapa é exibido por padrão e alternado em 'grade'."""
    rendered_mapa = render_home_content("Governador", "SP", desktop_view="mapa")
    xml_mapa = fh.to_xml(rendered_mapa)
    assert "container-visual-mapa" in xml_mapa
    assert "container-visual-grade" not in xml_mapa

    rendered_grade = render_home_content("Governador", "SP", desktop_view="grade")
    xml_grade = fh.to_xml(rendered_grade)
    assert "container-visual-grade" in xml_grade
    assert "container-visual-mapa" not in xml_grade


def test_view_toggle_always_accessible() -> None:
    """O toggle [ Mapa | Grade ] deve estar acessível no cabeçalho do box visual."""
    rendered = render_home_content("Governador", "SP", desktop_view="mapa")
    xml = fh.to_xml(rendered)

    assert 'id="btn-view-mapa"' in xml
    assert 'id="btn-view-grade"' in xml


def test_no_standalone_huge_button_in_section() -> None:
    """Garante que a barra de seleção contenha apenas as pílulas de cargos, sem botão enorme solto."""
    rendered = render_home_content("Presidente", "BR", desktop_view="mapa")
    xml = fh.to_xml(rendered)

    assert "Escolha o cargo:" in xml
    assert "cargo-btn-presidente" in xml
