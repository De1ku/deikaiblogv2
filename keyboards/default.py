from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def defaultState() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="/createPost")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)