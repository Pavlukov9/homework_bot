# Telegram Bot

Проект разработан во время учёбы на Яндекс.Практикум. Cоздан Телеграм Бот через "BotFather" в Telegram, который оповещает пользователя о статусе его "Домашнего задания".

Статусы:

1. <<Работа взята на проверку ревьюером.>> - задание отправлено на GitHub;

2. <<Работа проверена: у ревьюера есть замечания.>> - задание проверено и отправлено на доработку;

3. <<Работа проверена: ревьюеру всё понравилось. Ура!>> - задание проверено и принято.

## Технологии
- Python;
- Библиотеки: dotenv, python-telegram-bot;

## Установка
1. Склонировать репозиторий
```
git clone https://github.com/Pavlukov9/homework_bot.git
```

2. Создать и активировать виртуальное окружение
```
python -m venv venv
```
```
source venv/Scripts/activate
```

3. Установить зависимости для Python
```
pip install -r requirements.txt
```

4. Выполнить миграции
```
python manage.py migrate
```

5. Запустить проект
```
python manage.py runserver
```

## Автор
- Павлюков Даниил Сергеевич