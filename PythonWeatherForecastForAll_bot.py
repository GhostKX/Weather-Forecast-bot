import math
import telebot

import Buttons
import Buttons as bt
import requests
from datetime import datetime
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()
API_KEY = str(os.getenv('API_KEY'))
bot = telebot.TeleBot(API_KEY)

API_key_weather = str(os.getenv('API'))

trash_messages = []
today_weather = []
tomorrow_weather = []
seven_days_weather = []

# Dictionary to track user states
user_states = {}

# Mapping of OpenWeatherMap icon codes to emojis
icon_code = {
    '01d': '☀️',  # Clear sky (day)
    '02d': '⛅',  # Few clouds (day)
    '03d': '☁️',  # Scattered clouds (day)
    '04d': '☁️',  # Broken clouds (day)
    '09d': '🌧️',  # Shower rain (day)
    '10d': '🌧️',  # Rain (day)
    '11d': '⛈️',  # Thunderstorm (day)
    '13d': '❄️',  # Snow (day)
    '50d': '🌫️',  # Mist (day)
    '01n': '🌙',  # Clear sky (night)
    '02n': '☁️',  # Few clouds (night)
    '03n': '☁️',  # Scattered clouds (night)
    '04n': '☁️',  # Broken clouds (night)
    '09n': '🌧️',  # Shower rain (night)
    '10n': '🌧️',  # Rain (night)
    '11n': '⛈️',  # Thunderstorm (night)
    '13n': '❄️',  # Snow (night)
    '50n': '💨'   # Mist (night)
}

# Mapping of WeatherAPI condition codes to emojis for night-time
night_icon_code_to_emoji = {
    1000: "🌙",  # Clear
    1003: "☁️",  # Partly Cloudy
    1006: "☁️",  # Cloudy
    1009: "☁️",  # Overcast
    1030: "🌫️",  # Mist
    1063: "🌧️",  # Patchy Rain
    1066: "🌨️ ❄️",  # Patchy Snow
    1072: "🌧️",  # Freezing Drizzle
    1087: "⛈️",  # Thunder
    1114: "🌬️",  # Blowing Snow
    1135: "🌁",  # Fog
    1150: "🌧️",
    1153: "🌦️",  # Light Drizzle
    1180: "🌧️",
    1186: "🌧️",  # Light Rain Shower
    1210: "🌨️ ❄️",  # Light Snow Shower
    1243: "🌧️",  # Moderate Rain
    1273: "⛈️",  # Thunderstorm
    1282: "🌪️"  # Blizzard
}

# Mapping of weather condition descriptions to emojis
condition_to_emoji = {
    "Clear": "☀️",
    "Sunny": "☀️",
    "Partly Cloudy": "⛅",
    "Cloudy": "☁️",
    "Overcast": "🌥️",
    "Mist": "🌫️",
    "Patchy Rain": "🌦️",
    "Patchy Rain Nearby": "🌦️",
    "Patchy Snow": "🌨️",
    "Freezing Drizzle": "🌧️",
    "Thunder": "⛈️",
    "Blowing Snow": "🌬️",
    "Fog": "🌁",
    "Light Rain Shower": "🌦️",
    "Light Snow Shower": "🌨️",
    "Moderate Rain": "🌧️",
    "Thunderstorm": "⛈️",
    "Blizzard": "🌪️",
    "Light Sleet": "🌨️",  # Added missing key
}

city_name_list = []

