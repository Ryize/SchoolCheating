import time
import vk_api
import sqlite3
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
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
    user_id_hide = event.object.from_id
    if list(db_worker.execute_query(f'SELECT * FROM HideUserProfile WHERE user_id = {event.object.from_id}')):
        user_id_hide = -event.object.from_id
    sql_query = f"""INSERT INTO UserCheating(user_id, site_url, time_left) 
                VALUES('{user_id_hide}', '{url}', {time_left})"""
    db_worker.execute_query(sql_query)
    vk_api.messages.send(peer_id=event.object.peer_id,
                         message=f'✅Вы успешно пишите с сайта: {url}',
                         random_id=get_random_id(), )


@check_validity_url
def command_check_url(event, url):
    sql_query = f"SELECT user_id, time_left FROM UserCheating WHERE site_url = '{url}';"
    query_res = list(db_worker.execute_query(sql_query))

    # We check if more than a day has passed since the start of the write-off, if not, then add to the list
    if not len([i for i in query_res if i[1] - time.time() > 0]):
        vk_api.messages.send(peer_id=event.object.peer_id,
                             message=f'С этого сайта никто не списывает, путь свободен! 😉',
                             random_id=get_random_id(), )
        return

    profile_users = []
    for i in query_res:
        if i[1] - time.time() < 0:
            continue

        city = vk_api.users.get(user_id=abs(i[0]), fields="home_town")[0]["home_town"]
        school = vk_api.users.get(user_id=abs(i[0]), fields="schools, city")[0]["schools"][0]["name"]

        if i[0] != abs(i[0]):
            profile_users.append(f'* Профиль скрыт ({city}, {school})'.replace('\n', ''))
            continue
        profile_users.append(f'- https://vk.com/id{i[0]} ({city}, {school})'.replace('\n', ''))

    line_break = '\n'

    user_word = ' пользователей пишут с этого сайта, их профили:'
    if len(profile_users) == 1:
        user_word = ' пользователь пишет с этого сайта, его профиль:'
    elif len(profile_users) < 4:
        user_word = '`е пользователей пишут с этого сайта, их профили:'

    message = f"""{len(profile_users)}{user_word} \n{f'{line_break}'.join(profile_users)}"""
    vk_api.messages.send(peer_id=event.object.peer_id,
                         message=message,
                         random_id=get_random_id(), )


def command_start(event):
    keyboard = VkKeyboard()
    keyboard.add_button('СкрытьПрофиль', VkKeyboardColor.NEGATIVE)
    keyboard.add_button('ПоказывайПрофиль', VkKeyboardColor.POSITIVE)
    vk_api.messages.send(peer_id=event.object.peer_id,
                         message="""Приветствую в боте для безопасного списывания!
                         
                         Список комманд:
                         1)/пишу ссылка на сайт(Указать что вы пишите с этого сайта, /пишу https://google.com/gdz.ru)
                         2)/проверить ссылка на сайт(Проверить пишет ли кто-то сейчас с этого сайта, /проверить https://google.com/gdz.ru)
                         3)/спрячь (Убрать ссылку на профиль из списка при проверке сайта)
                         4)/покажи (Показывать ссылку на профиль в списке при проверке сайта)
                         
                         Это все команды, желаем хороших оценок! 😀
                         """,
                         random_id=get_random_id(),
                         keyboard=keyboard.get_keyboard())


def control_called_commands(event):  # Calling a specific function for a command
    if event.object.text.lower() == 'начать':
        command_start(event)

    elif event.object.text.split(' ')[0].lower() == '/пишу':
        url = event.object.text.split(' ')[1:]
        command_writen(event, url[0])

    elif event.object.text.split(' ')[0].lower() == '/проверить':
        url = event.object.text.split(' ')[1:]
        command_check_url(event, url[0])

    elif event.object.text.split(' ')[0].lower() in ['/спрячь', 'спрячь', 'скрытьпрофиль']:
        sql_query_select = f"""SELECT * FROM HideUserProfile WHERE user_id = {event.object.from_id}"""
        if not list(db_worker.execute_query(sql_query_select)):
            sql_query_insert = f"""INSERT INTO HideUserProfile (user_id) VALUES({event.object.from_id})"""
            db_worker.execute_query(sql_query_insert)
            keyboard = VkKeyboard()
            keyboard.add_button('СкрытьПрофиль', VkKeyboardColor.POSITIVE)
            keyboard.add_button('ПоказывайПрофиль', VkKeyboardColor.NEGATIVE)
            vk_api.messages.send(peer_id=event.object.peer_id,
                                 message='Ссылка на ваш профиль больше не будет отображаться! 👀',
                                 random_id=get_random_id(),
                                 keyboard=keyboard.get_keyboard()
                                 )

    elif event.object.text.split(' ')[0].lower() in ['/покажи', 'покажи', 'показывай', 'показывайпрофиль']:
        sql_query = f"""SELECT * FROM HideUserProfile WHERE user_id = {event.object.from_id}"""
        if list(db_worker.execute_query(sql_query)):
            sql_query1 = f"""DELETE FROM HideUserProfile WHERE user_id = {event.object.from_id}"""
            db_worker.execute_query(sql_query1)
            keyboard = VkKeyboard()
            keyboard.add_button('СкрытьПрофиль', VkKeyboardColor.NEGATIVE)
            keyboard.add_button('ПоказывайПрофиль', VkKeyboardColor.POSITIVE)
            vk_api.messages.send(peer_id=event.object.peer_id,
                                 message='Ссылка на ваш профиль снова отображается! 😙',
                                 random_id=get_random_id(),
                                 keyboard=keyboard.get_keyboard())


def main():
    print('✅ Бот успешно запущен!')
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                control_called_commands(event)
            except NotValidityURL:
                vk_api.messages.send(peer_id=event.object.peer_id,
                                     message='❌Не верный URL!\nСсылка указывается с http://',
                                     random_id=get_random_id(), )


if __name__ == '__main__':
    main()