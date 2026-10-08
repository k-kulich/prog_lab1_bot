import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.database.base import Base
from bot.database.models import User, UserRole
from bot.utils.codes import generate_tutor_code


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


@pytest_asyncio.fixture
async def tutor(session):
    u = User(
        telegram_id=1001,
        role=UserRole.TUTOR.value,
        full_name="Иван Петров",
        tutor_code=generate_tutor_code(),
    )
    session.add(u)
    await session.flush()
    return u


@pytest_asyncio.fixture
async def student(session):
    u = User(
        telegram_id=2002,
        role=UserRole.STUDENT.value,
        full_name="Маша Иванова",
    )
    session.add(u)
    await session.flush()
    return u