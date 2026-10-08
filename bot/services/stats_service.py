from __future__ import annotations
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.repositories import lesson_repo, link_repo
from bot.utils.datetime_utils import utcnow


async def tutor_stats(session: AsyncSession, tutor: User) -> dict:
    students = await link_repo.get_students(session, tutor.id)
    now = utcnow()

    total_lessons = 0
    upcoming_week = 0
    per_student: list[tuple[str, int]] = []

    for student in students:
        cnt = await lesson_repo.count_for_tutor_student(session, tutor.id, student.id)
        total_lessons += cnt
        per_student.append((student.full_name, cnt))

    week_lessons = await lesson_repo.list_for_user(
        session, tutor.id, now, now + timedelta(days=7)
    )
    upcoming_week = len(week_lessons)

    return {
        "students_count": len(students),
        "total_lessons": total_lessons,
        "upcoming_week": upcoming_week,
        "per_student": per_student,
    }