"""Прогон основного сценария без обращения к Telegram (тк на компе нет VPN).
Запуск: python -m scripts.smoke_test
"""
import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock
from sqlalchemy import delete, select

from bot.database.engine import SessionLocal, init_db
from bot.database.models import Reminder, TutorStudentLink, User
from bot.scheduler.reminders import check_and_send
from bot.services import lesson_service, schedule_service, stats_service, user_service
from bot.utils.datetime_utils import utcnow


async def main() -> None:
    await init_db()

    async with SessionLocal() as s:
        await s.execute(delete(Reminder))
        await s.execute(delete(TutorStudentLink))
        await s.execute(delete(User))
        await s.commit()

        print("1) Регистрация...")
        tutor = await user_service.register_tutor(s, 1001, "Иван Петров")
        student = await user_service.register_student(s, 2002, "Маша Иванова")
        print(f"   код репетитора: {tutor.tutor_code}")

        print("2) Привязка ученика по коду...")
        linked = await user_service.link_student_by_code(s, student, tutor.tutor_code)
        assert linked.id == tutor.id
        print("   ok")

        print("3) Создание одиночного занятия за 90 минут...")
        start = utcnow() + timedelta(minutes=90)
        lessons = await lesson_service.create_lesson(
            s, tutor, student_id=student.id,
            title="Алгебра", subject="Математика",
            topic="Логарифмы", description=None,
            lesson_url="https://zoom.us/j/123",
            materials_url=None, board_url=None,
            start_at=start, duration_min=60,
        )
        assert len(lessons) == 1
        print(f"   создано: {len(lessons)}")

        print("4) Создание серии (weekly x 4)...")
        series = await lesson_service.create_lesson(
            s, tutor, student_id=student.id,
            title="Физика", subject="Физика",
            topic=None, description=None,
            lesson_url=None, materials_url=None, board_url=None,
            start_at=start + timedelta(days=7),
            duration_min=90, recurrence="weekly",
            until=start + timedelta(days=28),
        )
        assert len(series) == 4, f"ожидали 4, получили {len(series)}"
        print(f"   создано: {len(series)}")

        print("5) Проверка напоминаний в БД...")
        res = await s.execute(select(Reminder))
        reminders = res.scalars().all()
        for r in reminders:
            print(f"   user={r.user_id} kind={r.kind} at={r.scheduled_at:%d.%m %H:%M}")
        await s.commit()

        print("6) Расписание ученика (неделя)...")
        sched = await schedule_service.get_week(s, student, utcnow())
        print(f"   занятий: {len(sched)}")

        print("7) Статистика репетитора...")
        st = await stats_service.tutor_stats(s, tutor)
        print(f"   {st}")

        print("8) Дымовой тест scheduler'а: сдвигаем одно напоминание в прошлое...")
        first = reminders[0]
        first.scheduled_at = utcnow() - timedelta(minutes=1)
        first.sent_at = None
        await s.commit()

        bot = AsyncMock()
        bot.send_message = AsyncMock()
        sent = await check_and_send(bot, SessionLocal)
        print(f"   отправлено сообщений: {sent}")
        for call in bot.send_message.await_args_list:
            tg_id, text = call.args[0], call.args[1]
            print(f"   → {tg_id}: {text.splitlines()[0]}")

        if sent == 0:
            raise SystemExit("SMOKE FAILED: scheduler не отправил ни одного сообщения")

        print("\nSMOKE OK")


if __name__ == "__main__":
    asyncio.run(main())