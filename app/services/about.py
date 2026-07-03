"""About page services."""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.about import AboutPage
from app.schemas.about import AboutForm, LinkInput

DEFAULT_ABOUT = AboutForm(
    author_name="میلاد میرزایی",
    author_bio=(
        "میلاد میرزایی — مدیر محصول. این سایت جایی است که یادداشت‌هایم را "
        "منظم می‌کنم و به اشتراک می‌گذارم."
    ),
    pet_feature_body=(
        "«پت فیچر» (Pet Feature) اصطلاحی در مدیریت محصول است برای ویژگی‌ای که یک مدیر محصول "
        "به‌خاطر علاقه شخصی — نه داده یا نیاز کاربر — به آن دلبسته است."
    ),
    site_story_body=(
        "پت فیچر یک دانشنامه شخصی مدیریت محصول است — کتاب‌هایی که خوانده‌ام، "
        "یادداشت‌هایی که نوشته‌ام، و منابعی که به درک عمیق‌تر کمک کرده‌اند."
    ),
    links=[LinkInput(title="لینکدین", url="https://linkedin.com/in/...")],
)


async def get_about_page(session: AsyncSession) -> AboutPage:
    result = await session.execute(select(AboutPage).limit(1))
    about = result.scalar_one_or_none()
    if about is None:
        about = AboutPage(
            author_name=DEFAULT_ABOUT.author_name,
            author_bio=DEFAULT_ABOUT.author_bio,
            pet_feature_body=DEFAULT_ABOUT.pet_feature_body,
            site_story_body=DEFAULT_ABOUT.site_story_body,
            links=[link.model_dump() for link in DEFAULT_ABOUT.links],
        )
        session.add(about)
        await session.commit()
        await session.refresh(about)
    return about


async def update_about_page(session: AsyncSession, about: AboutPage, data: AboutForm) -> AboutPage:
    about.author_name = data.author_name
    about.author_photo = data.author_photo or None
    about.author_bio = data.author_bio or None
    about.pet_feature_body = data.pet_feature_body or None
    about.site_story_body = data.site_story_body or None
    about.links = [link.model_dump() for link in data.links if link.title.strip()]
    await session.commit()
    await session.refresh(about)
    return about


def parse_links(raw: str) -> list[LinkInput]:
    raw = raw.strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [LinkInput.model_validate(item) for item in parsed if item.get("title", "").strip()]
    except (json.JSONDecodeError, ValueError):
        pass
    return []
