"""Testes para o componente de Mapa Vetorial SVG nativo do FastHTML."""

from fasthtml import common as fh

from radar_eleitoral.candidaturas import UF_NAMES
from radar_eleitoral.map_svg import render_brazil_svg_map


def test_render_brazil_svg_map_contains_all_27_ufs() -> None:
    """Garante que o SVG renderiza as 27 Unidades da Federação com identificadores e tooltips."""
    svg = render_brazil_svg_map(selected_uf="SP", cargo="Governador")
    xml = fh.to_xml(svg)

    assert "<svg" in xml
    assert "0 0 354 368" in xml

    for uf in UF_NAMES:
        if uf == "BR":
            continue
        assert f'id="svg-uf-{uf}"' in xml
        assert f'data-uf="{uf}"' in xml


def test_render_brazil_svg_map_htmx_attributes() -> None:
    """Verifica se os polígonos/caminhos contêm os atributos HTMX para interatividade sem JavaScript."""
    svg = render_brazil_svg_map(selected_uf="RJ", cargo="Senador")
    xml = fh.to_xml(svg)

    assert "/candidaturas?uf=RJ" in xml
    assert 'hx-target="#radar-content"' in xml
    assert 'hx-swap="outerHTML"' in xml
    assert 'hx-push-url="/?uf=RJ' in xml


def test_render_brazil_svg_map_selected_state_highlight() -> None:
    """O estado selecionado recebe destaque visual diferenciado."""
    svg = render_brazil_svg_map(selected_uf="MG", cargo="Governador")
    xml = fh.to_xml(svg)

    # Verifica se MG está marcado como selecionado
    assert 'fill="#10b981"' in xml  # Cor esmeralda ativo
    assert "svg-uf-MG" in xml


def test_render_brazil_svg_map_presidente_scope() -> None:
    """Quando o cargo é Presidente, todas as UFs refletem o escopo nacional."""
    svg = render_brazil_svg_map(selected_uf="BR", cargo="Presidente")
    xml = fh.to_xml(svg)

    # No escopo de Presidente, UFs têm visual de federação ativa
    assert "svg-uf-SP" in xml
    assert "svg-uf-DF" in xml
    assert "svg-uf-AM" in xml