# Mapping of weather condition descriptions to emojis for 7-day forecasts
condition_to_emoji_7_days = {
    "Thunderstorm with light rain": "⛈️",  # Thunderstorm
    "Thunderstorm with rain": "⛈️",  # Thunderstorm
    "Thunderstorm with heavy rain": "⛈️",  # Thunderstorm
    "Thunderstorm with light drizzle": "⛈️",  # Thunderstorm
    "Thunderstorm with drizzle": "⛈️",  # Thunderstorm
    "Thunderstorm with heavy drizzle": "⛈️",  # Thunderstorm
    "Thunderstorm with Hail": "⛈️",  # Thunderstorm
    "Light Drizzle": "🌦️",  # Drizzle
    "Drizzle": "🌦️",  # Drizzle
    "Heavy Drizzle": "🌧️",  # Heavy drizzle
    "Light Rain": "🌦️",  # Light rain
    "Moderate Rain": "🌧️",  # Moderate rain
    "Heavy Rain": "🌧️",  # Heavy rain
    "Freezing rain": "🌧️",  # Freezing rain
    "Light shower rain": "🌦️",  # Light shower rain
    "Shower rain": "🌧️",  # Shower rain
    "Heavy shower rain": "🌧️",  # Heavy shower rain
    "Light snow": "🌨️",  # Light snow
    "Snow": "🌨️",  # Snow
    "Heavy Snow": "❄️",  # Heavy snow
    "Mix snow/rain": "🌨️",  # Mix snow/rain
    "Sleet": "🌨️",  # Sleet
    "Heavy sleet": "🌨️",  # Heavy sleet
    "Snow shower": "🌨️",  # Snow shower
    "Heavy snow shower": "❄️",  # Heavy snow shower
    "Flurries": "❄️",  # Flurries
    "Mist": "🌫️",  # Mist
    "Smoke": "🌫️",  # Smoke
    "Haze": "🌫️",  # Haze
    "Sand/dust": "🌫️",  # Sand/dust
    "Fog": "🌫️",  # Fog
    "Freezing Fog": "🌫️",  # Freezing fog
    "Clear sky": "☀️",  # Clear sky
    "Few clouds": "⛅",  # Few clouds
    "Scattered clouds": "⛅",  # Scattered clouds
    "Broken clouds": "☁️",  # Broken clouds
    "Overcast clouds": "☁️",  # Overcast clouds
    "Unknown Precipitation": "❓"  # Unknown precipitation
}


@bot.message_handler(commands=['start'])
def start_bot(message):
    user_id = message.from_user.id
    bot.send_message(user_id, f'Welcome to the 🌦️Weather bot ⛈️', reply_markup=bt.start_bot_location_buttons())
    bot.register_next_step_handler(message, location_type)


@bot.message_handler(content_types=['text'])
def location_type(message):
    user_id = message.from_user.id
    if message.location:
        delete_trash_messages(user_id)
        latitude = message.location.latitude
        longitude = message.location.longitude
        bot.send_message(user_id, '🌏 Sharing location...', reply_markup=bt.remove_buttons())
        url = requests.get(f'https://api.weatherapi.com/v1/current.json?'
                           f'key={API_key_weather}&q={latitude},{longitude}&aqi=yes')
        if url.status_code == 200:
            weather_data = url.json()
            city_name = weather_data['location']['name']
            if len(city_name_list) == 0:
                city_name_list.append(city_name)
            else:
                pass
            country_name = weather_data['location']['country']
            bot.send_message(user_id, f'✅ {city_name}, {country_name} ✅')
            bot_response = bot.send_message(user_id, f'\n\n🌦️Weather🌤️ Forecast buttons below 💬',
                                            reply_markup=bt.weather_type_buttons())
            trash_messages.append(bot_response.message_id)
            user_states[user_id] = 'waiting_for_buttons'  # Set the state to waiting for button press
            bot.register_next_step_handler(message, weather_type_handler)
    elif message.text == '🗺️Search Location':
        delete_trash_messages(user_id)
        bot.send_message(user_id, 'Please type in city name 🏙️', reply_markup=bt.cancel_buttons())
        bot.register_next_step_handler(message, search_location)
    else:
        trash_user_message = message.message_id
        trash_messages.append(trash_user_message)
        bot_trash_response = bot.send_message(user_id, '‼️ Error ‼️'
                                                       '️\n\n⬇️Please use buttons below ⬇️',
                                              reply_markup=bt.start_bot_location_buttons())
        trash_messages.append(bot_trash_response.message_id)
        bot.register_next_step_handler(message, location_type)


