import logging
import os
import requests
import sys
import telegram
import time

from dotenv import load_dotenv
from json import JSONDecodeError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('TOKEN_PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TOKEN_TELEGRAM')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    logging.info('Проверка доступность переменных окружения.')
    environment_variables = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for name in environment_variables:
        if name is None:
            logging.critical(f'Отсутствует переменная окружения! {name}')
            raise ValueError(f'Отсутствует переменная окружения! {name}')
        else:
            logging.info('Все переменные окружения доступны!')
            return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    logging.debug('Отправка сообщения в Telegram')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено.')
        return True
    except telegram.error.TelegramError as error:
        logging.error(f'Не удалось отправить сообщение. {error}')
        return False


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту."""
    payload = {'from_date': timestamp}
    logging.info('Начало запроса.')
    try:
        homework = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.exceptions.RequestException as error:
        raise ConnectionError(f'Ошибка подключения к эндпоинту. {error}')
    if homework.status_code != 200:
        raise RuntimeError('Получен неожиданный статус API.')
    try:
        homework_json = homework.json()
        return homework_json
    except JSONDecodeError:
        logging.error('Не удалось преобразовать в json.')
        raise ValueError('Не удалось преобразовать в json.')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logging.debug('Начало проверки ответа API.')
    if not isinstance(response, dict):
        raise TypeError('Ответ API не соответствует требованиям')
    if 'homeworks' not in response:
        raise ValueError('В ответе нет значения "homeworks"')
    if 'current_date' not in response:
        raise ValueError('В ответе нет значения "current_date"')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Данный тип данных не является списком')
    logging.debug('Проверка ответа API закончена.')
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной работе статус этой работы."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise KeyError('Не найден такой ключ')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError('Полученный неожиданный статус домашней работы')
    return (f'Изменился статус проверки работы "{homework_name}"'
            f'{HOMEWORK_VERDICTS[homework_status]}')


def main():
    """Основная логика работы бота."""
    logging.info('Вы запустили Бота')
    timestamp = int(time.time())

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    previous_message = ''

    if check_tokens() is True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks and send_message(bot, parse_status(homeworks[0])):
                timestamp = response.get('current_date', timestamp)
        except Exception as error:
            message = f'Сбой в работе программы. {error}'
            logging.exception(message)
            if previous_message != message and send_message(bot, message):
                previous_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.INFO,
        filename='program.log',
        format='%(asctime)s, %(levelname)s, %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    main()
