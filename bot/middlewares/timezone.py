from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot.database.database import db


class HasTimezoneMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Any:
        if await db.is_user_has_timezone(message.from_user.id):
            return await handler(message, data)
        return await message.answer(
            text="Для начала работы предоставьте данные о вашем часовом поясе.🕐\nДля этого просто отправьте команду\n<b>/set_timezone</b>",
            parse_mode="HTML"
        )


class HasTimezoneCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        if await db.is_user_has_timezone(callback.from_user.id):
            return await handler(callback, data)
        await callback.message.answer(
            text="Для начала работы предоставьте данные о вашем часовом поясе.🕐\nДля этого просто отправьте команду\n<b>/set_timezone</b>",
            parse_mode="HTML"
        )
        await callback.answer()


