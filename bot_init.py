import app_logger
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import bot_token

memory_storage = MemoryStorage()

aiogram_logger = app_logger.get_logger('aiogram')


# Initialize bot and dispatcher
bot = Bot(token=bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=memory_storage)

