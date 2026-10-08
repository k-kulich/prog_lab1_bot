from aiogram.fsm.state import State, StatesGroup


class NewLesson(StatesGroup):
    choose_student = State()
    enter_title = State()
    enter_subject = State()
    enter_topic = State()
    enter_description = State()
    enter_lesson_url = State()
    enter_materials_url = State()
    enter_board_url = State()
    enter_datetime = State()
    enter_duration = State()
    choose_recurrence = State()
    enter_until = State()
    confirm = State()