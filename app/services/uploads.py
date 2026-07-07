"""Local file uploads for admin CMS."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

COVERS_DIR = Path(__file__).parent.parent / "static" / "uploads" / "covers"
COVERS_URL_PREFIX = "/static/uploads/covers/"
DOWNLOADS_DIR = Path(__file__).parent.parent / "static" / "uploads" / "downloads"
DOWNLOADS_URL_PREFIX = "/static/uploads/downloads/"
POST_COVERS_DIR = Path(__file__).parent.parent / "static" / "uploads" / "post-covers"
POST_COVERS_URL_PREFIX = "/static/uploads/post-covers/"
TOOL_COVERS_DIR = Path(__file__).parent.parent / "static" / "uploads" / "tool-covers"
TOOL_COVERS_URL_PREFIX = "/static/uploads/tool-covers/"
TOOL_FILES_DIR = Path(__file__).parent.parent / "static" / "uploads" / "tool-files"
TOOL_FILES_URL_PREFIX = "/static/uploads/tool-files/"

ALLOWED_COVER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_DOWNLOAD_EXTENSIONS = {".pdf"}
ALLOWED_TOOL_FILE_EXTENSIONS = {".pdf", ".xlsx", ".docx", ".pptx", ".csv"}
MAX_COVER_BYTES = 5 * 1024 * 1024
MAX_DOWNLOAD_BYTES = 25 * 1024 * 1024
MAX_TOOL_FILE_BYTES = 25 * 1024 * 1024


def ensure_upload_dirs() -> None:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    POST_COVERS_DIR.mkdir(parents=True, exist_ok=True)
    TOOL_COVERS_DIR.mkdir(parents=True, exist_ok=True)
    TOOL_FILES_DIR.mkdir(parents=True, exist_ok=True)


def is_local_tool_cover(path: Optional[str]) -> bool:
    return bool(path and path.startswith(TOOL_COVERS_URL_PREFIX))


def delete_local_tool_cover(path: Optional[str]) -> None:
    if not is_local_tool_cover(path):
        return
    filename = path.removeprefix(TOOL_COVERS_URL_PREFIX)
    file_path = TOOL_COVERS_DIR / filename
    if file_path.is_file():
        file_path.unlink()


async def save_tool_cover_upload(file: UploadFile, slug: str) -> str:
    if not file.filename:
        raise ValueError("فایل تصویر انتخاب نشده است.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_COVER_EXTENSIONS:
        raise ValueError("فرمت تصویر مجاز نیست. از JPG، PNG، WebP یا GIF استفاده کنید.")

    content = await file.read()
    if not content:
        raise ValueError("فایل تصویر خالی است.")
    if len(content) > MAX_COVER_BYTES:
        raise ValueError("حجم تصویر نباید بیشتر از ۵ مگابایت باشد.")

    ensure_upload_dirs()
    filename = f"{_safe_slug(slug)}-{uuid.uuid4().hex[:8]}{ext}"
    (TOOL_COVERS_DIR / filename).write_bytes(content)
    return f"{TOOL_COVERS_URL_PREFIX}{filename}"


async def resolve_tool_cover(
    existing_cover: str,
    cover_file: Optional[UploadFile],
    slug: str,
    *,
    old_cover: Optional[str] = None,
) -> str:
    if cover_file and cover_file.filename:
        new_path = await save_tool_cover_upload(cover_file, slug)
        if old_cover and old_cover != new_path:
            delete_local_tool_cover(old_cover)
        return new_path
    return existing_cover.strip()


def is_local_tool_file(path: Optional[str]) -> bool:
    return bool(path and path.startswith(TOOL_FILES_URL_PREFIX))


def delete_local_tool_file(path: Optional[str]) -> None:
    if not is_local_tool_file(path):
        return
    filename = path.removeprefix(TOOL_FILES_URL_PREFIX)
    file_path = TOOL_FILES_DIR / filename
    if file_path.is_file():
        file_path.unlink()


async def save_tool_file_upload(file: UploadFile, slug: str) -> str:
    if not file.filename:
        raise ValueError("فایلی انتخاب نشده است.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_TOOL_FILE_EXTENSIONS:
        raise ValueError("فرمت فایل مجاز نیست. از PDF، Excel، Word، PowerPoint یا CSV استفاده کنید.")

    content = await file.read()
    if not content:
        raise ValueError("فایل انتخاب‌شده خالی است.")
    if len(content) > MAX_TOOL_FILE_BYTES:
        raise ValueError("حجم فایل نباید بیشتر از ۲۵ مگابایت باشد.")

    ensure_upload_dirs()
    filename = f"{_safe_slug(slug)}-{uuid.uuid4().hex[:8]}{ext}"
    (TOOL_FILES_DIR / filename).write_bytes(content)
    return f"{TOOL_FILES_URL_PREFIX}{filename}"


async def resolve_tool_file(
    existing_file: str,
    upload: Optional[UploadFile],
    slug: str,
    *,
    old_file: Optional[str] = None,
) -> str:
    if upload and upload.filename:
        new_path = await save_tool_file_upload(upload, slug)
        if old_file and old_file != new_path:
            delete_local_tool_file(old_file)
        return new_path
    return existing_file.strip()


def is_local_post_cover(path: Optional[str]) -> bool:
    return bool(path and path.startswith(POST_COVERS_URL_PREFIX))


def delete_local_post_cover(path: Optional[str]) -> None:
    if not is_local_post_cover(path):
        return
    filename = path.removeprefix(POST_COVERS_URL_PREFIX)
    file_path = POST_COVERS_DIR / filename
    if file_path.is_file():
        file_path.unlink()


async def save_post_cover_upload(file: UploadFile, slug: str) -> str:
    if not file.filename:
        raise ValueError("فایل تصویر انتخاب نشده است.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_COVER_EXTENSIONS:
        raise ValueError("فرمت تصویر مجاز نیست. از JPG، PNG، WebP یا GIF استفاده کنید.")

    content = await file.read()
    if not content:
        raise ValueError("فایل تصویر خالی است.")
    if len(content) > MAX_COVER_BYTES:
        raise ValueError("حجم تصویر نباید بیشتر از ۵ مگابایت باشد.")

    ensure_upload_dirs()
    filename = f"{_safe_slug(slug)}-{uuid.uuid4().hex[:8]}{ext}"
    (POST_COVERS_DIR / filename).write_bytes(content)
    return f"{POST_COVERS_URL_PREFIX}{filename}"


async def resolve_post_cover(
    existing_cover: str,
    cover_file: Optional[UploadFile],
    slug: str,
    *,
    old_cover: Optional[str] = None,
) -> str:
    if cover_file and cover_file.filename:
        new_path = await save_post_cover_upload(cover_file, slug)
        if old_cover and old_cover != new_path:
            delete_local_post_cover(old_cover)
        return new_path
    return existing_cover.strip()


def is_local_cover(path: Optional[str]) -> bool:
    return bool(path and path.startswith(COVERS_URL_PREFIX))


def is_local_download(path: Optional[str]) -> bool:
    return bool(path and path.startswith(DOWNLOADS_URL_PREFIX))


def delete_local_cover(path: Optional[str]) -> None:
    if not is_local_cover(path):
        return
    filename = path.removeprefix(COVERS_URL_PREFIX)
    file_path = COVERS_DIR / filename
    if file_path.is_file():
        file_path.unlink()


def delete_local_download(path: Optional[str]) -> None:
    if not is_local_download(path):
        return
    filename = path.removeprefix(DOWNLOADS_URL_PREFIX)
    file_path = DOWNLOADS_DIR / filename
    if file_path.is_file():
        file_path.unlink()


def _safe_slug(slug: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", slug.lower()) or "file"


async def save_cover_upload(file: UploadFile, slug: str) -> str:
    if not file.filename:
        raise ValueError("فایل تصویر انتخاب نشده است.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_COVER_EXTENSIONS:
        raise ValueError("فرمت تصویر مجاز نیست. از JPG، PNG، WebP یا GIF استفاده کنید.")

    content = await file.read()
    if not content:
        raise ValueError("فایل تصویر خالی است.")
    if len(content) > MAX_COVER_BYTES:
        raise ValueError("حجم تصویر نباید بیشتر از ۵ مگابایت باشد.")

    ensure_upload_dirs()
    filename = f"{_safe_slug(slug)}-{uuid.uuid4().hex[:8]}{ext}"
    (COVERS_DIR / filename).write_bytes(content)
    return f"{COVERS_URL_PREFIX}{filename}"


async def save_download_upload(file: UploadFile, slug: str) -> str:
    if not file.filename:
        raise ValueError("فایل PDF انتخاب نشده است.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_DOWNLOAD_EXTENSIONS:
        raise ValueError("فقط فایل PDF مجاز است.")

    content = await file.read()
    if not content:
        raise ValueError("فایل PDF خالی است.")
    if len(content) > MAX_DOWNLOAD_BYTES:
        raise ValueError("حجم فایل PDF نباید بیشتر از ۲۵ مگابایت باشد.")

    ensure_upload_dirs()
    filename = f"{_safe_slug(slug)}-{uuid.uuid4().hex[:8]}{ext}"
    (DOWNLOADS_DIR / filename).write_bytes(content)
    return f"{DOWNLOADS_URL_PREFIX}{filename}"


async def resolve_cover(
    existing_cover: str,
    cover_file: Optional[UploadFile],
    slug: str,
    *,
    old_cover: Optional[str] = None,
) -> str:
    if cover_file and cover_file.filename:
        new_path = await save_cover_upload(cover_file, slug)
        if old_cover and old_cover != new_path:
            delete_local_cover(old_cover)
        return new_path
    return existing_cover.strip()


async def resolve_download(
    existing_download: str,
    download_file: Optional[UploadFile],
    slug: str,
    *,
    old_download: Optional[str] = None,
) -> str:
    if download_file and download_file.filename:
        new_path = await save_download_upload(download_file, slug)
        if old_download and old_download != new_path:
            delete_local_download(old_download)
        return new_path
    return existing_download.strip()
