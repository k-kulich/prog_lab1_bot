from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services import lesson_service, schedule_service


async def test_schedule_for_student(session: AsyncSession, tutor, student):
    start = datetime.utcnow() + timedelta(days=2)
    await lesson_service.create_lesson(
        session,
        tutor,
        student_id=student.id,
        title="A",
        subject="",
        topic=None,
        description=None,
        lesson_url=None,
        materials_url=None,
        board_url=None,
        start_at=start,
        duration_min=60,
    )
    now = datetime.utcnow()
    lessons = await schedule_service.get_schedule(session, student, now, now + timedelta(days=7))
    assert len(lessons) == 1
    assert lessons[0].title == "A"


async def test_schedule_empty(session: AsyncSession, student):
    now = datetime.utcnow()
    lessons = await schedule_service.get_week(session, student, now)
    assert lessons == []