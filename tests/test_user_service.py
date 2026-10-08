import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import UserRole
from bot.services import user_service


async def test_register_tutor(session: AsyncSession):
    u = await user_service.register_tutor(session, 555, "Тест")
    assert u.role == UserRole.TUTOR.value
    assert u.tutor_code and len(u.tutor_code) == 6


async def test_register_duplicate(session: AsyncSession):
    await user_service.register_tutor(session, 555, "Тест")
    with pytest.raises(user_service.AlreadyExistsError):
        await user_service.register_tutor(session, 555, "Тест2")


async def test_link_by_code(session: AsyncSession, tutor, student):
    linked_tutor = await user_service.link_student_by_code(
        session, student, tutor.tutor_code.lower()
    )
    assert linked_tutor.id == tutor.id
    students = await user_service.get_students(session, tutor)
    assert student.id in [s.id for s in students]
    tutors = await user_service.get_tutors(session, student)
    assert tutor.id in [t.id for t in tutors]


async def test_link_invalid_code(session: AsyncSession, student):
    with pytest.raises(user_service.InvalidCodeError):
        await user_service.link_student_by_code(session, student, "ZZZZZZ")


async def test_link_twice(session: AsyncSession, tutor, student):
    await user_service.link_student_by_code(session, student, tutor.tutor_code)
    with pytest.raises(user_service.AlreadyLinkedError):
        await user_service.link_student_by_code(session, student, tutor.tutor_code)