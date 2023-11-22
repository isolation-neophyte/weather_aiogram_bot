from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_weather_forecast_type_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Отправить геолокацию", request_location=True)],
        [KeyboardButton(text="Ввести название города вручную")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_request_location_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Отправить геолокацию", request_location=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_weather_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    btn_1 = InlineKeyboardButton(text="Обновить данные", callback_data="wthr_update")
    btn_2 = InlineKeyboardButton(text="Отправить новую геолокацию", callback_data="wthr_location")
    btn_3 = InlineKeyboardButton(text="Ввести новое название города", callback_data="wthr_input_city")
    btn_4 = InlineKeyboardButton(text="Показать прогноз на 4 дня", callback_data="wthr_show_4_days")

    builder.add(btn_1, btn_2, btn_3, btn_4)
    builder.adjust(1)

    return builder.as_markup()


def get_weather_4_days_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    btn_1 = InlineKeyboardButton(text="Обновить данные", callback_data="wthr_update")
    btn_2 = InlineKeyboardButton(text="Отправить новую геолокацию", callback_data="wthr_location")
    btn_3 = InlineKeyboardButton(text="Ввести новое название города", callback_data="wthr_input_city")
    btn_4 = InlineKeyboardButton(text="Скрыть прогноз на 4 дня", callback_data="wthr_hide_4_days")

    builder.add(btn_1, btn_2, btn_3, btn_4)
    builder.adjust(1)

    return builder.as_markup()


def get_edit_subscription_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Управление подпиской", callback_data="sub_edit"))

    return builder.as_markup()


def get_edit_sub_menu_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    btn_1 = InlineKeyboardButton(text="Изменить данные о городе", callback_data="sub_edit_city")
    btn_2 = InlineKeyboardButton(text="Изменить время получения рассылки", callback_data="sub_edit_time")
    btn_3 = InlineKeyboardButton(text="Отменить подписку", callback_data="sub_cancel")

    builder.add(btn_1, btn_2, btn_3)
    builder.adjust(1)

    return builder.as_markup()


def get_cancel_sub_kb() -> ReplyKeyboardMarkup:

    kb = [
        [KeyboardButton(text="Нет, я не хочу отменять подписку!")],
        [KeyboardButton(text="Да, я хочу отменить подписку. (😭)")]
    ]

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)



