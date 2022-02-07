# Bot for safe cheating

VK bot to check who is cheating from which site, for example, you can find out if someone from your class is writing the same essay as you.

## Deploy locally:

Clone the repository
```
git clone https://github.com/Ryize/schoolCheating.git
```

Install requirements
```
pip3 install -r requirements.txt
```

Add your bot token and group id here in main.py
```
TOKEN = os.getenv('TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
```

Run the bot
```
python3 main.py
```

> Technologies used in the project: Python3, vk-api, sqlite3, time.