def search_location(message):
    user_id = message.from_user.id
    city_name = message.text
    if city_name == '❌Cancel':
        delete_trash_messages(user_id)
        bot.send_message(user_id, '⬅️ Getting back', reply_markup=bt.start_bot_location_buttons())
        bot.register_next_step_handler(message, location_type)
    else:
        try:
            url = requests.get(f'https://api.weatherapi.com/v1'
                               f'/current.json?key={API_key_weather}&q={city_name}&aqi=yes')
            if url.status_code == 200:
                delete_trash_messages(user_id)
                weather_data = url.json()
                city_name = weather_data['location']['name']
                latitude = weather_data['location']['lat']
                longitude = weather_data['location']['lon']
                if len(city_name_list) == 0:
                    city_name_list.append(city_name)
                    city_name_list.append(latitude)
                    city_name_list.append(longitude)
                else:
                    pass
                bot.send_message(user_id, f'✅ "{city_name}" city name is successfully received ✅',
                                 reply_markup=bt.remove_buttons())
                bot_response = bot.send_message(user_id, f'\n\n⬇️ Please choose weather forecast by using buttons '
                                                         f'below 💬 ⬇️',
                                                reply_markup=bt.weather_type_buttons())
                trash_messages.append(bot_response.message_id)
                user_states[user_id] = 'waiting_for_buttons'  # Set the state to waiting for button press
                bot.register_next_step_handler(message, error_message)
            else:
                trash_user_message = message.message_id
                trash_messages.append(trash_user_message)
                bot_trash_response = bot.send_message(user_id, '❌ ERROR: Could not find location\n\n'
                                                               'Please try again 💬',
                                                      reply_markup=bt.cancel_buttons())
                trash_messages.append(bot_trash_response.message_id)
                bot.register_next_step_handler(message, search_location)
        except ValueError:
            bot_trash_response = bot.send_message(user_id, '❌ ERROR: Could not find location\n\n'
                                                           'Please try to check network connection 💬',
                                                  reply_markup=bt.cancel_buttons())
            trash_messages.append(bot_trash_response.message_id)
            bot.register_next_step_handler(message, search_location)


def delete_trash_messages(user_id):
    if len(trash_messages) > 0:
        for i in trash_messages:
            bot.delete_message(user_id, i)
        trash_messages.clear()
    else:
        pass
    return trash_messages


def error_message(message):
    user_id = message.from_user.id
    delete_trash_messages(user_id)
    bot_response = bot.send_message(user_id, '❌ Error ❌', reply_markup=Buttons.remove_inline_buttons())
    trash_messages.append(bot_response.message_id)
    bot_response = bot.send_message(user_id, f'\n\n\n⬇️ Please choose weather forecast by using buttons '
                              f'below 💬 ⬇️', reply_markup=Buttons.weather_type_buttons())
    trash_messages.append(bot_response.message_id)


@bot.callback_query_handler(
    func=lambda call: call.data in ('Now', 'TodayWeather', 'TomorrowWeather', 'For3Days', 'Back'))
