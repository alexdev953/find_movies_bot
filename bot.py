from aiogram import Bot, Dispatcher, executor, types
from config import bot_token
from find_movie_bot import FindMovies
from bot_utils import make_inline_keyboard
from db_func import DbFunc

# Initialize bot and dispatcher
bot = Bot(token=bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

url_for_search = 'http://baskino.me/films/'


@dp.message_handler(commands=['start'])
async def take_start(message: types.Message):
    DbFunc().check_user(message)
    about_bot = await bot.get_me()
    await message.answer(
        f"Привіт, {message.from_user.first_name}!\nЯ - <b>{about_bot['first_name']}</b>")


@dp.message_handler(text_startswith=[url_for_search])
async def echo(message: types.Message):
    DbFunc().check_user(message)
    answer = FindMovies().find_movies(url=message.text)
    poster_url = answer['poster']
    await message.answer_photo(photo=poster_url)
    for name, inline_keyboard in make_inline_keyboard(answer):
        await message.answer(name, reply_markup=inline_keyboard)


@dp.message_handler(content_types=['text'])
async def take_text(message: types.Message):
    DbFunc().check_user(message)
    if message.text.startswith('/'):
        await message.reply('Перевірьте чи правильно введена команда')
    else:
        await message.reply('Нажаль я ще не все вмію')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
