from aiogram import Bot, Dispatcher, executor, types
from config import bot_token
from find_movie_bot import FindMovies
import json
# Initialize bot and dispatcher
bot = Bot(token=bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

url_for_search = 'http://baskino.me/films/'


@dp.message_handler(commands=['start'])
async def take_start(message):
    about_bot = await bot.get_me()
    await message.answer(
        f"Привіт, {message.from_user.first_name}!\nЯ - <b>{about_bot['first_name']}</b>")


@dp.message_handler(text_startswith=[url_for_search])
async def echo(message: types.Message):
    answer = FindMovies().find_movies(url=message.text)
    print(answer)
    # print(len(answer))
    inline_declar = types.InlineKeyboardMarkup(row_width=5)
    inline_key = []
    for title in answer['quality'].keys():
        for href in answer['quality'][title]['mp4']:
            inline_key.append((title, href))
            # inline_declar.add(types.InlineKeyboardButton)

    declar_keys = (types.InlineKeyboardButton(title, url=href) for title, href in tuple(inline_key))
    inline_declar.add(*declar_keys)
    poster_url = answer['poster']
    await message.answer_photo(photo=poster_url, reply_markup=inline_declar)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
