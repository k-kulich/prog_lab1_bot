from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.repositories import user_repo


class UserMiddleware(BaseMiddleware):
    """Кладет в data['db_user'] пользователя (или None)."""

    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: dict[str, Any]) -> Any:
        session = data.get("session")
        tg_user = None
        if isinstance(event, Message):
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery):
            tg_user = event.from_user

        data["db_user"] = None
        if session is not None and tg_user is not None:
            data["db_user"] = await user_repo.get_by_telegram_id(session, tg_user.id)
        return await handler(event, data)