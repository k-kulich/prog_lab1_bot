from __future__ import annotations
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User, UserRole
from bot.repositories import link_repo, user_repo
from bot.utils.codes import generate_tutor_code


class AlreadyExistsError(Exception):
    pass


class InvalidCodeError(Exception):
    pass


class AlreadyLinkedError(Exception):
    pass


async def _unique_tutor_code(session: AsyncSession) -> str:
    for _ in range(10):
        code = generate_tutor_code()
        if await user_repo.get_by_tutor_code(session, code) is None:
            return code
    raise RuntimeError("Не удалось сгенерировать уникальный код")


async def register_tutor(session: AsyncSession, telegram_id: int, full_name: str) -> User:
    existing = await user_repo.get_by_telegram_id(session, telegram_id)
    if existing:
        raise AlreadyExistsError("Пользователь уже зарегистрирован")
    code = await _unique_tutor_code(session)
    return await user_repo.create(
        session,
        telegram_id=telegram_id,
        role=UserRole.TUTOR.value,
        full_name=full_name,
        tutor_code=code,
    )


async def register_student(session: AsyncSession, telegram_id: int, full_name: str) -> User:
    existing = await user_repo.get_by_telegram_id(session, telegram_id)
    if existing:
        raise AlreadyExistsError("Пользователь уже зарегистрирован")
    return await user_repo.create(
        session,
        telegram_id=telegram_id,
        role=UserRole.STUDENT.value,
        full_name=full_name,
    )


async def link_student_by_code(session: AsyncSession, student: User, code: str) -> User:
    """Возвращает репетитора, к которому привязался ученик."""
    code = code.strip().upper()
    tutor = await user_repo.get_by_tutor_code(session, code)
    if tutor is None or tutor.role != UserRole.TUTOR.value:
        raise InvalidCodeError("Код не найден")
    if tutor.id == student.id:
        raise InvalidCodeError("Нельзя привязать самого себя")
    if await link_repo.exists(session, tutor.id, student.id):
        raise AlreadyLinkedError("Вы уже связаны с этим репетитором")
    await link_repo.create(session, tutor.id, student.id)
    return tutor


async def get_students(session: AsyncSession, tutor: User) -> Sequence[User]:
    return await link_repo.get_students(session, tutor.id)


async def get_tutors(session: AsyncSession, student: User) -> Sequence[User]:
    return await link_repo.get_tutors(session, student.id)