from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services import lesson_service, stats_service


async def test_stats_empty(session: AsyncSession, tutor):
    s = await stats_service.tutor_stats(session, tutor)
    assert s["students_count"] == 0
    assert s["total_lessons"] == 0
    assert s["upcoming_week"] == 0


async def test_stats_with_lessons(session: AsyncSession, tutor, student):
    start = datetime.utcnow() + timedelta(days=1)
    for i in range(3):
        await lesson_service.create_lesson(
            session,
            tutor,
            student_id=student.id,
            title=f"L{i}",
            subject="",
            topic=None,
            description=None,
            lesson_url=None,
            materials_url=None,
            board_url=None,
            start_at=start + timedelta(days=i),
            duration_min=60,
        )
    from bot.repositories import link_repo

    await link_repo.create(session, tutor.id, student.id)
    s = await stats_service.tutor_stats(session, tutor)
    assert s["students_count"] == 1
    assert s["total_lessons"] == 3
    assert s["upcoming_week"] == 3
    assert s["per_student"][0][0] == student.full_name