from aiogram import types


def make_inline_keyboard(data):
    object_col = []
    for watch in data['watch']:
        inline_declar = types.InlineKeyboardMarkup(row_width=5)
        inline_key = []
        for title in watch['quality'].keys():
            mp4_file = watch['quality'][title]['mp4']
            # if mp4_file:
            #     inline_key.append((title, mp4_file))
            inline_key.append((title, mp4_file))
        declar_keys = (types.InlineKeyboardButton(title, url=href) for title, href in tuple(inline_key))
        object_col.append((watch['name'], inline_declar.add(*declar_keys)))
    return object_col


markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add('🎥 Показати новинки Топ-10')
markup.add('🔎 Пошук')
