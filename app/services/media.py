"""Service layer for the admin media library."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media_file import MediaFile
from app.services.uploads import MEDIA_DIR, ensure_upload_dirs

logger = logging.getLogger(__name__)

ALLOWED_TYPES: dict[str, str] = {
    "application/pdf": ".pdf",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/quicktime": ".mov",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "text/csv": ".csv",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

SIZE_LIMITS: dict[str, int] = {
    "application/pdf": 50 * 1024 * 1024,
    "video/mp4": 200 * 1024 * 1024,
    "video/webm": 200 * 1024 * 1024,
    "video/quicktime": 200 * 1024 * 1024,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": 25 * 1024 * 1024,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": 25 * 1024 * 1024,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": 25 * 1024 * 1024,
    "text/csv": 25 * 1024 * 1024,
    "image/jpeg": 10 * 1024 * 1024,
    "image/png": 10 * 1024 * 1024,
    "image/webp": 10 * 1024 * 1024,
    "image/gif": 10 * 1024 * 1024,
}


def human_size(size_bytes: int) -> str:
    """Return a human-readable file size string."""
    if size_bytes < 1024 * 1024:
        return f"{size_bytes // 1024} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


async def get_media_files(
    db: AsyncSession, page: int = 1, per_page: int = 50
) -> Tuple[list[MediaFile], int]:
    """Return a paginated list of media files (newest first) and total count."""
    offset = (page - 1) * per_page
    result = await db.execute(
        select(MediaFile)
        .order_by(MediaFile.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    files = list(result.scalars().all())
    count_result = await db.execute(select(func.count()).select_from(MediaFile))
    total = count_result.scalar() or 0
    return files, total


async def upload_media_file(file: UploadFile, db: AsyncSession) -> MediaFile:
    """Validate, save to disk, and insert a MediaFile record. Raises HTTPException on rejection."""
    mime = file.content_type or ""
    if mime not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "نوع فایل مجاز نیست. "
                "فرمت‌های پشتیبانی‌شده: PDF، MP4، WEBM، MOV، XLSX، DOCX، PPTX، CSV، JPG، PNG، WEBP، GIF"
            ),
        )

    content = await file.read()
    size = len(content)
    limit = SIZE_LIMITS.get(mime, 10 * 1024 * 1024)
    if size > limit:
        limit_mb = limit // (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"حجم فایل از حد مجاز بیشتر است ({limit_mb} MB).",
        )

    ext = ALLOWED_TYPES[mime]
    filename = f"{uuid.uuid4().hex}{ext}"
    ensure_upload_dirs()
    dest = MEDIA_DIR / filename
    dest.write_bytes(content)

    rel_path = f"/static/uploads/media/{filename}"
    record = MediaFile(
        original_name=file.filename or filename,
        file_path=rel_path,
        file_size=size,
        mime_type=mime,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def delete_media_file(file_id: int, db: AsyncSession) -> None:
    """Delete a media file from disk and DB. Missing disk file is handled gracefully."""
    result = await db.execute(select(MediaFile).where(MediaFile.id == file_id))
    record = result.scalar_one_or_none()
    if not record:
        return

    disk_path = Path("app") / record.file_path.lstrip("/")
    try:
        disk_path.unlink()
    except FileNotFoundError:
        logger.warning("Media file not found on disk during delete: %s", disk_path)

    await db.delete(record)
    await db.commit()
