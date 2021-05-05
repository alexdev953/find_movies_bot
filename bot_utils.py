from aiogram import types


def make_inline_keyboard(data):
    object_col = []
    for watch in data['watch']:
        inline_declar = types.InlineKeyboardMarkup(row_width=5)
        inline_key = []
        for title in watch['quality'].keys():
            inline_key.append((title, watch['quality'][title]['mp4']))
        declar_keys = (types.InlineKeyboardButton(title, url=href) for title, href in tuple(inline_key))
        object_col.append((watch['name'], inline_declar.add(*declar_keys)))
    return object_col
