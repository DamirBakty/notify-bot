import asyncio
import logging

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
            return await self.updater.bot.send_message(
                chat_id=self.chat_id,
                text=log_entry
            )
        except Exception as e:
            logging.error(e)
            return e


async def get_bot_updater(bot):
    updater = Updater(bot=bot, update_queue=None)
    return updater


async def get_bot_handler(updater, chat_id):
    bot_handler = BotHandler(updater, chat_id)
    bot_handler.setLevel(logging.ERROR)
    bot_handler.setFormatter(logging.Formatter('%(message)s'))
    return bot_handler
