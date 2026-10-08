from __future__ import annotations
from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func as sa_func

from bot.database.models import Lesson


async def create(session: AsyncSession, **kwargs) -> Lesson:
    lesson = Lesson(**kwargs)
    session.add(lesson)
    await session.flush()
    return lesson


async def get_by_id(session: AsyncSession, lesson_id: int) -> Optional[Lesson]:
    return await session.get(Lesson, lesson_id)


async def delete(session: AsyncSession, lesson: Lesson) -> None:
    await session.delete(lesson)


async def list_for_user(session: AsyncSession, user_id: int, start: datetime, end: datetime) -> Sequence[Lesson]:
    res = await session.execute(
        select(Lesson)
        .where(
            Lesson.start_at >= start,
            Lesson.start_at <= end,
            (Lesson.tutor_id == user_id) | (Lesson.student_id == user_id),
        )
        .order_by(Lesson.start_at)
    )
    return res.scalars().all()


async def list_by_tutor_student(session: AsyncSession, tutor_id: int, student_id: int) -> Sequence[Lesson]:
    res = await session.execute(
        select(Lesson)
        .where(Lesson.tutor_id == tutor_id, Lesson.student_id == student_id)
        .order_by(Lesson.start_at)
    )
    return res.scalars().all()


async def count_for_tutor(session: AsyncSession, tutor_id: int) -> int:
    res = await session.execute(
        select(sa_func.count(Lesson.id)).where(Lesson.tutor_id == tutor_id)
    )
    return int(res.scalar_one())


async def count_for_tutor_student(session: AsyncSession, tutor_id: int, student_id: int) -> int:
    res = await session.execute(
        select(sa_func.count(Lesson.id)).where(
            Lesson.tutor_id == tutor_id, Lesson.student_id == student_id
        )
    )
    return int(res.scalar_one())