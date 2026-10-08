from datetime import datetime, timedelta
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Reminder, ReminderKind
from bot.services import lesson_service, user_service


async def test_create_single_lesson(session: AsyncSession, tutor, student):
    await user_service.link_student_by_code(session, student, tutor.tutor_code)
    start = datetime.utcnow() + timedelta(days=3)
    lessons = await lesson_service.create_lesson(
        session,
        tutor,
        student_id=student.id,
        title="Алгебра",
        subject="Математика",
        topic="Квадратные уравнения",
        description=None,
        lesson_url="https://zoom.us/x",
        materials_url=None,
        board_url=None,
        start_at=start,
        duration_min=60,
    )
    assert len(lessons) == 1
    assert lessons[0].title == "Алгебра"


async def test_create_recurring_lessons(session: AsyncSession, tutor, student):
    start = datetime.utcnow() + timedelta(days=3)
    until = start + timedelta(weeks=3)
    lessons = await lesson_service.create_lesson(
        session,
        tutor,
        student_id=student.id,
        title="Физика",
        subject="Физика",
        topic=None,
        description=None,
        lesson_url=None,
        materials_url=None,
        board_url=None,
        start_at=start,
        duration_min=90,
        recurrence="weekly",
        until=until,
    )
    assert len(lessons) == 4
    assert all(l.series_id == lessons[0].series_id for l in lessons)


async def test_reminders_are_created(session: AsyncSession, tutor, student):
    start = datetime.utcnow() + timedelta(days=3)
    await lesson_service.create_lesson(
        session,
        tutor,
        student_id=student.id,
        title="X",
        subject="",
        topic=None,
        description=None,
        lesson_url=None,
        materials_url=None,
        board_url=None,
        start_at=start,
        duration_min=60,
    )
    res = await session.execute(select(Reminder))
    reminders = res.scalars().all()
    assert len(reminders) == 3
    kinds_for_student = [r.kind for r in reminders if r.user_id == student.id]
    assert set(kinds_for_student) == {
        ReminderKind.DAY_BEFORE.value,
        ReminderKind.HOUR_BEFORE.value,
    }
    kinds_for_tutor = [r.kind for r in reminders if r.user_id == tutor.id]
    assert kinds_for_tutor == [ReminderKind.HOUR_BEFORE.value]


async def test_student_cannot_create_lesson(session: AsyncSession, student):
    with pytest.raises(lesson_service.LessonError):
        await lesson_service.create_lesson(
            session,
            student,
            student_id=student.id,
            title="X",
            subject="",
            topic=None,
            description=None,
            lesson_url=None,
            materials_url=None,
            board_url=None,
            start_at=datetime.utcnow() + timedelta(days=1),
            duration_min=60,
        )