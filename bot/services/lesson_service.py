from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Lesson, RecurrenceType, ReminderKind, User, UserRole
from bot.repositories import lesson_repo, reminder_repo
from bot.utils.recurrence import generate_occurrences


class LessonError(Exception):
    pass


async def create_lesson(
    session: AsyncSession,
    tutor: User,
    student_id: int,
    *,
    title: str,
    subject: str,
    topic: Optional[str],
    description: Optional[str],
    lesson_url: Optional[str],
    materials_url: Optional[str],
    board_url: Optional[str],
    start_at: datetime,
    duration_min: int,
    recurrence: str = RecurrenceType.NONE.value,
    until: Optional[datetime] = None,
) -> list[Lesson]:
    if tutor.role != UserRole.TUTOR.value:
        raise LessonError("Только репетитор может создавать занятия")

    series_id = uuid.uuid4().hex if recurrence != RecurrenceType.NONE.value else None

    dates = generate_occurrences(start_at, recurrence, until)
    lessons: list[Lesson] = []
    for dt in dates:
        lesson = await lesson_repo.create(
            session,
            tutor_id=tutor.id,
            student_id=student_id,
            title=title,
            subject=subject,
            topic=topic,
            description=description,
            lesson_url=lesson_url,
            materials_url=materials_url,
            board_url=board_url,
            start_at=dt,
            duration_min=duration_min,
            recurrence=recurrence,
            series_id=series_id,
        )
        lessons.append(lesson)
        await _schedule_reminders(session, lesson)
    return lessons


async def _schedule_reminders(session: AsyncSession, lesson: Lesson) -> None:
    # ученику: за сутки и за час
    day_before = lesson.start_at - timedelta(days=1)
    hour_before = lesson.start_at - timedelta(hours=1)

    if day_before > datetime.utcnow():
        await reminder_repo.create(
            session,
            lesson_id=lesson.id,
            user_id=lesson.student_id,
            kind=ReminderKind.DAY_BEFORE.value,
            scheduled_at=day_before,
        )
    if hour_before > datetime.utcnow():
        await reminder_repo.create(
            session,
            lesson_id=lesson.id,
            user_id=lesson.student_id,
            kind=ReminderKind.HOUR_BEFORE.value,
            scheduled_at=hour_before,
        )
        # репетитору — только за час
        await reminder_repo.create(
            session,
            lesson_id=lesson.id,
            user_id=lesson.tutor_id,
            kind=ReminderKind.HOUR_BEFORE.value,
            scheduled_at=hour_before,
        )


async def delete_lesson(session: AsyncSession, tutor: User, lesson_id: int) -> None:
    lesson = await lesson_repo.get_by_id(session, lesson_id)
    if lesson is None:
        raise LessonError("Занятие не найдено")
    if lesson.tutor_id != tutor.id:
        raise LessonError("Нет прав на удаление")
    await lesson_repo.delete(session, lesson)


async def list_tutor_student_lessons(session: AsyncSession, tutor: User, student_id: int) -> Sequence[Lesson]:
    return await lesson_repo.list_by_tutor_student(session, tutor.id, student_id)