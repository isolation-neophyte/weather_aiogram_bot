import os
import requests
import re
import pytz

from datetime import datetime
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


def is_valid_time(time):
    time_pattern = r'^\d{1,2}[:. ]\d{2}$'

    if re.match(time_pattern, time):
        parts = re.split(r'[:. ]', time)
        hours, minutes = int(parts[0]), int(parts[1])
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return True
    return False


def format_time(time):
    parts = re.split(r'[:. ]', time)
    return f"{parts[0]}:{parts[1]}"


def get_timezone(city_name: str):
    geolocator = Nominatim(user_agent="weather_isneo_bot")
    location = geolocator.geocode(city_name)

    if location:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        return timezone_str
    else:
        return None


def get_timezone_time(timezone_str):
    tz = pytz.timezone(timezone_str)
    current_time = datetime.now(tz=tz)
    date_str = current_time.strftime("%Y-%m-%d")
    time_str = current_time.strftime("%H:%M:%S")
    return {"date": date_str, "time": time_str}


def get_today_forecast(city_data, timezone):
    current_time = datetime.now(tz=pytz.timezone(timezone))

    base_url = "https://api.openweathermap.org/data/2.5/"
    api_key = os.getenv("OPEN_WEATHER_TOKEN")

    if isinstance(city_data, list):
        lat, lon = city_data
        url_current = f"{base_url}weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=ru"
        url_forecast = f"{base_url}forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=ru"
    else:
        url_current = f"{base_url}weather?q={city_data}&appid={api_key}&units=metric&lang=ru"
        url_forecast = f"{base_url}forecast?q={city_data}&appid={api_key}&units=metric&lang=ru"

    current_weather_data = requests.get(url_current).json()
    forecast_weather_data = requests.get(url_forecast).json()

    forecast_result = f"""<b>Сейчас</b> в городе {current_weather_data['name']}:
        {current_weather_data['weather'][0]['description'].capitalize()}{get_condition_emoji(current_weather_data['weather'][0]['id'])}, {round(current_weather_data['main']['temp'])}°C. 
        Ощущается как {round(current_weather_data['main']['feels_like'])}°C.\n\n<b>Прогноз погоды на сегодня:</b>\n\n"""

    for forecast in forecast_weather_data["list"]:
        weather_date = forecast["dt_txt"].split(" ")[0]
        if current_time.date() == datetime.strptime(weather_date, '%Y-%m-%d').date():
            forecast_result += f"В {forecast['dt_txt'].split(' ')[1][:5]} ожидается {'{0:+3.0f}'.format(forecast['main']['temp'])}, {forecast['weather'][0]['description']}{get_condition_emoji(forecast['weather'][0]['id'])}\n"

    return forecast_result


def get_4_days_forecast(city_data, timezone):
    current_time = datetime.now(tz=pytz.timezone(timezone))

    base_url = "https://api.openweathermap.org/data/2.5/"
    api_key = os.getenv("OPEN_WEATHER_TOKEN")

    if isinstance(city_data, list):
        lat, lon = city_data
        url_forecast = f"{base_url}forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=ru"
    else:
        url_forecast = f"{base_url}forecast?q={city_data}&appid={api_key}&units=metric&lang=ru"

    forecast_user_data = requests.get(url_forecast).json()

    forecast_result = "\n\n<b>Прогноз погоды на следующие 4 дня:</b>\n\n"

    for forecast in forecast_user_data["list"]:
        weather_date = forecast["dt_txt"].split(" ")[0]
        weather_time = forecast["dt_txt"].split(" ")[1]
        if current_time.date() != datetime.strptime(weather_date, '%Y-%m-%d').date() and weather_time == "15:00:00":
            forecast_result += f"{forecast['dt_txt'].split(' ')[0]} ожидается {'{0:+3.0f}'.format(forecast['main']['temp_min'])}, {forecast['weather'][0]['description']}{get_condition_emoji(forecast['weather'][0]['id'])}\n"

    return forecast_result


def get_condition_emoji(weather_id):
    emojis = {"2": "🌩", "3": "🌨", "5": "🌨", "6": "❄️", "7": "🌫"}
    emojis_exceptions = {800: "☀️", 801: "🌤", 802: "🌥", 803: "⛅️", 804: "☁️"}

    if weather_id in (800, 801, 802, 803, 804,):
        return emojis_exceptions[weather_id]
    return emojis[str(weather_id)[0]]


def get_description():
    return """🌦️ Добро пожаловать! 🌦️

С Погода ботом вы всегда будете в курсе актуальной погоды и прогноза на ближайшие 5 дней. Бот предоставляет удобные способы получения погодной информации:

1️⃣ Отправьте боту вашу геолокацию, и вы мгновенно узнаете текущую погоду и прогноз по вашему местоположению.

2️⃣ Просто напишите название города, и бот предоставит вам текущую погоду и прогноз для этого региона.

🕐 Также вы можете подписаться на ежедневную рассылку погоды. Вы выбираете город (его всегда можно изменить) и удобное для себя время, и каждый день в это время вы будете получать сведения о текущей погоде и прогноз.

🌞🌧️❄️"""


def get_rules():
    return """Пожалуйста, отправьте название города. Соблюдение этих правил поможет боту верно определить выбранный вами город:

1. Соблюдайте грамматические правила и пишите без ошибок.

2. Можете написать название города без учета регистра (регистр неважен).

3. Если в названии города есть дефис (прим. "Куала-Лумпур"), рекомендовано его написать."""


def get_help_command_text():
    return """Вы можете выбрать команду из списка ниже или воспользоваться кнопкой на всплывающей клавиатуре.

Список доступных команд:

<b>/weather</b> - узнать погоду в интересующем вас городе.🌞
<b>/subscribe</b> - оформить подписку на ежедневную рассылку погоды.💌🌍
<b>/edit_sub</b> - управление подпиской.📝
<b>/set_timezone</b> - установить часовой пояс.🕐
<b>/cancel</b> - отмена действия (может пригодиться если вы, к примеру, передумаете спрашивать о погоде или отменять подписку на лучший погодный бот когда-либо придуманный человечеством💅)"""
