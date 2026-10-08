import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.database.engine import SessionLocal, init_db
from bot.handlers import lessons, linking, registration, schedule, stats
from bot.middlewares.db_middleware import DbSessionMiddleware
from bot.middlewares.user_middleware import UserMiddleware
from bot.middlewares import escape
from bot.scheduler.reminders import setup_scheduler


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.update.outer_middleware(DbSessionMiddleware(SessionLocal))
    dp.update.outer_middleware(UserMiddleware())

    dp.include_router(escape.router)
    dp.include_router(registration.router)
    dp.include_router(linking.router)
    dp.include_router(lessons.router)
    dp.include_router(schedule.router)
    dp.include_router(stats.router)
    return dp


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()

    scheduler = setup_scheduler(bot, SessionLocal)
    scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())