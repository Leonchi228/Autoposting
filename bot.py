import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from aiogram.utils import executor

# Configure logging
logging.basicConfig(level=logging.INFO)

API_TOKEN = 'YOUR_API_TOKEN'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

# Command handler for /start
@dispatcher.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Hello! I'm your bot ready to help!")

# Command handler for /help
@dispatcher.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.reply("Available commands: /start, /help")

if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)