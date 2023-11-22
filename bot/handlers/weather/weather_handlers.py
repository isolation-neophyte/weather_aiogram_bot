import requests

from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.database.database import db
from bot.middlewares.timezone import HasTimezoneMessageMiddleware, HasTimezoneCallbackMiddleware
from bot.keyboards.user_keyboards import get_weather_forecast_type_kb, get_weather_4_days_inline_kb, get_weather_inline_kb, get_request_location_kb
from bot.handlers.weather.weather_functions import get_rules, get_timezone_time, get_today_forecast, get_4_days_forecast


router = Router()
router.message.middleware(HasTimezoneMessageMiddleware())
router.message.middleware(HasTimezoneCallbackMiddleware())


class Weather(StatesGroup):
    forecast_type = State()
    city_name = State()


@router.message(Command("weather"))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer(text='Предоставьте данные о городе, в котором вы хотите узнать прогноз погоды.🌍😊',
                         reply_markup=get_weather_forecast_type_kb()
                         )
    await state.set_state(Weather.forecast_type)


@router.message(F.location, Weather.forecast_type)
async def send_weather_by_geo(message: types.Message, state: FSMContext):
    timezone = await db.get_timezone(user_id=message.from_user.id)

    try:
        forecast_msg = await message.answer(
            text=get_today_forecast(city_data=[message.location.latitude, message.location.longitude],
                                    timezone=timezone
                                    ),
            reply_markup=get_weather_inline_kb(),
            parse_mode="HTML"
        )

        await message.answer(
            text="Для управления прогнозом воспользуйтесь кнопками выше.",
            reply_markup=types.ReplyKeyboardRemove()
            )

        await db.set_last_city_data(user_id=message.from_user.id,
                                    city_data=f"{message.location.latitude}, {message.location.longitude}"
                                    )
        await db.set_forecast_msg_id(user_id=message.from_user.id, msg_id=forecast_msg.message_id)

        await state.clear()
    except KeyError:
        await message.answer(
            text="Не удалось найти такой город. Пожалуйста, отправьте геолокацию еще раз, или напишите название города вручную.",
            reply_markup=get_weather_forecast_type_kb()
        )
    except requests.exceptions.RequestException:
        await message.answer(text="Произошла ошибка при отправке запроса к сервису погоды.😰 Пожалуйста, попробуйте позже.🙏")


@router.message(F.text == "Ввести название города вручную", Weather.forecast_type)
async def send_city_name_rules(message: types.Message, state: FSMContext):
    await message.answer(text=get_rules(), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Weather.city_name)


@router.message(F.text, Weather.city_name)
async def send_weather_by_city_name(message: types.Message, state: FSMContext):
    timezone = await db.get_timezone(user_id=message.from_user.id)
    try:
        forecast_msg = await message.answer(
            text=get_today_forecast(city_data=message.text, timezone=timezone),
            reply_markup=get_weather_inline_kb(),
            parse_mode="HTML"
        )

        await message.answer(
            text="Для управления прогнозом воспользуйтесь кнопками выше.",
            reply_markup=types.ReplyKeyboardRemove()
        )

        await db.set_last_city_data(user_id=message.from_user.id, city_data=message.text)
        await db.set_forecast_msg_id(user_id=message.from_user.id, msg_id=forecast_msg.message_id)

        await state.clear()
    except KeyError:
        return await message.answer(text="Не удалось найти такой город. Попробуйте написать его название латиницей или указать более крупный город поблизости.")
    except requests.exceptions.RequestException:
        await message.answer(text="Произошла ошибка при отправке запроса к сервису погоды.😰 Пожалуйста, попробуйте позже.🙏")


