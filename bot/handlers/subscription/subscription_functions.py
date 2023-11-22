from datetime import datetime
from pytz import timezone
from aiogram import Bot

from bot.database.database import db
from bot.handlers.weather.weather_functions import get_today_forecast
from bot.keyboards.user_keyboards import get_weather_inline_kb


def get_greeting(time_str):
    try:
        hour = int(time_str.split(":")[0])
        if 6 <= hour < 12:
            return "Доброе утро 🌅"
        elif 12 <= hour < 18:
            return "Добрый день ☀️"
        elif 18 <= hour < 22:
            return "Добрый вечер 🌆"
        else:
            return "Доброй ночи 🌙"
    except (ValueError, IndexError):
        return "Здравствуйте!👋"


async def send_daily_forecasts(bot: Bot):
    users = await db.get_users()

    for user in users:
        user_id = user[1]

        if await db.is_user_subscribed(user_id=user_id):
            user_timezone = timezone(await db.get_timezone(user_id=user_id))
            user_forecast_time = await db.get_sub_forecast_time(user_id=user_id)
            current_time_server = datetime.now(tz=user_timezone).strftime("%H:%M")

            if user_forecast_time == current_time_server:
                await bot.send_message(
                    chat_id=user_id,
                    text=get_greeting(user_forecast_time)
                )

                forecast_msg = await bot.send_message(
                    chat_id=user_id,
                    text=get_today_forecast(city_data=await db.get_sub_city_data(user_id=user_id),
                                            timezone=await db.get_timezone(user_id=user_id)),
                    reply_markup=get_weather_inline_kb(),
                    parse_mode="HTML"
                )

                await db.set_last_city_data(user_id=user_id, city_data=await db.get_sub_city_data(user_id=user_id))
                await db.set_forecast_msg_id(user_id=user_id, msg_id=forecast_msg.message_id)
