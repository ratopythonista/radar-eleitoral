"""Radar Eleitoral - Ponto de entrada da aplicação FastHTML + HTMX (ASGI)."""

from pathlib import Path

from fasthtml import common as fh
from fasthtml.fastapp import fast_app
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from radar_eleitoral.config import settings
from radar_eleitoral.pages import home, sobre

STATIC_DIR = Path(__file__).parent / "static"

SW_SCRIPT = """
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js').catch(function() {});
    });
}
"""

GLOBAL_HEADERS = (
    fh.Meta(name="description", content=settings.app_description),
    fh.Meta(name="theme-color", content="#040f0c"),
    fh.Meta(name="apple-mobile-web-app-capable", content="yes"),
    fh.Meta(name="apple-mobile-web-app-status-bar-style", content="black-translucent"),
    fh.Meta(name="format-detection", content="telephone=no"),
    fh.Meta(name="robots", content="index, follow"),
    # Open Graph & Twitter
    fh.Meta(property="og:type", content="website"),
    fh.Meta(property="og:site_name", content=settings.app_name),
    fh.Meta(property="og:title", content=f"{settings.app_name} | Cobertura G1 de Candidaturas"),
    fh.Meta(property="og:description", content=settings.app_description),
    fh.Meta(property="og:image", content=settings.default_social_card),
    fh.Meta(name="twitter:card", content="summary_large_image"),
    fh.Meta(name="twitter:title", content=f"{settings.app_name} | Cobertura G1 de Candidaturas"),
    fh.Meta(name="twitter:description", content=settings.app_description),
    fh.Meta(name="twitter:image", content=settings.default_social_card),
    # Favicons & Manifest
    fh.Link(rel="icon", type="image/png", sizes="32x32", href="/static/icon-32.png"),
    fh.Link(rel="icon", type="image/svg+xml", href="/static/favicon.svg"),
    fh.Link(rel="apple-touch-icon", href="/static/icon-192.png"),
    fh.Link(rel="manifest", href="/static/manifest.json"),
    fh.Link(rel="stylesheet", href="/static/tailwind.css"),
    fh.Script(SW_SCRIPT),
)
app, rt = fast_app(
    pico=False,
    title=f"{settings.app_name} | Cobertura G1 de Candidaturas",
    htmlkw={"lang": "pt-BR", "cls": "h-full bg-[#040f0c]"},
    bodykw={"cls": "h-full bg-[#040f0c] text-slate-100 antialiased"},
    hdrs=GLOBAL_HEADERS,
    routes=(Mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static"),),
)


@app.route("/healthz", methods=["GET"])
def healthz() -> fh.Response:
    """Health check endpoint ultra-leve para pings de keep-alive externos."""
    return fh.Response("OK", media_type="text/plain")


# Registro modular das telas da aplicação
home.register(app)
sobre.register(app)
