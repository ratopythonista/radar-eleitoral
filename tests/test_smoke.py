"""Smoke test for radar-eleitoral package."""

from starlette.testclient import TestClient

from radar_eleitoral import __version__
from radar_eleitoral.main import app


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_app_server_entrypoint() -> None:
    """Verify that radar_eleitoral.main exposes a valid ASGI application."""
    assert callable(app)


def test_healthz_endpoint() -> None:
    """Verify that /healthz returns 200 OK for lightweight keep-alive monitors."""
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.text == "OK"
