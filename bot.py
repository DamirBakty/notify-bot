import asyncio
import logging

from environs import Env
from telegram import Bot
from telegram.ext import Updater


class BotHandler(logging.Handler):
    def __init__(self, updater, chat_id):
        self.updater = updater
        self.chat_id = chat_id
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.create_task(self.send_log_message(log_entry))

    async def send_log_message(self, log_entry):
        try:
            print(65)
            return await self.updater.bot.send_message(
                chat_id=self.chat_id,
                text=log_entry
            )
        except Exception as e:
            logging.error(e)
            return e


async def get_bot_logger(bot, chat_id):
    updater = Updater(bot=bot, update_queue=None)
    bot_handler = BotHandler(updater, chat_id)
    bot_handler.setLevel(logging.DEBUG)
    bot_handler.setFormatter(logging.Formatter('%(message)s'))

    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(bot_handler)

    return updater


async def get_bot_updater(bot):
    updater = Updater(bot=bot, update_queue=None)
    return updater


async def get_bot_handler(updater, chat_id):
    bot_handler = BotHandler(updater, chat_id)
    bot_handler.setLevel(logging.DEBUG)
    bot_handler.setFormatter(logging.Formatter('%(message)s'))
    return bot_handler


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
    await updater.initialize()
    bot_handler = BotHandler(updater, chat_id)
    bot_handler.setLevel(logging.INFO)
    bot_handler.setFormatter(logging.Formatter('%(message)s'))

    logger.addHandler(bot_handler)
    await updater.start_polling()
    message = 'Hello from your Telegram bot!'
    try:
        a = 1 / 0
    except ZeroDivisionError as e:
        logger.error(e)

    # logger.info("This is an info log message")
    await updater.stop()

asyncio.run(start_bot())
