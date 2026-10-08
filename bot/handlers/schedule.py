from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.schedule_kb import period_kb
from bot.services import schedule_service
from bot.utils.datetime_utils import utcnow

router = Router()


def _fmt(lessons) -> str:
    if not lessons:
        return "Занятий нет."
    lines = []
    for l in lessons:
        parts = [f"{l.start_at:%d.%m %H:%M} — {l.title}"]
        if l.subject:
            parts.append(f"   предмет: {l.subject}")
        if l.lesson_url:
            parts.append(f"   {l.lesson_url}")
        lines.append("\n".join(parts))
    return "\n\n".join(lines)


@router.message(F.text == "Расписание")
async def show_schedule(message: Message, db_user):
    if db_user is None:
        await message.answer("Сначала /start")
        return
    await message.answer("Выберите период:", reply_markup=period_kb())


@router.callback_query(F.data == "sched:week")
async def week(call: CallbackQuery, session: AsyncSession, db_user):
    if db_user is None:
        await call.message.answer("Сначала /start")
        return
    lessons = await schedule_service.get_week(session, db_user, utcnow())
    await call.message.edit_text(_fmt(lessons))


@router.callback_query(F.data == "sched:month")
async def month(call: CallbackQuery, session: AsyncSession, db_user):
    if db_user is None:
        await call.message.answer("Сначала /start")
        return
    lessons = await schedule_service.get_month(session, db_user, utcnow())
    await call.message.edit_text(_fmt(lessons))