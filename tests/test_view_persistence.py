"""Testes de regressão para persistência da visão de grade regional ao navegar entre UFs.

Cenário: Ao navegar na visão de grade regional ('grade'), o clique em botões de estado (UFs)
provoca re-renderização do container principal. A remontagem dos botões de alternância
(btn-view-mapa e btn-view-grade) disparava o callback update_desktop_view indevidamente,
revertendo para a visão de mapa ('mapa').

Este arquivo garante:
1. Remontagem de botões preserva a visão ativa ('grade').
2. Clique explícito do usuário em 'btn-view-mapa' altera para 'mapa'.
3. Clique explícito do usuário em 'btn-view-grade' altera para 'grade'.
4. Fluxo completo: seleção de UF pelo cartograma preserva a visão de grade no DOM e no store.
"""

import pytest

from radar_eleitoral.app import server
from radar_eleitoral.pages.home import render_home_content


@pytest.fixture
def client():
    """Test client do Flask/WSGI do Dash."""
    server.config["TESTING"] = True
    with server.test_client() as c:
        yield c


def test_remount_does_not_revert_grade_view_to_mapa(client) -> None:
    """Quando a visão 'grade' está ativa, a remontagem dos botões não deve reverter para 'mapa'."""
    req_body = {
        "output": "store-desktop-view.data",
        "outputs": {"id": "store-desktop-view", "property": "data"},
        "inputs": [
            {"id": "btn-view-mapa", "property": "n_clicks", "value": 0},
            {"id": "btn-view-grade", "property": "n_clicks", "value": 0},
        ],
        "changedPropIds": ["btn-view-mapa.n_clicks", "btn-view-grade.n_clicks"],
        "state": [{"id": "store-desktop-view", "property": "data", "value": "grade"}],
    }

    resp = client.post("/_dash-update-component", json=req_body)
    assert resp.status_code == 200
    data = resp.get_json()

    result_view = data.get("response", {}).get("store-desktop-view", {}).get("data")
    assert result_view == "grade", (
        f"A visão foi revertida indevidamente para '{result_view}' em vez de 'grade'! Resposta: {data}"
    )


def test_user_click_btn_view_mapa_switches_to_mapa(client) -> None:
    """Clique explícito do usuário no botão Mapa deve alternar para 'mapa'."""
    req_body = {
        "output": "store-desktop-view.data",
        "outputs": {"id": "store-desktop-view", "property": "data"},
        "inputs": [
            {"id": "btn-view-mapa", "property": "n_clicks", "value": 1},
            {"id": "btn-view-grade", "property": "n_clicks", "value": 0},
        ],
        "changedPropIds": ["btn-view-mapa.n_clicks"],
        "state": [{"id": "store-desktop-view", "property": "data", "value": "grade"}],
    }

    resp = client.post("/_dash-update-component", json=req_body)
    assert resp.status_code == 200
    data = resp.get_json()

    result_view = data.get("response", {}).get("store-desktop-view", {}).get("data")
    assert result_view == "mapa"


def test_user_click_btn_view_grade_switches_to_grade(client) -> None:
    """Clique explícito do usuário no botão Grade deve alternar para 'grade'."""
    req_body = {
        "output": "store-desktop-view.data",
        "outputs": {"id": "store-desktop-view", "property": "data"},
        "inputs": [
            {"id": "btn-view-mapa", "property": "n_clicks", "value": 0},
            {"id": "btn-view-grade", "property": "n_clicks", "value": 1},
        ],
        "changedPropIds": ["btn-view-grade.n_clicks"],
        "state": [{"id": "store-desktop-view", "property": "data", "value": "mapa"}],
    }

    resp = client.post("/_dash-update-component", json=req_body)
    assert resp.status_code == 200
    data = resp.get_json()

    result_view = data.get("response", {}).get("store-desktop-view", {}).get("data")
    assert result_view == "grade"


def test_state_click_in_grade_view_end_to_end(client) -> None:
    """Fluxo e2e: usuário na visão grade clica em UF diferente; o layout e o store mantêm grade."""
    # 1. Clique em botão de estado no Cartograma (ex: 'RJ')
    cartograma_click_req = {
        "output": "..store-cargo.data...store-uf.data..",
        "outputs": [
            {"id": "store-cargo", "property": "data"},
            {"id": "store-uf", "property": "data"},
        ],
        "inputs": [
            [
                {
                    "id": {"cargo": "Governador", "type": "cargo-btn"},
                    "property": "n_clicks",
                    "value": 0,
                }
            ],
            [
                {
                    "id": {"index": "RJ", "type": "cartograma-uf-btn"},
                    "property": "n_clicks",
                    "value": 1,
                }
            ],
            {"id": "map-graph", "property": "clickData", "value": None},
        ],
        "changedPropIds": ['{"index":"RJ","type":"cartograma-uf-btn"}.n_clicks'],
        "state": [
            {"id": "store-cargo", "property": "data", "value": "Governador"},
            {"id": "store-uf", "property": "data", "value": "SP"},
        ],
    }

    resp_filter = client.post("/_dash-update-component", json=cartograma_click_req)
    assert resp_filter.status_code == 200
    filter_data = resp_filter.get_json().get("response", {})
    new_cargo = filter_data.get("store-cargo", {}).get("data", "Governador")
    new_uf = filter_data.get("store-uf", {}).get("data")
    assert new_uf == "RJ"

    # 2. Renderização do conteúdo com desktop_view='grade'
    rendered = render_home_content(new_cargo, new_uf, desktop_view="grade")
    assert isinstance(rendered.children, list)
    main_el = rendered.children[2]
    assert hasattr(main_el, "children") and isinstance(main_el.children, list)
    col_visual = main_el.children[0]
    assert hasattr(col_visual, "children") and isinstance(col_visual.children, list)
    box_el = col_visual.children[0]
    assert hasattr(box_el, "children") and isinstance(box_el.children, list)
    map_container = box_el.children[1]
    grade_container = box_el.children[2]

    # Na visão grade, o container do mapa deve estar oculto e o da grade visível
    assert map_container.className == "hidden"
    assert grade_container.className == "block"

    # 3. Disparo de remontagem que o Dash executa em seguida
    remount_req = {
        "output": "store-desktop-view.data",
        "outputs": {"id": "store-desktop-view", "property": "data"},
        "inputs": [
            {"id": "btn-view-mapa", "property": "n_clicks", "value": 0},
            {"id": "btn-view-grade", "property": "n_clicks", "value": 0},
        ],
        "changedPropIds": ["btn-view-mapa.n_clicks", "btn-view-grade.n_clicks"],
        "state": [{"id": "store-desktop-view", "property": "data", "value": "grade"}],
    }
    resp_view = client.post("/_dash-update-component", json=remount_req)
    assert resp_view.status_code == 200
    view_data = resp_view.get_json()
    final_view = view_data.get("response", {}).get("store-desktop-view", {}).get("data")
    assert final_view == "grade", f"Visão reverteu indevidamente para {final_view}!"
