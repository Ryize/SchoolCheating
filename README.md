# schoolCheating

Бот ВКОНТАКТЕ для проверки, кто с какого сайта списывает. Например: вы можете узнать, пишет ли кто-то из вашего класса то же эссе, что и вы.

## Прежде всего:

Клонируйте репозиторий и перейдите в установленную папку:
```
git clone https://github.com/Ryize/schoolCheating.git
cd schoolCheating
```

Установите requirements:
```
pip3 install -r requirements.txt
```

Добавьте токен своего бота и идентификатор группы в main.py (если у вас их нет, создайте группу в ВК и возьмите данные оттуда):
```
TOKEN = os.getenv('TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
```

Запустите бота:
```
python3 main.py
```

> Технологии используемые в проекте: Python3, vk-api, sqlite3, time.
