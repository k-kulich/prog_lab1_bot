from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import UserRole
from bot.keyboards.main_kb import main_menu_student, main_menu_tutor
from bot.services import user_service
from bot.states.registration_states import Registration

router = Router()


def role_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Я репетитор"), KeyboardButton(text="Я ученик")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession, db_user):
    if db_user is not None:
        kb = main_menu_tutor() if db_user.role == UserRole.TUTOR.value else main_menu_student()
        await message.answer(f"С возвращением, {db_user.full_name}!", reply_markup=kb)
        return
    await state.set_state(Registration.choosing_role)
    await message.answer("Привет! Кто вы?", reply_markup=role_kb())


@router.message(Registration.choosing_role, F.text.in_({"Я репетитор", "Я ученик"}))
async def choose_role(message: Message, state: FSMContext):
    role = UserRole.TUTOR.value if message.text == "Я репетитор" else UserRole.STUDENT.value
    await state.update_data(role=role)
    await state.set_state(Registration.entering_name)
    await message.answer("Как вас зовут? (ФИО или имя)")


@router.message(Registration.entering_name, F.text)
async def enter_name(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    role = data["role"]
    name = message.text.strip()[:255]

    try:
        if role == UserRole.TUTOR.value:
            user = await user_service.register_tutor(session, message.from_user.id, name)
            await message.answer(
                f"Готово! Ваш код для приглашения учеников: <b>{user.tutor_code}</b>\n"
                "Передайте его ученикам.",
                reply_markup=main_menu_tutor(),
            )
        else:
            await user_service.register_student(session, message.from_user.id, name)
            await message.answer(
                "Готово! Теперь привяжите репетитора по коду.",
                reply_markup=main_menu_student(),
            )
    except user_service.AlreadyExistsError:
        await message.answer("Вы уже зарегистрированы. /start")

    await state.clear()