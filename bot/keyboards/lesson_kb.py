from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def recurrence_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Без повтора", callback_data="rec:none")],
            [InlineKeyboardButton(text="Каждый день", callback_data="rec:daily")],
            [InlineKeyboardButton(text="Каждую неделю", callback_data="rec:weekly")],
            [InlineKeyboardButton(text="Каждый месяц", callback_data="rec:monthly")],
        ]
    )


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сохранить", callback_data="lesson:save"),
                InlineKeyboardButton(text="Отмена", callback_data="lesson:cancel"),
            ]
        ]
    )