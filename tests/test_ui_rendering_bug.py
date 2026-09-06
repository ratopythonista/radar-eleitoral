"""Feedback loop e testes de regressão determinísticos para os bugs de renderização:
1. O mapa não aparecia no desktop devido à ausência de .lg:block e classes conflitantes.
2. O toggle Mapa vs Grade não aparecia.
3. O botão de âmbito nacional estava com tamanho excessivo e solto na página inicial.
"""

from pathlib import Path


def test_tailwind_css_contains_lg_block() -> None:
    """O arquivo assets/tailwind.css DEVE conter a classe .lg:block compilada."""
    css_path = Path("src/radar_eleitoral/assets/tailwind.css")
    assert css_path.exists(), "assets/tailwind.css não encontrado"
    css_content = css_path.read_text(encoding="utf-8")

    assert ".lg\\:block" in css_content or ".lg:block" in css_content, (
        "assets/tailwind.css não contém a regra de estilo .lg:block!"
    )


def test_map_visible_by_default() -> None:
    """Verifica se o container do mapa é exibido com 'block' por padrão e oculto em 'grade'."""
    import radar_eleitoral.app  # noqa: F401
    from radar_eleitoral.pages.home import render_home_content

    rendered_mapa = render_home_content("Governador", "SP", desktop_view="mapa")
    assert isinstance(rendered_mapa.children, list)
    main_el = rendered_mapa.children[2]
    assert hasattr(main_el, "children") and isinstance(main_el.children, list)
    col_visual = main_el.children[0]
    assert hasattr(col_visual, "children") and isinstance(col_visual.children, list)
    box_el = col_visual.children[0]
    assert hasattr(box_el, "children") and isinstance(box_el.children, list)
    map_container = box_el.children[1]
    grade_container = box_el.children[2]

    assert map_container.className == "block"
    assert grade_container.className == "hidden"

    # Na visão 'grade', o container do mapa é hidden e o da grade é block
    rendered_grade = render_home_content("Governador", "SP", desktop_view="grade")
    assert isinstance(rendered_grade.children, list)
    main_grade = rendered_grade.children[2]
    assert hasattr(main_grade, "children") and isinstance(main_grade.children, list)
    box_el_grade = main_grade.children[0].children[0]
    assert hasattr(box_el_grade, "children") and isinstance(box_el_grade.children, list)
    assert box_el_grade.children[1].className == "hidden"
    assert box_el_grade.children[2].className == "block"


def test_view_toggle_always_accessible() -> None:
    """O toggle [ Mapa | Grade ] deve estar acessível no cabeçalho do box visual."""
    import radar_eleitoral.app  # noqa: F401
    from radar_eleitoral.pages.home import render_home_content

    rendered = render_home_content("Governador", "SP", desktop_view="mapa")
    assert isinstance(rendered.children, list)
    header_el = rendered.children[2].children[0].children[0].children[0]
    assert hasattr(header_el, "children") and isinstance(header_el.children, list)
    toggle_el = header_el.children[1]
    assert hasattr(toggle_el, "children") and isinstance(toggle_el.children, list)

    btn_ids = [btn.id for btn in toggle_el.children]
    assert "btn-view-mapa" in btn_ids
    assert "btn-view-grade" in btn_ids


def test_no_standalone_huge_button_in_section() -> None:
    """Garante que a barra de seleção contenha apenas as pílulas de cargos, sem botão enorme solto."""
    import radar_eleitoral.app  # noqa: F401
    from radar_eleitoral.pages.home import render_home_content

    rendered = render_home_content("Presidente", "BR", desktop_view="mapa")
    assert isinstance(rendered.children, list)
    section_el = rendered.children[1]
    assert hasattr(section_el, "children") and isinstance(section_el.children, list)

    assert len(section_el.children) == 1
    container_div = section_el.children[0]
    assert hasattr(container_div, "children") and isinstance(container_div.children, list)
    assert "Escolha o cargo:" in container_div.children[0].children
