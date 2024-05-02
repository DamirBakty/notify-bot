import time

import requests
from environs import Env


def send_telegram_message(text, token, chat_id):
    apiURL = f'https://api.telegram.org/bot{token}/sendMessage'
    req = requests.get(apiURL, params={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'})
    return req.status_code


def main():
    env = Env()
    env.read_env()

    AUTH_TOKEN = env.str('TOKEN')
    BOT_TOKEN = env.str('BOT_TOKEN')
    CHAT_ID = env.str('CHAT_ID')
    headers = {
        'Authorization': AUTH_TOKEN
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
            if response.status_code != 200:
                print(f"Error sending long polling request. Status code: {response.status_code}")
                continue

            long_polling_details = response.json()

            if long_polling_details.get('status') == 'timeout':
                timestamp = int(long_polling_details['timestamp_to_request'])
            else:
                timestamp = int(long_polling_details['last_attempt_timestamp'])

            new_attempts = long_polling_details.get('new_attempts')
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
                    message_send_status = send_telegram_message(
                        text=message,
                        token=BOT_TOKEN,
                        chat_id=CHAT_ID
                    )
                    if message_send_status != 200:
                        print(f"Error sending telegram message. Status code: {message_send_status}")

        except requests.exceptions.ConnectionError:
            print('Connection Error occurred')
            time.sleep(60)
        except requests.exceptions.ReadTimeout:
            print('Request Timed Out')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
