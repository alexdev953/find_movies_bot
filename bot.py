import aiogram.utils.exceptions
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from find_movie_bot import FindMovies
from bot_utils import make_inline_keyboard, markup, keyboard_inline_state, NextStep
from db_func import DBFunc
import asyncio
import app_logger

from bot_init import dp, bot

logger = app_logger.get_logger('handler')


loop = asyncio.get_event_loop()





url_for_search = 'http://baskino.me/films/'


@dp.message_handler(lambda message: DBFunc().check_user(message),
                    commands=['start'])
async def take_start(message: types.Message):
    about_bot = await bot.get_me()
    await message.answer(
        f"Привіт, {message.from_user.first_name}!\nЯ - <b>{about_bot['first_name']}</b>", reply_markup=markup)


@dp.message_handler(lambda message: DBFunc().check_user(message) and message.from_user.id == 379210271,
                    commands=['count'])
async def dump(message: types.Message):
    answer_count = DBFunc().count_users()
    await message.answer(f'Реальних користувачів: {answer_count["count"]}')


@dp.message_handler(lambda message: DBFunc().check_user(message),
                    text_startswith=[url_for_search])
async def echo(message: types.Message):
    answer = FindMovies().find_movies(url=message.text)
    if answer:
        poster_url = answer['poster']
        await message.answer_photo(photo=poster_url)

        for name, inline_keyboard in make_inline_keyboard(answer):
            await message.answer(f'🎙 {name}', reply_markup=inline_keyboard)
    else:
        await message.answer('Фільм не знайдено')


@dp.message_handler(lambda message: DBFunc().check_user(message),
                    text=['🎥 Показати новинки Топ-15'], state='*')
async def take_text(message: types.Message):
    answer_msg = FindMovies().find_newest()
    if not answer_msg.get('error'):
        for text in answer_msg.get('movies')[:15]:
            inline_declar = types.InlineKeyboardMarkup()
            inline_declar.add(types.InlineKeyboardButton('🎬 Дивитися', callback_data=f"f_id@{text['id_film']}"))
            await message.answer_photo(text['poster'], f"<b>{text['name']}</b>", reply_markup=inline_declar)
            await asyncio.sleep(0.3)
    else:
        await message.answer(answer_msg.get('error'))


@dp.message_handler(lambda message: DBFunc().check_user(message),
                    text=['🎲 Випадковий фільм'], state='*')
async def take_text(message: types.Message):
    random_movie = await loop.run_in_executor(None, FindMovies().get_random_bs)
    try:
        answer = await loop.run_in_executor(None, FindMovies().find_movies, random_movie)
        poster_url = answer['poster']
        await message.answer_photo(photo=poster_url)
        for name, inline_keyboard in make_inline_keyboard(answer):
            try:
                await message.answer(f'🎙 {name}', reply_markup=inline_keyboard)
            except aiogram.utils.exceptions.BadRequest:
                continue
    except AttributeError:
        await message.answer('Спробуйте ще раз')


@dp.message_handler(lambda message: DBFunc().check_user(message),
                    text=['🔎 Пошук'], state='*')
async def search_state(message: types.Message, state: FSMContext):
    send_message = await message.answer("Введіть назву фільма\nРосійською або Англійською",
                                        reply_markup=keyboard_inline_state)
    await NextStep.waiting_for_movies_name.set()
    async with state.proxy() as data:
        data['message'] = {'chat_id': send_message.chat.id, 'message_id': send_message.message_id}


@dp.message_handler(lambda message: DBFunc().check_user(message),
                    state=NextStep.waiting_for_movies_name, content_types=types.ContentTypes.TEXT)
async def check_city(message: types.Message, state: FSMContext):
    message_info = await state.get_data()
    search_text = message.text
    answer_msg = FindMovies().search_films(search_text)
    if answer_msg:
        await bot.delete_message(message_info['message']['chat_id'], message_info['message']['message_id'])
        await state.finish()
        for text in answer_msg:
            inline_declar = types.InlineKeyboardMarkup()
            inline_declar.add(types.InlineKeyboardButton('🎬 Дивитися', callback_data=f"f_id@{text['id_film']}"))
            await message.answer_photo(text['poster'], f"<b>{text['name']}</b>", reply_markup=inline_declar)
            await asyncio.sleep(0.5)
    else:
        send_message = await message.answer('Нічого не знайдено\nВведіть назву ще раз',
                                            reply_markup=keyboard_inline_state)
        async with state.proxy() as data:
            data['message'] = {'chat_id': send_message.chat.id, 'message_id': send_message.message_id}


@dp.message_handler(lambda message: DBFunc().check_user(message),
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
    url_film = DBFunc().search_film_id(answer_data.split('@')[1])['url']
    answer = FindMovies().find_movies(url=url_film)
    if answer:
        poster_url = answer['poster']
        await query.message.answer_photo(photo=poster_url)
        for name, inline_keyboard in make_inline_keyboard(answer):
            try:
                await query.message.answer(f'🎙 {name}', reply_markup=inline_keyboard)
                await asyncio.sleep(0.3)
            except aiogram.utils.exceptions.BadRequest:
                continue
    else:
        await query.message.answer('Фільм не знайдено')


@dp.callback_query_handler(text_startswith='state_cancel', state='*')
async def state_cancel(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await query.answer("Охрана отмєна 😎")
    await query.message.edit_text('Пошук скасовано')


@dp.errors_handler()
async def send_admin(update: types.Update, error):
    """
    Take error in bot and send to admin and user
    """
    if not isinstance(error, TimeoutError):
        name_error = f'{error}'.replace('<', '').replace('>', '')
        message_to_admin = f"""Сталася помилка в боті:\n{name_error}\nПри запиті:\n{update}"""
        await bot.send_message(379210271, message_to_admin)
        if update.message:
            await update.message.answer('Сталася загальна помилка')
        elif update.callback_query:
            await update.callback_query.message.answer(f'Сталася загальна помилка: {error}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
