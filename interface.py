import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import *
import core
import data_store
import datetime
import psycopg2

conn = psycopg2.connect(host=host, user=user, password=password, database=db_name)

current_year = datetime.datetime.now().year

class BotInterface:

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VKTools(acces_token) 
        self.params = None

    def message_send(self, user_id, message=None, attachment=None): # отправка сообщений
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id(),
                              }
                              )

    def event_handler(self):  # обработка событий, получение сообщений
        offset = 0
        longpull = VkLongPoll(self.interface)
        for event in longpull.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                data_store.create_table(conn)
#                 user_info = core.tools.get_profile_info(event.user_id)
#                 city_id = user_info[0].get('city').get('id')
#                 birthday = user_info[0].get('bdate')
#                 f_name = user_info[0].get('first_name')
#                 birth_year = birthday.split('.')[2]
#                 age_from = current_year - int(birth_year) - 5
#                 age_to = current_year - int(birth_year)
#                 sex = user_info[0].get('sex')
#                 sex = 1 if sex == 2 else 2

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Привет, {self.params["first_name"]}, чтобы начать поиск отправьте букву "П" или "С" для перехода к следующему найденному человеку')
                elif command == 'п' or command == 'с':
#                     if sex == None:
#                         sex = int(input('Отправьте:'
#                                         ' 1 - если Вы женщина, 2 - если Вы мужчина'))
                    while command != 'пока':

                        users = core.tools.user_serch(city_id, age_from, age_to, sex, 1, offset)
                        user = users.pop()
                        offset += 1
                        id_found = user.get('id')
                        name_found = user.get('name')

                        # логика для проверки в бд
                        id_list = data_store.from_db(conn, event.user_id)
                        list_id = []
                        for x in id_list:
                            list_id.append(x[0])


                        if id_found in list_id:
                            continue
                        else:
                            self.message_send(event.user_id,
                                              f'{self.params["first_name"]}, встречайте: {self.params["name_found"], {"https://vk.com/id" + str(self.params["id_found"]}')
                            result_photos_get = core.tools.photos_get(id_found)
                            for photo in result_photos_get:
                                photo_id = photo.get('id')
                                owner_id = photo.get('owner_id')
                                media = 'photo' + str(owner_id) + '_' + str(photo_id)
                                self.message_send(event.user_id, attachment=media)
                            data_store.to_db(conn, event.user_id, id_found)
                            self.message_send(event.user_id, 'Отправьте "С", для перехода к следующей анкете')
                            break


                elif command == 'пока':
                    self.message_send(event.user_id, f'До новых встреч, {self.params["name"]}')

                else:
                    self.message_send(event.user_id, 'Неизвестная команда.  введите "П" для поиска", или "пока" для выхода)')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
