import time
import vk_api
import sqlite3
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
from vk_api.utils import get_random_id

from exception import *
from project_decorator import check_validity_url


class DbWorker:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS UserCheating(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            site_url TEXT NOT NULL,
                            time_left INTEGER NOT NULL
                            )
                        """)
        self.cur.execute("""CREATE TABLE IF NOT EXISTS HideUserProfile(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL
                            )
                        """)
        self.con.commit()

    def execute_query(self, text_query: str):
        res = self.cur.execute(text_query)
        self.con.commit()
        return res


vk_session = vk_api.VkApi(token='83908bd5550b90513c8834c2f1fd2d043b21ed8d8f309f267d483642896f6a1e70856dcdafdd1fc3c4395')
longpoll = VkBotLongPoll(vk_session, group_id=209501325)

vk_api = vk_session.get_api()

db_worker = DbWorker()


@check_validity_url
def command_writen(event, url):
    time_left = int(time.time() + 60 * 60 * 24)
    sql_query = f"""INSERT INTO UserCheating(user_id, site_url, time_left) 
                VALUES('{event.object.from_id}', '{url}', {time_left})"""
    db_worker.execute_query(sql_query)
    vk_api.messages.send(peer_id=event.object.peer_id,
                         message=f'✅Вы успешно пишите с сайта: {url}',
                         random_id=get_random_id(), )


@check_validity_url
def command_check_url(event, url):
    sql_query = f"SELECT * FROM UserCheating WHERE site_url = '{url}';"
    # We check if more than a day has passed since the start of the write-off, if not, then add to the list
    if not len([i for i in db_worker.execute_query(sql_query) if i[3] - time.time() > 0]):
        vk_api.messages.send(peer_id=event.object.peer_id,
                             message=f'С этого сайта никто не списывает, путь свободен! 😉',
                             random_id=get_random_id(), )
        return

    profile_users = list(
        [
            f'''
        https://vk.com/id{i[1]} ({vk_api.users.get(user_id=(i[1]), fields="home_town")[0]["home_town"]}, 
        {vk_api.users.get(user_id=i[1], fields="schools, city")[0]["schools"][0]["name"]})
    '''.replace('\n', '')
            for i in db_worker.execute_query(sql_query) if i[3] - time.time() > 0])

    line_break = '\n'

    user_word = ' пользователей пишут с этого сайта, их профили:'
    if len(profile_users) == 1:
        user_word = ' пользователь пишет с этого сайта, его профиль:'
    elif 1 < len(profile_users) < 4:
        user_word = '`е пользователей пишут с этого сайта, их профили:'

    message = f"""{len(profile_users)}{user_word} \n{f'{line_break}'.join(profile_users)}"""
    vk_api.messages.send(peer_id=event.object.peer_id,
                         message=message,
                         random_id=get_random_id(), )


def control_called_commands(event):  # Calling a specific function for a command
    if event.object.text.split(' ')[0] == '/пишу':
        url = event.object.text.split(' ')[1:]
        command_writen(event, url[0])

    elif event.object.text.split(' ')[0] == '/проверить':
        url = event.object.text.split(' ')[1:]
        command_check_url(event, url[0])

    elif event.object.text.split(' ')[0] == '/спрячь':
        sql_query = f"""SELECT * FROM HideUserProfile WHERE user_id = {event.object.from_id}"""
        if not list(db_worker.execute_query(sql_query)):
            sql_query1 = f"""INSERT INTO HideUserProfile (user_id) VALUES({event.object.from_id})"""
            db_worker.execute_query(sql_query1)
        print(list(db_worker.execute_query(sql_query)))


def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                control_called_commands(event)
            except NotValidityURL:
                vk_api.messages.send(peer_id=event.object.peer_id,
                                     message='❌Не верный URL!',
                                     random_id=get_random_id(), )


if __name__ == '__main__':
    main()
