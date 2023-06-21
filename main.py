import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from settings import acces_token, group_token
from database import DbWorker
from back import VkWorker


class BotWorker:
    def __init__(self):
        self.bot = vk_api.VkApi(token=group_token)  # Авторизация под группой
        self.api = VkWorker(acces_token)  # Авторизация под собой
        self.data = DbWorker()  # запуск базы данных
        self.worksheets = []
        self.params = {}
        self.flag = None

    def write_msg(self, user_id, message, attachment):
        """Ответ на сообщения пользователя"""
        self.bot.method('messages.send', {'user_id': user_id, 'message': message,
                                          'attachment': attachment,
                                          'random_id': get_random_id()})

    def see_profile(self):
        """заполняем воркшит, проверяем анкеты"""
        while True:
            if self.worksheets:
                sheet = self.worksheets.pop()
                if self.data.wiev(self.params['id'], sheet['user_id']):
                    continue
                self.data.add_partner(self.params['id'], sheet['user_id'])
                return sheet
            self.worksheets = self.api.get_search(self.params)
            if self.worksheets is None:
                return

    def tracking(self):
        """Отслеживаем события"""
        long = VkLongPoll(self.bot)
        for event in long.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                msg = event.text.lower()
                attach = None
                if not self.flag and msg:
                    self.flag = 'online'
                    self.params = self.api.get_profile(event.user_id)
                    ans = (f'Привет, {self.params["name"]}\n'
                           f'могу помочь с поиском анкет подходящих для тебя\n'
                           f'прошу вводить только простые команды\n Готовы?')

                elif msg in ('нет', 'пока', 'q'):
                    ans = (f'{self.params["name"]}, если будет интересно - продолжим\n'
                           f'Всего хорошего!')
                    self.worksheets = []
                    self.params = {}
                    self.flag = None

                elif self.flag == 'online':
                    if self.params['age'] == 0:
                        self.flag = 'set_age'
                        ans = 'необходимо установить возраст поиска'

                    if self.params['city'] is None:
                        self.flag = 'set_city'
                        ans = 'необходимо указать город для поиска'

                    else:
                        ans = (f'Начинаем поиск, вводные данные для поиска:\n'
                               f'Возраст {self.params["age"]}\n'
                               f'Город {self.params["city"]}\n'
                               f'Для следующей анкеты вводите "f" либо "д"\n'
                               f'"q" либо "пока" для завершения')
                        self.flag = 'search'

                elif self.flag == 'search':
                    ans = "Начинаем"
                    if msg in ('f', 'д'):
                        if profile := self.see_profile():
                            ans = f'{profile["user_name"]}  vk.com/id{profile["user_id"]}'
                            attach = ''
                            photos = self.api.get_photos(profile['user_id'])
                            for photo in photos:
                                attach += f'photo{profile["user_id"]}_{photo[0]},'
                        else:
                            ans = 'Анкет не найдено :('

                elif self.flag == 'set_age':
                    if msg.isdigit():
                        self.flag = 'online'
                        self.params['age'] = int(msg)
                        ans = f'Возраст изменён на {self.params["age"]}'
                    else:
                        ans = f'Возраст не распознан, пожалуйста введите число'

                elif self.flag == 'set_city':
                    if msg.isdigit() == False:
                        self.flag = 'online'
                        self.params['city'] = msg.capitalize()
                        ans = f'Город изменён на {self.params["city"]}'
                    else:
                        ans = f'Город не распознан, пожалуйста повторите ввод'

                else:
                    ans = 'Я не понимаю вашей команды'

                self.write_msg(event.user_id, ans, attachment=attach)


if __name__ == '__main__':
    my_bot = BotWorker()
    my_bot.tracking()
