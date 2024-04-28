import requests
from environs import Env

env = Env()
env.read_env()

AUTH_TOKEN = env.str('TOKEN')
BOT_TOKEN = env.str('BOT_TOKEN')
CHAT_ID = env.str('CHAT_ID')


def send_telegram_message(text, token=BOT_TOKEN):
    apiURL = f'https://api.telegram.org/bot{token}/sendMessage'
    req = requests.get(apiURL, params={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'})
    print(req.status_code)
    return req.status_code


headers = {
    'Authorization': AUTH_TOKEN
}

# review_url = 'https://dvmn.org/api/user_reviews/'
long_polling_url = 'https://dvmn.org/api/long_polling/'

timestamp = None

while True:
    try:
        if timestamp:
            long_polling_url += f'?timestamp={timestamp}'
        response = requests.get(
            long_polling_url,
            headers=headers,
        )
        data = response.json()
        print(data)
        timestamp = int(response.json()['last_attempt_timestamp'])
        new_attempts = data.get('new_attempts')
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
                send_telegram_message(text=message)

    except requests.exceptions.ConnectionError:
        print('Connection Error occurred')
    except requests.exceptions.ReadTimeout:
        print('Request Timed Out')
    except Exception as e:
        print(e)
