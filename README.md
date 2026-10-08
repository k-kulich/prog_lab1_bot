# Tutor Bot — телеграм-бот для репетиторов и учеников

Бот помогает репетиторам вести расписание занятий, а ученикам — получать напоминания
и видеть ближайшие занятия со всеми своими репетиторами.

## Возможности

- Регистрация репетитора и ученика с ролями
- Привязка ученика к репетитору по уникальному коду
- Создание занятий с полями: название, предмет, тема, описание, ссылки
  (занятие / материалы / онлайн-доска), дата, длительность, повторение
- Поддержка повторяющихся занятий (день / неделя / месяц)
- Просмотр расписания на неделю или месяц
- Напоминания: ученику за сутки и за час, репетитору за час
- Статистика репетитора по ученикам и занятиям
- Юнит-тесты бизнес-логики

## Стек

- Python 3.11+
- aiogram 3.x
- SQLAlchemy 2.0 (async) + aiosqlite / asyncpg
- APScheduler 3.x
- pytest + pytest-asyncio

## Архитектура

```
Telegram → Handlers → Services → Repositories → DB
              ↑            ↑
          Keyboards    Scheduler (APScheduler)
          FSM States
```


- __Handlers__ — прием апдейтов, FSM.
- __Services__ — вся бизнес-логика (легко тестируется без Telegram).
- __Repositories__ — SQL-запросы.
- __Scheduler__ — фоновая проверка напоминаний раз в минуту.

## Установка

```bash
git clone <repo> && cd tutor_bot
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# вписать BOT_TOKEN
```

## Запуск 

```zsh
python run.py
```

БД создается автоматически (SQLite по умолчанию).

## Тесты

```zsh
pytest -v
```

Результаты тестирования:

```zsh
============================================================================ test session starts =============================================================================
platform darwin -- Python 3.9.6, pytest-8.3.2, pluggy-1.6.0 -- /Users/ksenia/Documents/itmo/академ разница/прога/lab1/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/ksenia/Documents/itmo/академ разница/прога/lab1
configfile: pytest.ini
testpaths: tests
plugins: asyncio-0.24.0
asyncio: mode=auto, default_loop_scope=function
collected 22 items                                                                                                                                                           

tests/test_codes.py::test_length PASSED                                                                                                                                [  4%]
tests/test_codes.py::test_alphabet PASSED                                                                                                                              [  9%]
tests/test_codes.py::test_unique PASSED                                                                                                                                [ 13%]
tests/test_lesson_service.py::test_create_single_lesson PASSED                                                                                                         [ 18%]
tests/test_lesson_service.py::test_create_recurring_lessons PASSED                                                                                                     [ 22%]
tests/test_lesson_service.py::test_reminders_are_created PASSED                                                                                                        [ 27%]
tests/test_lesson_service.py::test_student_cannot_create_lesson PASSED                                                                                                 [ 31%]
tests/test_recurrence.py::test_none_returns_single PASSED                                                                                                              [ 36%]
tests/test_recurrence.py::test_weekly_with_until PASSED                                                                                                                [ 40%]
tests/test_recurrence.py::test_daily_default_count PASSED                                                                                                              [ 45%]
tests/test_recurrence.py::test_monthly PASSED                                                                                                                          [ 50%]
tests/test_recurrence.py::test_unknown_recurrence PASSED                                                                                                               [ 54%]
tests/test_recurrence.py::test_max_count_cap PASSED                                                                                                                    [ 59%]
tests/test_schedule_service.py::test_schedule_for_student PASSED                                                                                                       [ 63%]
tests/test_schedule_service.py::test_schedule_empty PASSED                                                                                                             [ 68%]
tests/test_stats_service.py::test_stats_empty PASSED                                                                                                                   [ 72%]
tests/test_stats_service.py::test_stats_with_lessons PASSED                                                                                                            [ 77%]
tests/test_user_service.py::test_register_tutor PASSED                                                                                                                 [ 81%]
tests/test_user_service.py::test_register_duplicate PASSED                                                                                                             [ 86%]
tests/test_user_service.py::test_link_by_code PASSED                                                                                                                   [ 90%]
tests/test_user_service.py::test_link_invalid_code PASSED                                                                                                              [ 95%]
tests/test_user_service.py::test_link_twice PASSED                                                                                                                     [100%]

============================================================================= 22 passed in 0.17s =============================================================================
```

Также есть smoke_test, который я использовала, так как VPN на компьютере нет:
```zsh
python -m scripts.smoke_test
```

## Как пользоваться

1. Репетитор: /start → «Я репетитор» → вводит имя → получает код.
2. Ученик: /start → «Я ученик» → «Привязать репетитора» → вводит код.
3. Репетитор: «Новое занятие» — создает занятие для ученика.
4. Ученик: получает напоминания автоматически.
5. Расписание: «Расписание» → неделя/месяц.
6. Статистика: «Статистика» (только репетитор).

## Планируемое расширение

- Alembic для миграций.
- Redis FSM storage для горизонтального масштабирования.
- Экспорт расписания в .ics.
- Оплата занятий через YooKassa.
