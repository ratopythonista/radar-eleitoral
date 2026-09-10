"""Testes unitários para a configuração global da aplicação."""

from radar_eleitoral.config import Settings


def test_settings_author_and_contact_defaults() -> None:
    """Valida valores padrão para autoria e links de contato no rodapé."""
    cfg = Settings()
    assert cfg.author_name == "Rodrigo Guimarães Araújo"
    assert cfg.author_email == "ratopythonista@gmail.com"
    assert cfg.github_url == "https://github.com/ratopythonista"
    assert cfg.linkedin_url == "https://www.linkedin.com/in/ratopythonista/"

    # Campos removidos não devem existir no modelo
    assert not hasattr(cfg, "pix_key")
    assert not hasattr(cfg, "pix_receiver_name")
    assert not hasattr(cfg, "pix_city")
    assert not hasattr(cfg, "instagram_url")
    assert not hasattr(cfg, "x_url")
    assert not hasattr(cfg, "author_headline")
    assert not hasattr(cfg, "author_avatar_url")
