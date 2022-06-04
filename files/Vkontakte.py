import configparser
import requests
from datetime import datetime
from PIL import Image
import sys


class VkPhotos:

    def __init__(self):
        self.path = 'settings.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.path)
        self.token = self.config.get("Tokens", "vk_token")

    def _get_user_id(self):
        flag = True
        while flag:
            name = input('Введите id или вот эти буквы вместо него: ')
            URL = 'https://api.vk.com/method/users.get'
            params = {
                'user_ids': name,
                'access_token': self.token,
                'v': '5.131'
            }
            res = requests.get(URL, params=params)
            if res.status_code != 200:
                sys.exit('Что-то пошло не так, давай сначала.')
            if not bool(res.json()['response']):
                print('Пользователь не существует')
                flag = not bool(res.json()['response'])
            else:
                if 'can_access_closed' in res.json()['response'][0].keys() and not res.json()['response'][0]['can_access_closed']:
                    print('Профиль закрыт')
                elif 'deactivated' in res.json()['response'][0].keys():
                    print('Профиль неактивен')
                else:
                    flag = False
        user_id = res.json()['response'][0]['id']
        return user_id

    def get_size(self, url):
        foto_url = url
        raw = requests.get(foto_url, stream=True).raw
        size = Image.open(raw).size
        return size

    def get_maxsize_photo(self):
        URL = 'https://api.vk.com/method/photos.get'
        user_id = self._get_user_id()
        params = {
            'user_ids': user_id,
            'access_token': self.token,
            'v':'5.131',
            'owner_id': user_id,
            'album_id': 'profile',
            'extended' : '1',
            'count': '999',
        }
        res = requests.get(URL, params=params)
        photo_dict = {}
        f_photo_dict = {}
        photo_list = []
        like = 0
        result = res.json()['response']['items']
        for photos in result:
            like = photos['likes']['count']
            date = datetime.fromtimestamp(photos['date']).strftime("%B_%d_%Y_%H-%M-%S")
            for photo in photos['sizes']:
                photo['likes'] = like
                photo['date'] = date
                if photo['height'] != 0:
                    photo['size'] = photo['height'] + photo['width']
                else:
                    photo['size'] = sum(self.get_size(photo['url']))
                f_photo = {key: photo[key] for key in photo if key not in ['height', 'width']}
                photo_dict = {**photo_dict, **f_photo}
            photo_list.append([*photo_dict.values()])
            photo_list.sort(key=lambda i: i[4], reverse=True)
        return photo_list


