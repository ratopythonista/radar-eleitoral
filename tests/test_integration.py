"""Testes de integração end-to-end do servidor ASGI, SEO/OpenGraph, PWA e infraestrutura."""

import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from radar_eleitoral.main import app


@pytest.fixture
def client() -> TestClient:
    """Fixture fornecendo o test client do servidor ASGI Starlette/FastHTML."""
    return TestClient(app)


class TestASGIServerIntegration:
    """Valida o seam do servidor ASGI e renderização SSR de HTML e metatags."""

    def test_home_page_status_and_pwa_meta(self, client: TestClient) -> None:
        """Verifica se a rota raiz (/) retorna 200 com a casca HTML pt-BR e tags PWA."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        # Verificação da casca HTML e acessibilidade
        assert 'lang="pt-BR"' in html
        assert 'name="theme-color" content="#040f0c"' in html
        assert 'name="viewport"' in html

        # Verificação de assets PWA injetados
        assert '<link rel="manifest" href="/static/manifest.json"' in html
        assert '<link rel="icon" type="image/svg+xml" href="/static/favicon.svg"' in html
        assert "serviceWorker" in html
        assert "/static/sw.js" in html
        assert '<link rel="apple-touch-icon" href="/static/icon-192.png"' in html

    def test_home_page_opengraph_meta_tags(self, client: TestClient) -> None:
        """Verifica se a rota raiz inclui as tags OpenGraph e Twitter Card no primeiro render."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.text

        assert 'property="og:site_name" content="Radar Eleitoral"' in html
        assert 'property="og:title"' in html
        assert 'property="og:description"' in html
        assert 'property="og:image"' in html
        assert 'name="twitter:card"' in html

    def test_sobre_page_status_and_content(self, client: TestClient) -> None:
        """Verifica se a rota /sobre retorna 200 com conteúdo e layout preservados."""
        response = client.get("/sobre")
        assert response.status_code == 200
        html = response.text

        assert "Democratizando o Acesso" in html
        assert "Voltar ao Mapa" in html
        assert "copyPixKey" in html

    def test_static_assets_serving(self, client: TestClient) -> None:
        """Verifica se os arquivos estáticos de PWA e SEO são entregues corretamente via /static/."""
        # 1. Manifest
        res_manifest = client.get("/static/manifest.json")
        assert res_manifest.status_code == 200
        manifest_data = json.loads(res_manifest.text)
        assert manifest_data["short_name"] == "Radar Eleitoral"
        assert manifest_data["theme_color"] == "#040f0c"
        assert len(manifest_data["icons"]) >= 3

        # 2. Favicon SVG
        res_fav = client.get("/static/favicon.svg")
        assert res_fav.status_code == 200
        assert "image/svg+xml" in res_fav.headers.get("content-type", "")

        # 3. Favicon ICO
        res_ico = client.get("/static/favicon.ico")
        assert res_ico.status_code == 200

        # 4. Ícones PWA
        res_icon192 = client.get("/static/icon-192.png")
        assert res_icon192.status_code == 200
        assert "image/png" in res_icon192.headers.get("content-type", "")

        res_icon512 = client.get("/static/icon-512.png")
        assert res_icon512.status_code == 200

        # 5. Imagem de Card Social
        res_social = client.get("/static/social-card.png")
        assert res_social.status_code == 200

        # 6. Folha de estilos compilada Tailwind CSS
        res_css = client.get("/static/tailwind.css")
        assert res_css.status_code == 200
        assert "text/css" in res_css.headers.get("content-type", "")

        # 7. Service Worker
        res_sw = client.get("/static/sw.js")
        assert res_sw.status_code == 200
        assert "javascript" in res_sw.headers.get("content-type", "")


class TestDeploymentContracts:
    """Valida os arquivos de infraestrutura e contrato com o Render.com."""

    def test_render_blueprint_specification(self) -> None:
        """Verifica conformidade do render.yaml."""
        render_path = Path("render.yaml")
        assert render_path.exists(), "render.yaml não encontrado na raiz"
        content = render_path.read_text(encoding="utf-8")

        assert "name: radar-eleitoral" in content
        assert "runtime: docker" in content
        assert "healthCheckPath: /healthz" in content
        assert "autoDeploy: true" in content

    def test_dockerignore_configuration(self) -> None:
        """Verifica se .dockerignore exclui diretórios e arquivos desnecessários."""
        dockerignore_path = Path(".dockerignore")
        assert dockerignore_path.exists(), ".dockerignore não encontrado"
        content = dockerignore_path.read_text(encoding="utf-8")

        assert ".git" in content
        assert ".venv" in content
        assert "__pycache__" in content

    def test_dockerfile_multi_stage_and_security(self) -> None:
        """Verifica se Dockerfile segue o padrão multi-stage unprivileged para ASGI."""
        dockerfile_path = Path("Dockerfile")
        assert dockerfile_path.exists(), "Dockerfile não encontrado"
        content = dockerfile_path.read_text(encoding="utf-8")

        assert "FROM python:3.12-slim AS builder" in content
        assert "FROM python:3.12-slim AS runner" in content
        assert "USER appuser" in content
        assert "--interface asgi" in content
        assert "radar_eleitoral.main:app" in content
        assert "${PORT:-8080}" in content
