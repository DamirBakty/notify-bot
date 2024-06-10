import asyncio
import logging
import time

import requests
from environs import Env
from telegram import Bot

from bot_handler import get_bot_handler

logger = logging.getLogger(__file__)


async def start_polling(bot, chat_id, auth_token):


    headers = {
        'Authorization': auth_token
    }

    long_polling_url = 'https://dvmn.org/api/long_polling/'

    start_time = time.time()
    timestamp = None

    params = {}

    while True:
        try:
            if timestamp:
                params['timestamp'] = timestamp
                logger.debug(f'Started polling with timestamp: {timestamp}')
            else:
                logger.debug(f'Started polling without timestamp')
            response = requests.get(
                long_polling_url,
                headers=headers,
                params=params,
                timeout=120
            )
            response.raise_for_status()
            logger.debug(f"Polling time = {start_time - time.time()}")

            review_details = response.json()
            timestamp = (review_details.get('last_attempt_timestamp')
                         or review_details.get('timestamp_to_request'))

            new_attempts = review_details.get('new_attempts')
            if new_attempts:
                for attempt in new_attempts:
                    lesson_title = attempt.get('lesson_title')
                    lesson_url = attempt.get('lesson_url')
                    is_negative = attempt.get('is_negative')

                    message = f'У вас проверили работу «{lesson_title}»\n\n'
                    if is_negative:
                        status = 'К сожалению в работе нашлись ошибки\n\n'
                    else:
                        status = 'Преподателю всё понравилось, можно приступать к следущему уроку!\n\n'

                    lesson_url_message = f'Ссылка на урок: {lesson_url}'
                    message += status
                    message += lesson_url_message
                    telegram_message_sending_timestamp = time.time()
                    try:
                        await bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode='Markdown',
                        )
                        await asyncio.sleep(1)

                    except Exception as e:
                        logger.debug(e)
                        await asyncio.sleep(1)

                    telegram_message_sent_timestamp = time.time()
                    logger.debug(
                        f'Send Telegram message. Duration: '
                        f'{telegram_message_sent_timestamp - telegram_message_sending_timestamp}'
                    )

        except requests.exceptions.ConnectionError:
            logger.exception('Connection Error occurred. Sleeping for 120 seconds...')
            await asyncio.sleep(120)
        except requests.exceptions.ReadTimeout:
            logger.exception('Request Timed Out')
            await asyncio.sleep(1)
            continue
        except requests.exceptions.HTTPError as err:
            logger.exception(f'HTTP error. Status: {err}')
            await asyncio.sleep(1)
        except Exception as e:
            logger.exception(e)
            await asyncio.sleep(1)


def main():
    env = Env()
    env.read_env()
    auth_token = env.str('DEVMAN_TOKEN')
    bot_token = env.str('BOT_TOKEN')
    chat_id = env.str('CHAT_ID')

    bot = Bot(token=bot_token)

    bot_handler = get_bot_handler(bot, chat_id)
    logger.addHandler(bot_handler)

    loop = asyncio.get_event_loop()
    loop.create_task(start_polling(bot, chat_id, auth_token))
    loop.run_forever()


if __name__ == '__main__':
    main()
