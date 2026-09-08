"""Testes de regressão para persistência da visão [Mapa | Grade Regional] no FastHTML + HTMX.

Garante:
1. Alternância explícita para Grade Regional retorna o container da grade.
2. Alternância explícita para Mapa retorna o container do mapa SVG.
3. Navegação entre UFs sob a visão Grade preserva a visão ativa.
4. Carregamento inicial com parâmetro desktop_view='grade' respeita a preferência do usuário.
"""

import pytest
from starlette.testclient import TestClient

from radar_eleitoral.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_view_toggle_to_grade(client: TestClient) -> None:
    """Requisição de toggle para Grade Regional deve renderizar o container da grade."""
    res = client.get("/view-toggle?view=grade&uf=SP&cargo=Governador")
    assert res.status_code == 200
    assert "container-visual-grade" in res.text
    assert "container-visual-mapa" not in res.text


def test_view_toggle_to_mapa(client: TestClient) -> None:
    """Requisição de toggle para Mapa deve renderizar o container do mapa SVG."""
    res = client.get("/view-toggle?view=mapa&uf=SP&cargo=Governador")
    assert res.status_code == 200
    assert "container-visual-mapa" in res.text
    assert "container-visual-grade" not in res.text


def test_navigation_preserves_grade_view(client: TestClient) -> None:
    """Ao trocar de estado estando na visão grade, a resposta deve manter a visão grade."""
    res = client.get("/candidaturas?uf=RJ&cargo=Governador&desktop_view=grade")
    assert res.status_code == 200
    assert "container-visual-grade" in res.text
    assert "container-visual-mapa" not in res.text
    assert "Rio de Janeiro" in res.text


def test_home_initial_view_preserves_query_param(client: TestClient) -> None:
    """Carregamento da URL inicial com desktop_view='grade' deve iniciar diretamente na grade."""
    res = client.get("/?uf=MG&cargo=Governador&desktop_view=grade")
    assert res.status_code == 200
    assert "container-visual-grade" in res.text
    assert "container-visual-mapa" not in res.text
    assert "Minas Gerais" in res.text
