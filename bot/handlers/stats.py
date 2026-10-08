from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import UserRole
from bot.services import stats_service

router = Router()


@router.message(F.text == "Статистика")
async def stats(message: Message, session: AsyncSession, db_user):
    if db_user is None or db_user.role != UserRole.TUTOR.value:
        await message.answer("Доступно только репетиторам.")
        return
    s = await stats_service.tutor_stats(session, db_user)
    per = "\n".join(f"• {name}: {cnt}" for name, cnt in s["per_student"]) or "—"
    text = (
        f"Учеников: {s['students_count']}\n"
        f"Всего занятий: {s['total_lessons']}\n"
        f"Занятий на неделю: {s['upcoming_week']}\n\n"
        f"По ученикам:\n{per}"
    )
    await message.answer(text)