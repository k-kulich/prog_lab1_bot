from datetime import datetime
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import RecurrenceType, UserRole
from bot.keyboards.lesson_kb import recurrence_kb
from bot.keyboards.main_kb import main_menu_tutor
from bot.services import lesson_service, user_service
from bot.states.lesson_states import NewLesson
from bot.utils.datetime_utils import parse_user_datetime

router = Router()


@router.message(F.text == "Новое занятие")
async def new_lesson_start(message: Message, state: FSMContext, session: AsyncSession, db_user):
    if db_user is None or db_user.role != UserRole.TUTOR.value:
        await message.answer("Только для репетиторов.")
        return
    students = await user_service.get_students(session, db_user)
    if not students:
        await message.answer("Сначала пригласите учеников.")
        return

    keyboard = "\n".join(f"{i+1}. {s.full_name} (id={s.id})" for i, s in enumerate(students))
    await state.set_state(NewLesson.choose_student)
    await message.answer(
        f"Выберите ученика, введите его id:\n{keyboard}",
    )


@router.message(NewLesson.choose_student, F.text)
async def choose_student(message: Message, state: FSMContext, session: AsyncSession, db_user):
    try:
        student_id = int(message.text.strip())
    except ValueError:
        await message.answer("Введите числовой id")
        return
    students = await user_service.get_students(session, db_user)
    if student_id not in [s.id for s in students]:
        await message.answer("Ученик не найден в вашем списке.")
        return
    await state.update_data(student_id=student_id)
    await state.set_state(NewLesson.enter_title)
    await message.answer("Название занятия:")


@router.message(NewLesson.enter_title, F.text)
async def enter_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip()[:255])
    await state.set_state(NewLesson.enter_subject)
    await message.answer("Предмет:")


@router.message(NewLesson.enter_subject, F.text)
async def enter_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text.strip()[:120])
    await state.set_state(NewLesson.enter_topic)
    await message.answer("Тема (или «-» чтобы пропустить):")


@router.message(NewLesson.enter_topic, F.text)
async def enter_topic(message: Message, state: FSMContext):
    val = None if message.text.strip() == "-" else message.text.strip()[:255]
    await state.update_data(topic=val)
    await state.set_state(NewLesson.enter_description)
    await message.answer("Описание (или «-»):")


@router.message(NewLesson.enter_description, F.text)
async def enter_description(message: Message, state: FSMContext):
    val = None if message.text.strip() == "-" else message.text.strip()
    await state.update_data(description=val)
    await state.set_state(NewLesson.enter_lesson_url)
    await message.answer("Ссылка на занятие (Zoom/Meet) или «-»:")


@router.message(NewLesson.enter_lesson_url, F.text)
async def enter_lesson_url(message: Message, state: FSMContext):
    val = None if message.text.strip() == "-" else message.text.strip()[:512]
    await state.update_data(lesson_url=val)
    await state.set_state(NewLesson.enter_materials_url)
    await message.answer("Ссылка на облако с файлами или «-»:")


@router.message(NewLesson.enter_materials_url, F.text)
async def enter_materials_url(message: Message, state: FSMContext):
    val = None if message.text.strip() == "-" else message.text.strip()[:512]
    await state.update_data(materials_url=val)
    await state.set_state(NewLesson.enter_board_url)
    await message.answer("Ссылка на онлайн-доску или «-»:")


@router.message(NewLesson.enter_board_url, F.text)
async def enter_board_url(message: Message, state: FSMContext):
    val = None if message.text.strip() == "-" else message.text.strip()[:512]
    await state.update_data(board_url=val)
    await state.set_state(NewLesson.enter_datetime)
    await message.answer("Дата и время начала (ДД.ММ.ГГГГ ЧЧ:ММ), UTC:")


@router.message(NewLesson.enter_datetime, F.text)
async def enter_datetime(message: Message, state: FSMContext):
    try:
        dt = parse_user_datetime(message.text)
    except ValueError:
        await message.answer("Неверный формат. Пример: 25.12.2025 18:30")
        return
    await state.update_data(start_at_iso=dt.isoformat())
    await state.set_state(NewLesson.enter_duration)
    await message.answer("Длительность в минутах (например 60):")


@router.message(NewLesson.enter_duration, F.text)
async def enter_duration(message: Message, state: FSMContext):
    try:
        dur = int(message.text.strip())
    except ValueError:
        await message.answer("Введите число")
        return
    await state.update_data(duration_min=dur)
    await state.set_state(NewLesson.choose_recurrence)
    await message.answer("Повторение:", reply_markup=recurrence_kb())


@router.callback_query(NewLesson.choose_recurrence, F.data.startswith("rec:"))
async def choose_recurrence(call: CallbackQuery, state: FSMContext):
    rec = call.data.split(":", 1)[1]
    await state.update_data(recurrence=rec)
    await call.message.edit_reply_markup(reply_markup=None)
    if rec == RecurrenceType.NONE.value:
        await _finalize(call, state)
    else:
        await state.set_state(NewLesson.enter_until)
        await call.message.answer("До какой даты повторять? (ДД.ММ.ГГГГ ЧЧ:ММ)")


@router.message(NewLesson.enter_until, F.text)
async def enter_until(message: Message, state: FSMContext):
    try:
        dt = parse_user_datetime(message.text)
    except ValueError:
        await message.answer("Неверный формат.")
        return
    await state.update_data(until_iso=dt.isoformat())
    await _finalize(message, state)


async def _finalize(event, state: FSMContext):
    await state.update_data(ready=True)
    await state.set_state(NewLesson.confirm)
    await event.answer("Данные собраны. Отправьте /save_lesson")


@router.message(NewLesson.confirm, F.text == "/save_lesson")
async def save_lesson(message: Message, state: FSMContext, session: AsyncSession, db_user):
    data = await state.get_data()
    if not data.get("ready"):
        await message.answer("Нет данных для сохранения.")
        return
    start_at = datetime.fromisoformat(data["start_at_iso"])
    until = datetime.fromisoformat(data["until_iso"]) if data.get("until_iso") else None

    lessons = await lesson_service.create_lesson(
        session,
        db_user,
        student_id=data["student_id"],
        title=data["title"],
        subject=data["subject"],
        topic=data.get("topic"),
        description=data.get("description"),
        lesson_url=data.get("lesson_url"),
        materials_url=data.get("materials_url"),
        board_url=data.get("board_url"),
        start_at=start_at,
        duration_min=data["duration_min"],
        recurrence=data.get("recurrence", RecurrenceType.NONE.value),
        until=until,
    )
    await state.clear()
    await message.answer(f"Создано занятий: {len(lessons)}", reply_markup=main_menu_tutor())