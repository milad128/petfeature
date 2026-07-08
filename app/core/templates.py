"""Shared Jinja2 templates instance."""

from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from app.core.jalali import format_jalali, to_fa_digits

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
STATIC_DIR = Path(__file__).parent.parent / "static"

templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["jalali"] = format_jalali
templates.env.filters["fa_digits"] = to_fa_digits


def asset_url(request, path: str) -> str:
    """Static asset URL with a cache-busting query param based on file mtime.

    Without this, browsers can keep serving a stale cached copy of main.css/
    admin.js/library.js after a deploy since the URL never changes.

    Uses a root-relative path to avoid http/https mixed-content issues behind
    a TLS-terminating reverse proxy (e.g. Hamravesh Darkube ingress).
    """
    file_path = STATIC_DIR / path
    try:
        version = int(file_path.stat().st_mtime)
    except OSError:
        version = 0
    return f"/static/{path}?v={version}"


@pass_context
def url_for(context: dict, name: str, **path_params) -> str:
    """Root-relative url_for replacement.

    Starlette's built-in url_for() generates absolute URLs using the request
    scheme, which becomes http:// behind Hamravesh's TLS-terminating ingress.
    Browsers then block form submissions and resources as mixed content.
    Returning a root-relative path sidesteps this entirely.
    """
    request = context["request"]
    url = request.url_for(name, **path_params)
    return url.path


templates.env.globals["asset_url"] = asset_url
templates.env.globals["url_for"] = url_for
