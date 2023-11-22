from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.database.database import db


class IsUserSubscribed(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await db.is_user_subscribed(message.from_user.id)


class IsUserNotSubscribed(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return not await db.is_user_subscribed(message.from_user.id)
