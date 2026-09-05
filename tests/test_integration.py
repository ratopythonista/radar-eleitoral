"""Testes de integração end-to-end do servidor WSGI, SEO/OpenGraph, PWA e infraestrutura."""

import json
from pathlib import Path

import pytest

from radar_eleitoral.app import server


@pytest.fixture
def client():
    """Fixture fornecendo o test client do servidor Flask/WSGI."""
    server.config["TESTING"] = True
    with server.test_client() as c:
        yield c


class TestWSGIServerIntegration:
    """Valida o seam do servidor WSGI e renderização SSR de HTML e metatags."""

    def test_home_page_status_and_pwa_meta(self, client):
        """Verifica se a rota raiz (/) retorna 200 com a casca HTML pt-BR e tags PWA."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        # Verificação da casca HTML e acessibilidade
        assert '<html lang="pt-BR"' in html
        assert 'name="theme-color" content="#040f0c"' in html
        assert 'name="viewport"' in html

        # Verificação de assets PWA injetados
        assert '<link rel="manifest" href="/assets/manifest.json"' in html
        assert '<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"' in html
        assert "serviceWorker" in html
        assert "/assets/sw.js" in html
        assert '<link rel="apple-touch-icon" href="/assets/icon-192.png"' in html

    def test_home_page_opengraph_meta_tags(self, client):
        """Verifica se a rota raiz inclui as tags OpenGraph e Twitter Card no primeiro render."""
        response = client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        assert 'property="og:site_name" content="Radar Eleitoral"' in html
        assert 'property="og:locale" content="pt_BR"' in html
        assert 'property="og:title"' in html
        assert 'property="og:description"' in html
        assert 'property="og:image"' in html
        assert "twitter:card" in html

    def test_sobre_page_status_and_content(self, client):
        """Verifica se a rota /sobre retorna 200 com metadados SEO e OpenGraph."""
        response = client.get("/sobre")
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        assert 'property="og:title"' in html
        assert 'property="og:description"' in html
        assert 'property="og:image"' in html

    def test_proxy_fix_canonical_https_resolution(self, client):
        """Verifica se o ProxyFix resolve URLs canônicas HTTPS sob headers de reverse proxy."""
        headers = {
            "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "radar-eleitoral.onrender.com",
            "X-Forwarded-For": "203.0.113.195",
        }
        response = client.get("/", headers=headers)
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        # Com ProxyFix ativo, URLs absolutas geradas pelo Dash SSR usam https e o host público
        assert "https://radar-eleitoral.onrender.com" in html
        assert "http://localhost" not in html

    def test_static_assets_serving(self, client):
        """Verifica se os arquivos estáticos de PWA e SEO são entregues corretamente via /assets/."""
        # 1. Manifest
        res_manifest = client.get("/assets/manifest.json")
        assert res_manifest.status_code == 200
        manifest_data = json.loads(res_manifest.get_data(as_text=True))
        assert manifest_data["short_name"] == "Radar Eleitoral"
        assert manifest_data["theme_color"] == "#040f0c"
        assert len(manifest_data["icons"]) >= 3

        # 2. Favicon SVG
        res_fav = client.get("/assets/favicon.svg")
        assert res_fav.status_code == 200
        assert "image/svg+xml" in res_fav.content_type

        # Favicon ICO (Tab icon para Dash e browsers legados)
        res_ico = client.get("/assets/favicon.ico")
        assert res_ico.status_code == 200
        assert (
            "image/x-icon" in res_ico.content_type
            or "image/vnd.microsoft.icon" in res_ico.content_type
        )

        res_dash_ico = client.get("/_favicon.ico")
        assert res_dash_ico.status_code == 200
        assert (
            "image/x-icon" in res_dash_ico.content_type
            or "image/vnd.microsoft.icon" in res_dash_ico.content_type
        )

        # 3. PWA Icons PNG
        res_192 = client.get("/assets/icon-192.png")
        assert res_192.status_code == 200
        assert "image/png" in res_192.content_type

        res_512 = client.get("/assets/icon-512.png")
        assert res_512.status_code == 200
        assert "image/png" in res_512.content_type

        # 4. Social Card PNG
        res_card = client.get("/assets/social-card.png")
        assert res_card.status_code == 200
        assert "image/png" in res_card.content_type
        # Peso menor que 300 KB exigido por scrapers
        assert len(res_card.data) < 300 * 1024

        # 5. Service Worker JS
        res_sw = client.get("/assets/sw.js")
        assert res_sw.status_code == 200
        assert "javascript" in res_sw.content_type


class TestDeploymentContracts:
    """Valida os arquivos de infraestrutura e contrato com o Render.com."""

    def test_render_blueprint_specification(self):
        """Verifica conformidade do render.yaml."""
        render_path = Path("render.yaml")
        assert render_path.exists(), "render.yaml deve existir na raiz"

        content = render_path.read_text(encoding="utf-8")
        assert "services:" in content
        assert "name: radar-eleitoral" in content
        assert "type: web" in content
        assert "runtime: docker" in content
        assert "plan: free" in content
        assert "healthCheckPath: /" in content
        assert "autoDeploy: true" in content

    def test_dockerignore_configuration(self):
        """Verifica se .dockerignore exclui diretórios e arquivos desnecessários."""
        dockerignore = Path(".dockerignore")
        assert dockerignore.exists(), ".dockerignore deve existir na raiz"
        content = dockerignore.read_text(encoding="utf-8")
        assert ".venv" in content
        assert "tests/" in content
        assert ".git" in content
        # .python-version NÃO deve ser ignorado pois é copiado no builder do Dockerfile
        assert ".python-version" not in content

    def test_dockerfile_multi_stage_and_security(self):
        """Verifica se Dockerfile segue o padrão multi-stage unprivileged."""
        dockerfile = Path("Dockerfile")
        assert dockerfile.exists()
        content = dockerfile.read_text(encoding="utf-8")

        assert "FROM python:3.12-slim AS builder" in content
        assert "FROM python:3.12-slim AS runner" in content
        assert "useradd" in content or "appuser" in content
        assert "USER appuser" in content
        assert "granian --interface wsgi" in content
        assert "${PORT:-8080}" in content
