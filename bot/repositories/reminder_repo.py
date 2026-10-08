from __future__ import annotations
from datetime import datetime
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import Reminder


async def create(session: AsyncSession, lesson_id: int, user_id: int, kind: str, scheduled_at: datetime) -> Reminder:
    r = Reminder(lesson_id=lesson_id, user_id=user_id, kind=kind, scheduled_at=scheduled_at)
    session.add(r)
    await session.flush()
    return r


async def get_due(session: AsyncSession, now: datetime) -> Sequence[Reminder]:
    res = await session.execute(
        select(Reminder)
        .options(
            selectinload(Reminder.lesson),
            selectinload(Reminder.user),
        )
        .where(Reminder.sent_at.is_(None), Reminder.scheduled_at <= now)
    )
    return res.scalars().all()


async def mark_sent(session: AsyncSession, reminder: Reminder, when: datetime) -> None:
    reminder.sent_at = when
    await session.flush()