"""Contact message services."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import ContactMessage
from app.schemas.contact import ContactForm


async def save_message(session: AsyncSession, data: ContactForm) -> ContactMessage:
    msg = ContactMessage(
        name=data.name.strip() or None,
        email=data.email.strip(),
        subject=data.subject.strip() or None,
        message=data.message.strip(),
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg


async def list_messages(session: AsyncSession) -> list[ContactMessage]:
    result = await session.execute(
        select(ContactMessage).order_by(ContactMessage.created_at.desc())
    )
    return list(result.scalars().all())


async def get_message(session: AsyncSession, message_id: int) -> Optional[ContactMessage]:
    result = await session.execute(
        select(ContactMessage).where(ContactMessage.id == message_id)
    )
    return result.scalar_one_or_none()


async def toggle_read(session: AsyncSession, msg: ContactMessage) -> ContactMessage:
    msg.is_read = not msg.is_read
    await session.commit()
    await session.refresh(msg)
    return msg


async def delete_message(session: AsyncSession, msg: ContactMessage) -> None:
    await session.delete(msg)
    await session.commit()


async def unread_count(session: AsyncSession) -> int:
    result = await session.execute(
        select(ContactMessage).where(ContactMessage.is_read.is_(False))
    )
    return len(result.scalars().all())
