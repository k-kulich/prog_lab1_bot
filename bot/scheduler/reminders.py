import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.config import settings
from bot.database.models import ReminderKind
from bot.repositories import reminder_repo, user_repo
from bot.utils.datetime_utils import utcnow

logger = logging.getLogger(__name__)


def _format_reminder(kind: str, lesson) -> str:
    when = "через час" if kind == ReminderKind.HOUR_BEFORE.value else "завтра"
    lines = [f"Напоминание: занятие {when}"]
    lines.append(f"{lesson.title}")
    lines.append(f"{lesson.start_at:%d.%m.%Y %H:%M} (UTC)")
    if lesson.subject:
        lines.append(f"{lesson.subject}")
    if lesson.topic:
        lines.append(f"{lesson.topic}")
    if lesson.lesson_url:
        lines.append(f"Ссылка: {lesson.lesson_url}")
    if lesson.materials_url:
        lines.append(f"Материалы: {lesson.materials_url}")
    if lesson.board_url:
        lines.append(f"Доска: {lesson.board_url}")
    return "\n".join(lines)


async def check_and_send(bot: Bot, session_factory: async_sessionmaker) -> int:
    sent = 0
    async with session_factory() as session:
        now = utcnow()
        due = await reminder_repo.get_due(session, now)
        for r in due:
            try:
                user = r.user 
                text = _format_reminder(r.kind, r.lesson)
                await bot.send_message(user.telegram_id, text)
                await reminder_repo.mark_sent(session, r, now)
                sent += 1
            except Exception as e:
                logger.exception("Не удалось отправить напоминание %s: %s", r.id, e)
        await session.commit()
    return sent


def setup_scheduler(bot: Bot, session_factory: async_sessionmaker) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.timezone)
    scheduler.add_job(
        check_and_send,
        "interval",
        seconds=settings.reminder_check_interval,
        args=[bot, session_factory],
        id="reminders",
        replace_existing=True,
    )
    return scheduler