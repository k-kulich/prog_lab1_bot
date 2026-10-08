from __future__ import annotations
from datetime import datetime, timedelta
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Lesson, User
from bot.repositories import lesson_repo


async def get_schedule(session: AsyncSession, user: User, start: datetime, end: datetime) -> Sequence[Lesson]:
    return await lesson_repo.list_for_user(session, user.id, start, end)


async def get_week(session: AsyncSession, user: User, now: datetime) -> Sequence[Lesson]:
    return await get_schedule(session, user, now, now + timedelta(days=7))


async def get_month(session: AsyncSession, user: User, now: datetime) -> Sequence[Lesson]:
    return await get_schedule(session, user, now, now + timedelta(days=30))