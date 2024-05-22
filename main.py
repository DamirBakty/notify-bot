import logging
import time

import requests
from environs import Env

logger = logging.getLogger(__name__)


def send_telegram_message(text, token, chat_id):
    api_url = f'https://api.telegram.org/bot{token}/sendMessage'
    req = requests.get(api_url, params={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})
    return req


def main():
    env = Env()
    env.read_env()

    auth_token = env.str('TOKEN')
    bot_token = env.str('BOT_TOKEN')
    chat_id = env.str('CHAT_ID')
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
                    message_send = send_telegram_message(
                        text=message,
                        token=bot_token,
                        chat_id=chat_id
                    )
                    message_send.raise_for_status()
                    telegram_message_sent_timestamp = time.time()
                    logger.debug(
                        f'Send Telegram message. Duration: '
                        f'{telegram_message_sent_timestamp - telegram_message_sending_timestamp}'
                    )

        except requests.exceptions.ConnectionError:
            logger.error('Connection Error occurred. Sleeping for 120 seconds...')
            time.sleep(120)
        except requests.exceptions.ReadTimeout:
            logger.error('Request Timed Out')
            continue
        except requests.exceptions.HTTPError as err:
            logger.error(f'HTTP error. Status: {err}')
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    main()
