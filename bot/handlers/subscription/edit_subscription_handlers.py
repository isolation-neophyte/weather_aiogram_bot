from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.database.database import db
from bot.filters.subscription import IsUserSubscribed
from bot.keyboards.user_keyboards import get_weather_forecast_type_kb, get_edit_sub_menu_inline_kb, get_cancel_sub_kb
from bot.handlers.weather.weather_functions import get_rules, is_valid_time, format_time
from bot.middlewares.timezone import HasTimezoneMessageMiddleware, HasTimezoneCallbackMiddleware


router = Router()
router.message(IsUserSubscribed())
router.message.middleware(HasTimezoneMessageMiddleware())
router.message.middleware(HasTimezoneCallbackMiddleware())


class EditSubscription(StatesGroup):
    edit_city = State()
    edit_time = State()
    cancel = State()


@router.message(Command("edit_sub"))
async def edit_subscription_command(message: types.Message):
    await message.answer(
        text="Добро пожаловать в меню редактирования подписки на ежедневную рассылку прогноза погоды.",
        reply_markup=get_edit_sub_menu_inline_kb()
    )


@router.callback_query(F.data == "sub_edit_city")
async def sub_edit_choose_type_city_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Пожалуйста, выберите способ предоставления нового города, для которого вы хотели бы получать прогноз погоды.",
                                  reply_markup=get_weather_forecast_type_kb()
                                  )
    await callback.answer()
    await state.set_state(EditSubscription.edit_city)


@router.message(F.location, EditSubscription.edit_city)
async def sub_edit_city_data_by_location(message: types.Message, state: FSMContext):
    await db.set_sub_city_data(user_id=message.from_user.id,
                               city_data=f"{message.location.latitude}, {message.location.longitude}"
                               )
    await message.answer(text="Данные о городе были успешно изменены.✅")
    await state.clear()


@router.message(F.text == "Ввести название города вручную", EditSubscription.edit_city)
async def sub_edit_city_name_rules(message: types.Message):
    await message.answer(text=get_rules())


@router.message(F.text, EditSubscription.edit_city)
async def sub_edit_city_data_by_text(message: types.Message, state: FSMContext):
    await db.set_sub_city_data(user_id=message.from_user.id, city_data=message.text)
    await message.answer(text="Данные о городе были успешно изменены.✅")
    await state.clear()


@router.callback_query(F.data == "sub_edit_time")
async def sub_edit_time_rules(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Пожалуйста, введите новое время получения прогноза. Напишите время в формате Часы:Минуты (прим. 12:00, 14.30 или 21 46)."
    )
    await callback.answer()
    await state.set_state(EditSubscription.edit_time)


@router.message(F.text, EditSubscription.edit_time)
async def sub_edit_time(message: types.Message, state: FSMContext):
    if is_valid_time(message.text):
        await db.set_sub_forecast_time(user_id=message.from_user.id, time=format_time(message.text))
        await message.answer(text="Данные о ремени получения прогноза были успешно изменены.✅",
                             reply_markup=types.ReplyKeyboardRemove()
                             )
        await state.clear()
    else:
        await message.answer(text="Неверный формат написания времени. Пожалуйста, напишите только время в формате ЧЧ:ММ.\nЧасы и минуты должны разделяться двоеточием(:), точкой(.) или пробелом.")


@router.callback_query(F.data == "sub_cancel")
async def sub_edit_cancel_ask_if_user_sure(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Вы уверены, что хотите отменить подписку?😨\nВы можете просто отредактировать время и город!🥺",
        reply_markup=get_cancel_sub_kb()
    )
    await callback.answer()
    await state.set_state(EditSubscription.cancel)


@router.message(F.text, EditSubscription.cancel)
async def sub_cancel(message: types.Message, state: FSMContext):
    if message.text.lower().startswith("да"):
        await db.cancel_subscription(user_id=message.from_user.id)
        await message.answer(text="Вы отменили подписку на ежедневную рассылку погоды.",
                             reply_markup=types.ReplyKeyboardRemove()
                             )
    else:
        await message.answer(text="😘", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
