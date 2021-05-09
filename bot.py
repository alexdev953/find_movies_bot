from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import bot_token
from find_movie_bot import FindMovies
from bot_utils import make_inline_keyboard, markup
from db_func import DbFunc


memmory_storage = MemoryStorage()
# Initialize bot and dispatcher
bot = Bot(token=bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=memmory_storage)

url_for_search = 'http://baskino.me/films/'
# Inline Keyboard settings
keyboard_inline_state = types.InlineKeyboardMarkup(row_width=1)
keyboard_inline_state.add(types.InlineKeyboardButton('❌ Скасувати', callback_data=f'state_cancel'))


class NextStep(StatesGroup):
    waiting_for_movies_name = State()


@dp.message_handler(lambda message: DbFunc().check_user(message),
                    commands=['start'])
async def take_start(message: types.Message):
    about_bot = await bot.get_me()
    await message.answer(
        f"Привіт, {message.from_user.first_name}!\nЯ - <b>{about_bot['first_name']}</b>", reply_markup=markup)


@dp.message_handler(lambda message: DbFunc().check_user(message),
                    text_startswith=[url_for_search])
async def echo(message: types.Message):
    answer = FindMovies().find_movies(url=message.text)
    poster_url = answer['poster']
    await message.answer_photo(photo=poster_url)
    for name, inline_keyboard in make_inline_keyboard(answer):
        await message.answer(f'🎙 {name}', reply_markup=inline_keyboard)


@dp.message_handler(lambda message: DbFunc().check_user(message),
                    text=['🎥 Показати новинки Топ-10'], state='*')
async def take_text(message: types.Message):
    answer_msg = FindMovies().find_newest()
    for text in answer_msg[:10]:
        inline_declar = types.InlineKeyboardMarkup()
        inline_declar.add(types.InlineKeyboardButton('🎬 Дивитися', callback_data=f"f_id@{text['id_film']}"))
        await message.answer_photo(text['poster'], f"<b>{text['name']}</b>", reply_markup=inline_declar)
        # await message.answer(text)


@dp.message_handler(lambda message: DbFunc().check_user(message),
                    text=['🔎 Пошук'], state='*')
async def search_state(message: types.Message):
    await message.answer("Введіть назву фільма", reply_markup=keyboard_inline_state)
    await NextStep.waiting_for_movies_name.set()


@dp.message_handler(lambda message: DbFunc().check_user(message),
                    state=NextStep.waiting_for_movies_name, content_types=types.ContentTypes.TEXT)
async def check_city(message: types.Message, state: FSMContext):
    search_text = message.text
    answer_msg = FindMovies().search_films(search_text)
    if answer_msg:
        await state.finish()
        for text in answer_msg[:10]:
            inline_declar = types.InlineKeyboardMarkup()
            inline_declar.add(types.InlineKeyboardButton('🎬 Дивитися', callback_data=f"f_id@{text['id_film']}"))
            await message.answer_photo(text['poster'], f"<b>{text['name']}</b>", reply_markup=inline_declar)
    else:
        await message.answer('Нічого не знайдено\nВведіть назву ще раз', reply_markup=keyboard_inline_state)


@dp.message_handler(lambda message: DbFunc().check_user(message),
                    content_types=['text'])
async def take_text(message: types.Message):
    if message.text.startswith('/'):
        await message.reply('Перевірьте чи правильно введена команда', reply_markup=markup)
    else:
        await message.reply('Нажаль я ще не все вмію', reply_markup=markup)


@dp.callback_query_handler(text_startswith=['f_id'])
async def take_callback(query: types.CallbackQuery):
    await bot.answer_callback_query(query.id, '🔭 Шукаю фільм')
    answer_data = query.data
    url_film = DbFunc().search_film_id(answer_data.split('@')[1])
    answer = FindMovies().find_movies(url=url_film)
    poster_url = answer['poster']
    await query.message.answer_photo(photo=poster_url)
    for name, inline_keyboard in make_inline_keyboard(answer):
        await query.message.answer(f'🎙 {name}', reply_markup=inline_keyboard)


@dp.callback_query_handler(text_startswith='state_cancel', state='*')
async def state_cancel(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await query.answer("Охрана отмєна 😎")
    await query.message.edit_text('Пошук скасовано')


@dp.errors_handler()
async def send_admin(update, error):
    """
    Take error in bot and send to admin and user
    """
    if not isinstance(error, TimeoutError):
        print(update, error)
        list_admin = [379210271]
        name_error = f'{error}'.replace('<', '').replace('>', '')
        message_to_admin = f"""Сталася помилка в боті:\n{name_error}\nПри запиті:\n{update}"""
        for user in list_admin:
            await bot.send_message(user, message_to_admin)
        await update.message.answer('Сталася загальна помилка')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
