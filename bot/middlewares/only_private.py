from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class OnlyPrivateChatMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Any:
        if message.chat.type != "private":
            return await message.answer(text="Погода бот работает только в личных сообщениях!😇")
        await handler(message, data)


class OnlyPrivateChatCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        if callback.chat.type != "private":
            await callback.message.answer(text="Погода бот работает только в личных сообщениях!😇")
            return await callback.answer()
        await handler(callback, data)
