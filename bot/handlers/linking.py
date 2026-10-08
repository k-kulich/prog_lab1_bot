from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import UserRole
from bot.services import user_service
from bot.states.registration_states import Linking

router = Router()


@router.message(F.text == "Привязать репетитора")
async def start_link(message: Message, state: FSMContext, db_user):
    if db_user is None or db_user.role != UserRole.STUDENT.value:
        await message.answer("Доступно только ученикам.")
        return
    await state.set_state(Linking.entering_code)
    await message.answer("Введите код репетитора:")


@router.message(Linking.entering_code, F.text)
async def submit_code(message: Message, state: FSMContext, session: AsyncSession, db_user):
    try:
        tutor = await user_service.link_student_by_code(session, db_user, message.text)
        await message.answer(f"Вы привязаны к репетитору {tutor.full_name}")
    except user_service.InvalidCodeError as e:
        await message.answer(f"Ошибка: {e}")
    except user_service.AlreadyLinkedError as e:
        await message.answer(f"{e}")
    await state.clear()


@router.message(F.text == "Мои репетиторы")
async def my_tutors(message: Message, session: AsyncSession, db_user):
    tutors = await user_service.get_tutors(session, db_user)
    if not tutors:
        await message.answer("У вас пока нет репетиторов.")
        return
    text = "Ваши репетиторы:\n" + "\n".join(f"• {t.full_name}" for t in tutors)
    await message.answer(text)


@router.message(F.text == "Мои ученики")
async def my_students(message: Message, session: AsyncSession, db_user):
    if db_user is None or db_user.role != UserRole.TUTOR.value:
        await message.answer("Доступно только репетиторам.")
        return
    students = await user_service.get_students(session, db_user)
    if not students:
        await message.answer("У вас пока нет учеников. Передайте им ваш код.")
        return
    text = "Ваши ученики:\n" + "\n".join(f"• {s.full_name}" for s in students)
    await message.answer(text)


@router.message(F.text == "Мой код")
async def my_code(message: Message, db_user):
    if db_user and db_user.role == UserRole.TUTOR.value:
        await message.answer(f"Ваш код: <b>{db_user.tutor_code}</b>")