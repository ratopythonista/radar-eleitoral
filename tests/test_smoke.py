"""Smoke test for radar-eleitoral package."""

from radar_eleitoral import __version__


def test_version() -> None:
    assert __version__ == "0.1.0"
