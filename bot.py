from aiogram import Bot, Dispatcher, executor, types
from config import bot_token
from find_movie_bot import FindMovies
from bot_utils import make_inline_keyboard, markup
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
        f"Привіт, {message.from_user.first_name}!\nЯ - <b>{about_bot['first_name']}</b>", reply_markup=markup)


@dp.message_handler(text_startswith=[url_for_search])
async def echo(message: types.Message):
    DbFunc().check_user(message)
    answer = FindMovies().find_movies(url=message.text)
    poster_url = answer['poster']
    await message.answer_photo(photo=poster_url)
    for name, inline_keyboard in make_inline_keyboard(answer):
        await message.answer(name, reply_markup=inline_keyboard)


@dp.message_handler(text=['Показати новинки'])
async def take_text(message: types.Message):
    answer_msg = FindMovies().find_newest()

    DbFunc().insert_movies(answer_msg)
    for text in answer_msg[:10]:
        inline_declar = types.InlineKeyboardMarkup()
        inline_declar.add(types.InlineKeyboardButton('Дивитися', callback_data=f"f_id@{text['id_film']}"))
        await message.answer_photo(text['poster'], text['name'], reply_markup=inline_declar)
        # await message.answer(text)


@dp.message_handler(commands=['films'])
async def take_command_user(message: types.Message):
    print(message.text)


@dp.message_handler(content_types=['text'])
async def take_text(message: types.Message):
    DbFunc().check_user(message)
    if message.text.startswith('/'):
        await message.reply('Перевірьте чи правильно введена команда')
    else:
        await message.reply('Нажаль я ще не все вмію')


@dp.callback_query_handler(text_startswith=['f_id'])
async def take_callback(query: types.CallbackQuery):
    answer_data = query.data
    url_film = DbFunc().search_film_id(answer_data.split('@')[1])
    answer = FindMovies().find_movies(url=url_film)
    poster_url = answer['poster']
    await query.message.answer_photo(photo=poster_url)
    for name, inline_keyboard in make_inline_keyboard(answer):
        await query.message.answer(name, reply_markup=inline_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
