"""Smoke test for radar-eleitoral package."""

from radar_eleitoral import __version__


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_app_server_entrypoint() -> None:
    """Verify that radar_eleitoral.app exposes a valid WSGI callable server."""
    from radar_eleitoral.app import server

    assert callable(server)
    assert hasattr(server, "wsgi_app")


def test_healthz_endpoint() -> None:
    """Verify that /healthz returns 200 OK for lightweight keep-alive monitors."""
    from radar_eleitoral.app import server

    client = server.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.data == b"OK"
