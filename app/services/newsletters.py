"""Newsletter campaign CRUD service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.newsletter import NewsletterCampaign


async def list_campaigns(session: AsyncSession) -> list[NewsletterCampaign]:
    """Return all campaigns: drafts first, then sent in reverse chronological order."""
    result = await session.execute(
        select(NewsletterCampaign).order_by(
            NewsletterCampaign.status.asc(),  # "draft" < "sent" alphabetically → drafts first
            NewsletterCampaign.created_at.desc(),
        )
    )
    return list(result.scalars().all())


async def get_campaign(session: AsyncSession, campaign_id: int) -> Optional[NewsletterCampaign]:
    result = await session.execute(
        select(NewsletterCampaign).where(NewsletterCampaign.id == campaign_id)
    )
    return result.scalar_one_or_none()


async def create_draft(session: AsyncSession, body: str = "") -> NewsletterCampaign:
    campaign = NewsletterCampaign(body=body, status="draft")
    session.add(campaign)
    await session.commit()
    await session.refresh(campaign)
    return campaign


async def update_body(session: AsyncSession, campaign: NewsletterCampaign, body: str) -> NewsletterCampaign:
    campaign.body = body
    await session.commit()
    await session.refresh(campaign)
    return campaign


async def mark_sent(session: AsyncSession, campaign: NewsletterCampaign) -> NewsletterCampaign:
    campaign.status = "sent"
    campaign.sent_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(campaign)
    return campaign


async def delete_campaign(session: AsyncSession, campaign: NewsletterCampaign) -> None:
    """Only draft campaigns may be deleted."""
    await session.delete(campaign)
    await session.commit()


async def last_sent_campaign(session: AsyncSession) -> Optional[NewsletterCampaign]:
    """Return the most recently sent campaign, or None if none exists yet."""
    result = await session.execute(
        select(NewsletterCampaign)
        .where(NewsletterCampaign.status == "sent")
        .order_by(NewsletterCampaign.sent_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
