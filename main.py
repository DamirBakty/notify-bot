import time

import requests
from environs import Env


def send_telegram_message(text, token, chat_id):
    apiURL = f'https://api.telegram.org/bot{token}/sendMessage'
    req = requests.get(apiURL, params={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})
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

    timestamp = None
    params = {}
    while True:
        try:
            if timestamp:
                params['timestamp'] = timestamp
            response = requests.get(
                long_polling_url,
                headers=headers,
                params=params,
                timeout=120
            )
            response.raise_for_status()

            review_details = response.json()

            if review_details.get('status') == 'timeout':
                timestamp = int(review_details['timestamp_to_request'])
            else:
                timestamp = int(review_details['last_attempt_timestamp'])

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
                    message_send = send_telegram_message(
                        text=message,
                        token=bot_token,
                        chat_id=chat_id
                    )
                    message_send.raise_for_status()

        except requests.exceptions.ConnectionError:
            print('Connection Error occurred')
            time.sleep(60)
        except requests.exceptions.ReadTimeout:
            print('Request Timed Out')
        except requests.exceptions.HTTPError as err:
            print(f'HTTP error. Status: {err}')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
