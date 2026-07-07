"""Shared Jinja2 templates instance."""

from pathlib import Path

from fastapi.templating import Jinja2Templates

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
    """
    url = request.url_for("static", path=path)
    file_path = STATIC_DIR / path
    try:
        version = int(file_path.stat().st_mtime)
    except OSError:
        version = 0
    return f"{url}?v={version}"


templates.env.globals["asset_url"] = asset_url
