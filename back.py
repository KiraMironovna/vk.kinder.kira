import vk_api
from datetime import date

from settings import acces_token

class VkWorker:
    def __init__(self, a_token):
        self.api = vk_api.VkApi(token=a_token)
        self.counter = 0
        
    def get_profile(self, id):
        """Получаем данные по id"""
        profile_info = {'id': id, 'name': None, 'city': None, 'age': 0}
        if info := self.api.method('users.get', {'user_ids': id,
                                   'fields': ('bdate, city, sex, relation'),}):
            info = info[0]
            profile_info['name'] = f'{info.get("last_name")} {info.get("first_name")}'
            if info.get('city'): 
                profile_info['city'] = info.get('city').get('title')
            if info.get('bdate'):
                profile_info['age'] = (date.today().year - 
                                       int(info.get('bdate').split('.')[-1]))
            profile_info['sex'] = info.get('sex', 1)
            profile_info['relation'] = info.get('relation', 0)
        return profile_info
    
    def get_photos(self, id):
        """Получаем популярные фото по id"""
        photos = self.api.method('photos.get', {'owner_id': id,
                                                'album_id': 'profile',
                                                'extended': 1}) 
        if photos := photos.get('items'):
            photos = [(elem['id'], elem['likes']['count'] + elem['comments']['count']) for elem in photos]
            photos.sort(key=lambda x: x[1], reverse=True)
        return photos[:3]
    
    def get_search(self, data):
        """Ищем профили по вводным данным"""
        values = {'count': 25, 
                  'offset': self.counter,
                  'age_from': data['age'] - 3,
                  'age_to': data['age'] + 3,
                  'sex': 1 if data['sex'] == 2 else 2,
                  'hometown': data['city'], 
                  'has_photo': 1,
                  'status': data['relation'], 
                  'is_closed': False,}
        self.counter += values['count']
        users = self.api.method('users.search', values=values)
        if users.get('items'):
            open_users = []
            for user in users.get('items'):
                if user['is_closed'] == 0:
                    name = user.get('last_name', '') + ' ' + user.get('first_name', '')
                    open_users.append({'user_id': user['id'], 'user_name': name})
            return open_users


if __name__ == '__main__':
    worker = VkWorker(acces_token)
    print(worker.get_profile(456798))
    print(worker.get_photos(129224))
    print(worker.get_search({'id': 456798, 'name': 'Иванова Александра', 'city': 'Краснодар', 'age': 22, 'sex': 1, 'relation': 0}))
