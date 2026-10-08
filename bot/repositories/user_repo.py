from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    res = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return res.scalar_one_or_none()


async def get_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    return await session.get(User, user_id)


async def get_by_tutor_code(session: AsyncSession, code: str) -> Optional[User]:
    res = await session.execute(select(User).where(User.tutor_code == code))
    return res.scalar_one_or_none()


async def create(session: AsyncSession, telegram_id: int, role: str, full_name: str,
                 tutor_code: str | None = None) -> User:
    user = User(telegram_id=telegram_id, role=role, full_name=full_name, tutor_code=tutor_code)
    session.add(user)
    await session.flush()
    return user


async def list_all(session: AsyncSession) -> Sequence[User]:
    res = await session.execute(select(User))
    return res.scalars().all()