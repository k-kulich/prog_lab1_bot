from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_tutor() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои ученики")],
            [KeyboardButton(text="Новое занятие"), KeyboardButton(text="Расписание")],
            [KeyboardButton(text="Статистика"), KeyboardButton(text="Мой код")],
        ],
        resize_keyboard=True,
    )


def main_menu_student() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Привязать репетитора")],
            [KeyboardButton(text="Расписание")],
            [KeyboardButton(text="Мои репетиторы")],
        ],
        resize_keyboard=True,
    )