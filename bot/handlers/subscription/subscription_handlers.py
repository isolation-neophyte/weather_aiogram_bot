from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.database.database import db
from bot.filters.subscription import IsUserNotSubscribed
from bot.middlewares.timezone import HasTimezoneMessageMiddleware, HasTimezoneCallbackMiddleware
from bot.keyboards.user_keyboards import get_weather_forecast_type_kb
from bot.handlers.weather.weather_functions import get_rules, get_timezone, is_valid_time, format_time

router = Router()
router.message.middleware(HasTimezoneMessageMiddleware())
router.message.middleware(HasTimezoneCallbackMiddleware())


class Subscription(StatesGroup):
    city_data_type = State()
    city_data = State()
    time = State()


@router.message(Command("edit_sub"), IsUserNotSubscribed())
async def edit_subscription_command_redirect(message: types.Message):
    await message.answer(
        text="Вы еще не подписаны на ежедневную рассылку погоды.😰 Чтобы подписаться отправьте команду <b>/subscribe</b>",
        parse_mode="HTML"
    )


@router.message(Command("subscribe"))
async def subscribe_command(message: types.Message, state: FSMContext):
    if not await db.is_user_subscribed(message.from_user.id):
        await message.answer(
            text="Выберите способ предоставления города, для которого вы хотели бы получать прогноз погоды.",
            reply_markup=get_weather_forecast_type_kb()
            )
        await state.set_state(Subscription.city_data_type)
    else:
        await message.answer(
            text="Вы уже подписаны на ежедневную рассылку погоды! Для управления подпиской отправьте команду <b>/edit_sub</b>",
            parse_mode="HTML"
        )


@router.message(F.text == "Ввести название города вручную", Subscription.city_data_type)
async def subscription_send_city_title_rules(message: types.Message, state: FSMContext):
    await message.answer(text=get_rules(), reply_markup=types.ReplyKeyboardRemove())

    await state.set_state(Subscription.city_data)


@router.message(F.location, Subscription.city_data_type)
async def create_subscription_by_location(message: types.Message, state: FSMContext):
    await state.update_data(city_data=f"{message.location.latitude}, {message.location.longitude}")

    await message.answer(text="Пожалуйста, выберите удобное для вас время получения прогноза. Напишите время в формате Часы:Минуты (прим. 12:00, 14.30 или 21 46).\n❗️Прогноз отправляется один раз в день, но у вас всегда будет возможность обновить данные")

    await state.set_state(Subscription.time)


@router.message(F.text, Subscription.city_data)
async def create_subscription_by_title(message: types.Message, state: FSMContext):
    if get_timezone(message.text):
        await state.update_data(city_data=message.text)

        await message.answer(text="Пожалуйста, выберите удобное для вас время получения прогноза. Напишите время в формате Часы:Минуты (прим. 12:00, 14.30 или 21 46).\n❗️Прогноз отправляется один раз в день, но у вас всегда будет возможность обновить данные")

        await state.set_state(Subscription.time)
    else:
        await message.answer(text="Не удалось найти такой город. Попробуйте написать его название латиницей или указать более крупный город поблизости.")


@router.message(F.text, Subscription.time)
async def create_subscription(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if is_valid_time(message.text):
        await db.create_subscription(sub_city_data=user_data["city_data"],
                                     sub_forecast_time=format_time(message.text),
                                     user_id=message.from_user.id
                                     )

        await message.answer(text="Ура!🎉 Вы успешно подписались на ежедневную рассылку прогноза погоды.✅ \nДля редактирования города и времени воспользуйтесь командой /edit_sub")
        await state.clear()
    else:
        await message.answer(text="Неверный формат написания времени. Пожалуйста, напишите только время в формате ЧЧ:ММ.\nЧасы и минуты должны разделяться двоеточием(:), точкой(.) или пробелом.")
