from telebot import types


def start_bot_location_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    share_location_button = types.KeyboardButton('📍Share Location', request_location=True)
    search_location_button = types.KeyboardButton('🗺️Search Location')
    markup.row(share_location_button, search_location_button)
    return markup


def cancel_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = types.KeyboardButton('❌Cancel')
    markup.add(cancel_button)
    return markup


def remove_buttons():
    return types.ReplyKeyboardRemove()


def remove_inline_buttons():
    return types.InlineKeyboardMarkup()


def weather_type_buttons():
    markup = types.InlineKeyboardMarkup()
    now_button = types.InlineKeyboardButton('Now', callback_data='Now')
    today_button = types.InlineKeyboardButton('Today', callback_data='TodayWeather')
    tomorrow_button = types.InlineKeyboardButton('Tomorrow', callback_data='TomorrowWeather')
    back_button = types.InlineKeyboardButton('⬅️ Back', callback_data='Back')
    markup.row(now_button, today_button, tomorrow_button)
    markup.add(back_button)
    return markup
