from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.database.database import db
from bot.handlers.weather.weather_handlers import Weather
from bot.keyboards.user_keyboards import get_weather_forecast_type_kb
from bot.handlers.weather.weather_functions import get_description, get_help_command_text, get_timezone, get_rules

router = Router()


class TimezoneEdit(StatesGroup):
    city_name = State()


@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    await message.answer(text=get_description())
    if not await db.is_user_exists(message.from_user.id):
        await message.answer(text="Для начала работы предоставьте данные о вашем часовом поясе.🕐 Для этого просто напишите название города, в котором вы находитесь.✍️")
        await state.set_state(TimezoneEdit.city_name)
    else:
        await message.answer(text='Предоставьте данные о городе, в котором вы хотите узнать прогноз погоды.🌍😊\n\nЕсли вас не интересует прогноз погоды, просто напишите "отмена" или отправьте команду <b>/cancel</b>.\nДля получения списка команд отправьте команду <b>/help</b>.💕',
                             reply_markup=get_weather_forecast_type_kb(),
                             parse_mode="HTML"
                             )
        await state.set_state(Weather.forecast_type)


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cancel_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено.\nДля получения списка команд отправьте команду <b>/help</b>.",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
@router.message(F.text.lower() == "помощь")
async def help_command(message: types.Message):
    await message.answer(text=get_help_command_text(), reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")


@router.message(Command("set_timezone"))
async def set_timezone_command(message: types.Message, state: FSMContext):
    await message.answer(
        text="Напишите название города, в котором вы находитесь.✍️",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(TimezoneEdit.city_name)


@router.message(F.text, TimezoneEdit.city_name)
async def edit_timezone(message: types.Message, state: FSMContext):
    timezone = get_timezone(message.text)

    if timezone:
        if not await db.is_user_exists(user_id=message.from_user.id):
            await db.create_user(user_id=message.from_user.id)

        await db.set_timezone(user_id=message.from_user.id, timezone=timezone)

        await message.answer(
            text=f"Часовой пояс установлен в {timezone}. Спасибо!\n\n<em>Для получения прогноза погоды отправьте команду <b>/weather</b>. Список всех доступных команд доступен по команде <b>/help</b></em>.😊",
            parse_mode="HTML"
            )
        await state.clear()
    else:
        await message.answer(text="Не удалось найти такой город. Попробуйте написать его название латиницей или указать более крупный город поблизости.\nТакже ознакомьтесь с рекомендациями написания названия города:")
        await message.answer(text=get_rules())
