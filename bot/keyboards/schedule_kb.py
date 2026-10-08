from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def period_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Неделя", callback_data="sched:week"),
                InlineKeyboardButton(text="Месяц", callback_data="sched:month"),
            ]
        ]
    )