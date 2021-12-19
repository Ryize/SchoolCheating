from pprint import pprint

import vk_api
import sqlite3
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class DbWorker:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Class(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT NOT NULL,
                            conversation_id INTEGER NOT NULL,
                            fio TEXT NOT NULL
                            )
                        """)
        self.cur.execute("""CREATE TABLE IF NOT EXISTS UserCheating(
                    id AUTO_INCREMENT,
                    user_id INTEGER NOT NULL,
                    class_id INTEGER NOT NULL,
                    site_url TEXT NOT NULL,
                    time_left INTEGER NOT NULL,
                    FOREIGN KEY (class_id) REFERENCES Class(id)
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


def new_class(event): # Create new class(Max 1 class for 1 user)
    if db_worker.execute_query('SELECT conversation_id FROM Class WHERE conversation_id=' + str(event.object.from_id)):
        for i in db_worker.execute_query(
                'SELECT conversation_id FROM Class WHERE conversation_id=' + str(event.object.from_id)):
            if i[0] == event.object.from_id:
                vk_api.messages.send(peer_id=event.object.peer_id,
                                     message=f"У вас уже есть класс!",
                                     random_id=get_random_id(),
                                     )
                return
    data = vk_api.messages.getConversationMembers(peer_id=event.object.peer_id)
    conversation_id = event.object.from_id
    user_data = []
    pprint(data)
    for i in range(data['count']):
        try:
            user_data.append([int(data['profiles'][i]['id']),
                              data['profiles'][i]['first_name'] + ' ' + data['profiles'][i]['last_name']])
        except:
            pass
    user_id = ''
    fio = ''
    for i in user_data:
        user_id += f'{i[0]}, '
        fio += f'{i[1]}, '
    a = f"INSERT INTO Class (id, user_id, conversation_id, fio) VALUES(NULL, '{user_id}', {conversation_id}, '{fio}')"
    db_worker.execute_query(a)

    vk_api.messages.send(peer_id=event.object.peer_id,
                         message=f"Ты в новом классе!\n",
                         random_id=get_random_id(),
                         )


for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.object.text == '/новыйкласс':
            new_class(event)


        elif event.object.text == '/пишу':

            vk_api.messages.send(peer_id=event.object.peer_id,
                                 message='Ты в пишу!',
                                 random_id=get_random_id(),
                                 )

        elif event.object.text in ('/проверить', '/check'):
            vk_api.messages.send(peer_id=event.object.peer_id,
                                 message='Ты в чеке!',
                                 random_id=get_random_id(), )

# import time
# from pprint import pprint
#
# import requests
# from bs4 import BeautifulSoup
#
#
# URL = f"https://www.avito.ru/volgograd?q={input('Введите запрос: ')}"
# html_code = requests.get(URL).text
#
# HOST = URL.replace(':/', '').split('/')[1].replace('www.', '')
#
# # Title title-root-j7cja iva-item-title-_qCwt title-listRedesign-XHq38 title-root_maxHeight-SXHes text-text-LurtD text-size-s-BxGpL text-bold-SinUO
# # Price price-text-E1Y7h text-text-LurtD text-size-s-BxGpL
# # Url link-link-MbQDP link-design-default-_nSbv title-root-j7cja iva-item-title-_qCwt title-listRedesign-XHq38 title-root_maxHeight-SXHes
#
# # Card iva-item-root-Nj_hb photo-slider-slider-_PvpN iva-item-list-H_dpX iva-item-redesign-nV4C4 iva-item-responsive-gIKjW iva-item-ratingsRedesign-kK656 items-item-My3ih items-listItem-Gd1jN js-catalog-item-enum
#
# def get_all_pages(soup):
#     #pagination-root-Ntd_O
#     items = soup.find_all('span', class_='pagination-item-JJq_j')
#     page_max = []
#     for item in items:
#         if item.get_text().isdigit():
#             page_max.append(item.get_text())
#     return int(max(page_max))
#
# soup = BeautifulSoup(html_code, 'html.parser')
# for i in range(1, get_all_pages(soup)+1):
#
#     html_code = requests.get(URL+f'&p={i}').text
#     soup = BeautifulSoup(html_code, 'html.parser')
#     items = soup.find_all('div', class_='iva-item-root-Nj_hb photo-slider-slider-_PvpN iva-item-list-H_dpX iva-item-redesign-nV4C4 iva-item-responsive-gIKjW iva-item-ratingsRedesign-kK656 items-item-My3ih items-listItem-Gd1jN js-catalog-item-enum')
#
#     card = []
#     for item in items:
#         card.append({
#             'title': item.find('h3', class_='title-root-j7cja iva-item-title-_qCwt title-listRedesign-XHq38 title-root_maxHeight-SXHes text-text-LurtD text-size-s-BxGpL text-bold-SinUO').get_text(),
#             'price': f"{item.find('span', class_='price-text-E1Y7h text-text-LurtD text-size-s-BxGpL').get_text().encode('ascii', 'ignore')}р",
#             'url': HOST+item.find('a', class_='link-link-MbQDP link-design-default-_nSbv title-root-j7cja iva-item-title-_qCwt title-listRedesign-XHq38 title-root_maxHeight-SXHes').get('href'),
#         })
#
#     time.sleep(3)
#
#     pprint(card)
#