@router.callback_query(F.data == "wthr_update")
async def callback_update_weather_data(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    timezone = await db.get_timezone(user_id=callback.from_user.id)
    current_datetime = get_timezone_time(timezone)
    formatted_datetime = f"{current_datetime['date']} в {current_datetime['time']}"
    city_data = await db.get_last_city_data(user_id=callback.from_user.id)

    try:
        await bot.edit_message_text(
            text=f"[Обновлено {formatted_datetime}]\n" + get_today_forecast(city_data=city_data, timezone=timezone),
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=get_weather_inline_kb(),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        await callback.answer(text="Пожалуйста, не спамьте кнопочки!🥲")
    except KeyError:
        await callback.message.answer(
            text="Ой! Какая-то ошибка. Для получения прогноза, пожалуйста, предоставьте данные о городе заново.",
            reply_markup=get_weather_forecast_type_kb()
        )
        await callback.answer()
        await state.set_state(Weather.forecast_type)
    except requests.exceptions.RequestException:
        await callback.message.answer(text="Произошла ошибка при отправке запроса к сервису погоды.😰 Пожалуйста, попробуйте позже.🙏")
        await callback.answer()


@router.callback_query(F.data == "wthr_location")
async def callback_send_new_location(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.answer(text="Отправьте новую локацию.", reply_markup=get_request_location_kb())
        await callback.answer()
        await state.set_state(Weather.forecast_type)
    except TelegramBadRequest:
        await callback.answer(text="Пожалуйста, не спамьте кнопочки!🥲")


@router.callback_query(F.data == "wthr_input_city")
async def callback_input_new_city_name(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.answer(text="Введите новое название города.", reply_markup=types.ReplyKeyboardRemove())
        await callback.answer()
        await state.set_state(Weather.city_name)
    except TelegramBadRequest:
        await callback.answer(text="Пожалуйста, не спамьте кнопочки!🥲")


@router.callback_query(F.data == "wthr_show_4_days")
async def callback_show_4_days(callback: types.CallbackQuery, state: FSMContext):
    try:
        city_data = await db.get_last_city_data(user_id=callback.from_user.id)
        timezone = await db.get_timezone(user_id=callback.from_user.id)

        forecast_today = get_today_forecast(city_data=city_data, timezone=timezone)
        forecast_4_days = get_4_days_forecast(city_data=city_data, timezone=timezone)

        await callback.message.edit_text(
            text=f"{forecast_today}{forecast_4_days}",
            reply_markup=get_weather_4_days_inline_kb(),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        await callback.answer(text="Пожалуйста, не спамьте кнопочки!🥲")
    except KeyError:
        await callback.message.answer(
            text="Ой! Какая-то ошибка. Для получения прогноза, пожалуйста, предоставьте данные о городе заново.",
            reply_markup=get_weather_forecast_type_kb()
        )
        await callback.answer()
        await state.set_state(Weather.forecast_type)
    except requests.exceptions.RequestException:
        await callback.message.answer(
            text="Произошла ошибка при отправке запроса к сервису погоды.😰 Пожалуйста, попробуйте позже.🙏")
        await callback.answer()


@router.callback_query(F.data == "wthr_hide_4_days")
async def callback_hide_4_days(callback: types.CallbackQuery, state: FSMContext):
    try:
        city_data = await db.get_last_city_data(user_id=callback.from_user.id)
        timezone = await db.get_timezone(user_id=callback.from_user.id)

        await callback.message.edit_text(text=get_today_forecast(city_data=city_data, timezone=timezone),
                                         reply_markup=get_weather_inline_kb(),
                                         parse_mode="HTML"
                                         )
    except TelegramBadRequest:
        await callback.answer(text="Пожалуйста, не спамьте кнопочки!🥲")
    except KeyError:
        await callback.message.answer(
            text="Ой! Какая-то ошибка. Для получения прогноза, пожалуйста, предоставьте данные о городе заново.",
            reply_markup=get_weather_forecast_type_kb()
        )
        await callback.answer()
        await state.set_state(Weather.forecast_type)
    except requests.exceptions.RequestException:
        await callback.message.answer(
            text="Произошла ошибка при отправке запроса к сервису погоды.😰 Пожалуйста, попробуйте позже.🙏")
        await callback.answer()
