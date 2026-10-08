from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()

MENU_BUTTONS = {
    "Новое занятие", "Расписание", "Статистика", "Мой код",
    "Мои ученики", "Привязать репетитора", "Мои репетиторы",
}

@router.message(F.text.in_(MENU_BUTTONS))
async def drop_state(message: Message, state: FSMContext):
    await state.clear()