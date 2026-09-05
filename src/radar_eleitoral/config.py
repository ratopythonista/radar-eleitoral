"""Configurações globais da aplicação Radar Eleitoral via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação e dados de apoio/contato."""

    model_config = SettingsConfigDict(
        env_prefix="RADAR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    # Ativos de branding e metadados
    default_social_card: str = "social-card.png"

    # Dados do Pix para sustentabilidade e apoio
    pix_key: str = "ratopythonista@noh.pix"
    pix_receiver_name: str = "Rodrigo Guimarães Araújo"
    pix_city: str = "Brasília"

    # Perfil profissional e redes sociais do autor
    author_name: str = "Rodrigo Guimarães Araújo"
    author_headline: str = (
        "Tech Lead & Engenheiro de Software | Especialista em Inteligência Artificial"
    )
    author_avatar_url: str = "https://github.com/ratopythonista.png"
    github_url: str = "https://github.com/ratopythonista"
    linkedin_url: str = "https://www.linkedin.com/in/ratopythonista/"
    instagram_url: str = "https://www.instagram.com/ratopythonista/"
    x_url: str = "https://x.com/ratopythonista"


# Instância padrão para injeção e consumo no app
settings = Settings()
