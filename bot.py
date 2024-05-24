import asyncio
import logging

from environs import Env
from telegram import Bot
from telegram.ext import Updater


class BotHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.create_task(self.send_log_message(log_entry))

    async def send_log_message(self, log_entry):
        try:
            await self.bot.send_message(chat_id=self.chat_id, text='log_entry')
        except Exception as e:
            print(f'Error sending Telegram message: {e}')


async def start_bot():
    env = Env()
    env.read_env()
    logger = logging.getLogger()

    auth_token = env.str('TOKEN')
    bot_token = env.str('BOT_TOKEN')
    chat_id = env.str('CHAT_ID')

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    bot = Bot(token=bot_token)

    updater = Updater(bot=bot, update_queue=None)
    bot_handler = BotHandler(bot, chat_id)
    bot_handler.setLevel(logging.INFO)
    bot_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logger.addHandler(bot_handler)

    await updater.initialize()

    message = 'Hello from your Telegram bot!'

    # a = 1 / 0

    # await bot.send_message(chat_id=chat_id, text=message)
    logger.info("This is an info log message")
    logger.warning("This is a warning log message")
    logger.error("This is an error log message")



asyncio.run(start_bot())
