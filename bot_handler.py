import asyncio
import logging


class BotHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.create_task(self.bot.send_message(self.chat_id, log_entry))

    async def send_log_message(self, log_entry):
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=log_entry
            )
        except Exception as e:
            logging.error(e)
            return e


def get_bot_handler(bot, chat_id):
    bot_handler = BotHandler(bot, chat_id)
    bot_handler.setLevel(logging.ERROR)
    bot_handler.setFormatter(logging.Formatter('%(message)s'))
    return bot_handler
