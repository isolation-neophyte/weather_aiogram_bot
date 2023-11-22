import os
import asyncio

from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.database.database import db
from bot.handlers import user_handlers, trash_collector
from bot.handlers.weather import weather_handlers
from bot.handlers.subscription import edit_subscription_handlers, subscription_handlers
from bot.handlers.subscription.subscription_functions import send_daily_forecasts
from bot.middlewares.only_private import OnlyPrivateChatMessageMiddleware, OnlyPrivateChatCallbackMiddleware


async def main():
    load_dotenv(find_dotenv())

    bot = Bot(os.getenv("BOT_TOKEN_API"))
    dp = Dispatcher()
    await db.connect()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_forecasts, trigger="interval", seconds=60, kwargs={"bot": bot})
    scheduler.start()

    dp.message.middleware(OnlyPrivateChatMessageMiddleware())
    dp.message.middleware(OnlyPrivateChatCallbackMiddleware())

    dp.include_router(user_handlers.router)
    dp.include_router(weather_handlers.router)
    dp.include_router(subscription_handlers.router)
    dp.include_router(edit_subscription_handlers.router)
    dp.include_router(trash_collector.router)

    try:
        await dp.start_polling(bot)
    finally:
        await db.disconnect()
        await bot.session.close()
        await scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