def weather_type_handler(call):
    user_id = call.from_user.id
    delete_trash_messages(user_id)
    if call.data == 'Now':
        delete_trash_messages(user_id)
        url = requests.get(f'https://api.weatherapi.com/v1'
                           f'/current.json?key={API_key_weather}&q={city_name_list[0]}&aqi=yes')
        if url.status_code == 200:
            weather_data = url.json()
            city_name = weather_data['location']['name']
            country_name = weather_data['location']['country']
            temp_c = math.floor(weather_data['current']['temp_c'])
            weather_description = weather_data['current']['condition']['text'].title().strip()
            is_day = weather_data['current']['is_day']
            humidity = weather_data['current']['humidity']
            local_time = weather_data['location']['localtime']
            icon = weather_data['current']['condition']['code']
            dt = datetime.strptime(local_time, '%Y-%m-%d %H:%M')
            formatted_time = dt.strftime("%H:%M")  # %H for 24-hour format
            formatted_date = dt.strftime("%d of %B %Y")

            if is_day == 1:
                bot.send_message(user_id,
                                 f'{'-' * 47}'
                                 f'\n🌏 Weather in {city_name}, {country_name}'
                                 f'\n\n🗓️ Datetime: {formatted_time}, {formatted_date}'
                                 f'\n🌡️Temperature: {temp_c}°C {condition_to_emoji[weather_description]}'
                                 f'\n🌆 Condition: {weather_description}'
                                 f'\n💧 Humidity: {humidity}%'
                                 f'\n{'-' * 47}')
                bot_response = bot.send_message(user_id, f'\n\n⬇️ Get Weather Forecast by using buttons below 💬 ⬇️',
                                                reply_markup=bt.weather_type_buttons())
                trash_messages.append(bot_response.message_id)
                bot.register_next_step_handler(call.message, error_message)
            else:
                bot.send_message(user_id,
                                 f'{'-' * 47}'
                                 f'\n🌏 Weather in {city_name}, {country_name}'
                                 f'\n\n🗓️ Datetime: {formatted_time}, {formatted_date}'
                                 f'\n🌡️Temperature: {temp_c}°C {night_icon_code_to_emoji[icon]}'
                                 f'\n🌃 Condition: {weather_description}'
                                 f'\n💧 Humidity: {humidity}%'
                                 f'\n{'-' * 47}')

                bot_response = bot.send_message(user_id, f'\n\n⬇️ Get Weather Forecast by using buttons below 💬 ⬇️',
                                                reply_markup=bt.weather_type_buttons())
                trash_messages.append(bot_response.message_id)
                bot.register_next_step_handler(call.message, error_message)
        else:
            bot.send_message(user_id, '❌ ERROR: Could not find location'
                                      '\n\nPlease try to check network connection 💬',
                             reply_markup=bt.weather_type_buttons())
            bot.register_next_step_handler(call.message, error_message)
    elif call.data == 'TodayWeather':
        delete_trash_messages(user_id)
        url = requests.get('https://api.weatherapi.com/v1/'
                           f'forecast.json?key={API_key_weather}&q={city_name_list[0]}'
                           f'&days=1&aqi=no&alerts=no')
        if url.status_code == 200:
            weather_data = url.json()
            message_to_user = f'{'⌚️Time':<15}{'🌡️°C':<15}{'✨Sky':<15}{'Icon':<15}'
            message_to_user += f'\n{'_' * 40}'
            forecast_day = weather_data['forecast']['forecastday'][0]
            sunrise = forecast_day['astro']['sunrise']
            sunset = forecast_day['astro']['sunset']
            for hour_data in forecast_day['hour']:
                time = hour_data['time']
                temp_c = hour_data['temp_c']
                temp_c = math.floor(temp_c)
                is_day = hour_data['is_day']
                text = hour_data['condition']['text'].title().strip()
                night_icon = hour_data['condition']['code']
                dt = datetime.strptime(time, '%Y-%m-%d %H:%M')
                formatted_time = dt.strftime("%H:%M")  # %H for 24-hour format
                formatted_date = dt.strftime("🗓️ %d of %B %Y")
                today_weather.append(formatted_date)
                if is_day == 1:
                    day_icon = condition_to_emoji[text]
                    message_to_user += f'\n\n{formatted_time:<17}{f'{temp_c}°C':<17}{text:<17}{day_icon:<15}'
                else:
                    night_icon = night_icon_code_to_emoji[night_icon]
                    message_to_user += f'\n\n{formatted_time:<17}{f'{temp_c}°C':<17}{text:<17}{night_icon:<15}'

            bot.send_message(user_id, f'\n\n\n\n{today_weather[0]}'
                                      f'\n{'*' * 45}'
                                      f'\n{message_to_user}'
                                      f'\n{'_' * 40}'
                                      f'\n\n🌅 Sunrise: {sunrise}'
                                      f'\n\n🌃 Sunset: {sunset}', reply_markup=bt.remove_buttons())
            bot_trash_response = bot.send_message(user_id, f'\n\n{'*' * 45}'
                                                           f'\n\n⬇️ Get Weather Forecast by using buttons below 💬 ⬇️',
                                                  reply_markup=bt.weather_type_buttons())
            trash_messages.append(bot_trash_response.message_id)
            bot.register_next_step_handler(call.message, error_message)
        else:
            bot.send_message(user_id, '❌ ERROR: Could not find location'
                                      '\n\nPlease try to check network connection 💬',
                             reply_markup=bt.weather_type_buttons())
            bot.register_next_step_handler(call.message, error_message)
    elif call.data == 'TomorrowWeather':
        delete_trash_messages(user_id)
        url = requests.get(f'https://api.weatherapi.com/v1/forecast.json?'
                           f'key={API_key_weather}&q={city_name_list[0]}&days=2&aqi=no&alerts=no')
        if url.status_code == 200:
            weather_data = url.json()
            message_to_user = f'{'⌚️Time':<15}{'🌡️°C':<15}{'✨Sky':<15}{'Icon':<15}'
            message_to_user += f'\n{'_' * 40}'
            forecast_day = weather_data['forecast']['forecastday'][1]
            sunrise = forecast_day['astro']['sunrise']
            sunset = forecast_day['astro']['sunset']
            for hour_data in forecast_day['hour']:
                time = hour_data['time']
                temp_c = hour_data['temp_c']
                temp_c = math.floor(temp_c)
                is_day = hour_data['is_day']
                text = hour_data['condition']['text'].title().strip()
                night_icon = hour_data['condition']['code']
                dt = datetime.strptime(time, '%Y-%m-%d %H:%M')
                formatted_time = dt.strftime("%H:%M")  # %H for 24-hour format
                formatted_date = dt.strftime("🗓️ %d of %B %Y")
                tomorrow_weather.append(formatted_date)
                if is_day == 1:
                    day_icon = condition_to_emoji[text]
                    message_to_user += f'\n\n{formatted_time:<17}{f'{temp_c}°C':<17}{text:<17}{day_icon:<15}'
                else:
                    night_icon = night_icon_code_to_emoji[night_icon]
                    message_to_user += f'\n\n{formatted_time:<17}{f'{temp_c}°C':<17}{text:<17}{night_icon:<15}'

            bot.send_message(user_id, f'\n\n\n\n{tomorrow_weather[0]}'
                                      f'\n{'*' * 45}'
                                      f'\n{message_to_user}'
                                      f'\n{'_' * 40}'
                                      f'\n\n🌅 Sunrise: {sunrise}'
                                      f'\n\n🌃 Sunset: {sunset}', reply_markup=bt.remove_buttons())
            bot_trash_response = bot.send_message(user_id, f'\n\n{'*' * 45}'
                                                           f'\n\n⬇️ Get Weather Forecast by using buttons below 💬 ⬇️',
                                                  reply_markup=bt.weather_type_buttons())
            trash_messages.append(bot_trash_response.message_id)
            bot.register_next_step_handler(call.message, error_message)
        else:
            bot.send_message(user_id, '❌ ERROR: Could not find location'
                                      '\n\nPlease try to check network connection 💬',
                             reply_markup=bt.weather_type_buttons())
            bot.register_next_step_handler(call.message, error_message)
    elif call.data == 'Back':
        delete_trash_messages(user_id)
        city_name_list.clear()
        today_weather.clear()
        tomorrow_weather.clear()
        seven_days_weather.clear()
        user_states.clear()
        bot.send_message(user_id, '🔙 To Menu', reply_markup=bt.start_bot_location_buttons())
        bot.register_next_step_handler(call.message, location_type)


# Running the bot infinitely
bot.polling(non_stop=True)
