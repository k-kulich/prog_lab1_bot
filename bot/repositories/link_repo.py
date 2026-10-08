from __future__ import annotations
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import TutorStudentLink, User


async def exists(session: AsyncSession, tutor_id: int, student_id: int) -> bool:
    res = await session.execute(select(TutorStudentLink).where(TutorStudentLink.tutor_id == tutor_id, 
                                       TutorStudentLink.student_id == student_id))
    return res.scalar_one_or_none() is not None


async def create(session: AsyncSession, tutor_id: int, student_id: int, subject: str | None = None) -> TutorStudentLink:
    link = TutorStudentLink(tutor_id=tutor_id, student_id=student_id, subject=subject)
    session.add(link)
    await session.flush()
    return link


async def get_students(session: AsyncSession, tutor_id: int) -> Sequence[User]:
    res = await session.execute(
        select(User)
        .join(TutorStudentLink, TutorStudentLink.student_id == User.id)
        .where(TutorStudentLink.tutor_id == tutor_id)
    )
    return res.scalars().all()


async def get_tutors(session: AsyncSession, student_id: int) -> Sequence[User]:
    res = await session.execute(
        select(User)
        .join(TutorStudentLink, TutorStudentLink.tutor_id == User.id)
        .where(TutorStudentLink.student_id == student_id)
    )
    return res.scalars().all()