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
    app_name: str = "Radar Eleitoral"
    app_description: str = (
        "Vitrine interativa de candidaturas e matérias jornalísticas automatizadas "
        "do G1 por estado e cargo em todo o Brasil."
    )
    default_social_card: str = "/static/social-card.png"

    # Perfil profissional e links de contato do autor
    author_name: str = "Rodrigo Guimarães Araújo"
    author_email: str = "ratopythonista@gmail.com"
    github_url: str = "https://github.com/ratopythonista"
    linkedin_url: str = "https://www.linkedin.com/in/ratopythonista/"


# Instância padrão para injeção e consumo no app
settings = Settings()
