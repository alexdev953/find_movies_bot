from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
import os
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add('🎥 Показати новинки Топ-10')
markup.add('🔎 Пошук')

# Inline Keyboard settings
keyboard_inline_state = types.InlineKeyboardMarkup(row_width=1)
keyboard_inline_state.add(types.InlineKeyboardButton('❌ Скасувати', callback_data=f'state_cancel'))


class NextStep(StatesGroup):
    waiting_for_movies_name = State()


def make_inline_keyboard(data):
    object_col = []
    for watch in data['watch']:
        try:
            inline_declar = types.InlineKeyboardMarkup(row_width=5)
            inline_key = []
            for title in watch['quality'].keys():
                mp4_file = watch['quality'][title]['mp4']
                if mp4_file:
                    inline_key.append((title, mp4_file))
            declar_keys = (types.InlineKeyboardButton(title, url=href) for title, href in tuple(inline_key))
            object_col.append((watch['name'], inline_declar.add(*declar_keys)))
        except Exception as e:
            continue
    return object_col


def dump_sql():
    path = '/home/apache/bot.dump.sql'
    os.system(f'sqlite3 bot.db .dump > {path}')
    return path



