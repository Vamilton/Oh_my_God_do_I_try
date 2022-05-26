import requests
import os
import time
from pprint import pprint

with open('vk_token.txt', 'r') as file_object:
    vk_token = file_object.read().strip()

with open('ya_token.txt', 'r') as file_object:
    ya_token = file_object.read().strip()

class YaUploader:
    def __init__(self, token):
        self.ya_token = ya_token
        self.header = {
            'Content-Type': 'application/json',

            'Authorization': f'OAuth {ya_token}'
        }

    def ya_upload(self, disk_file_path, photo_url):
        param = {'url': photo_url, 'overwrite': 'true', 'path': disk_file_path}
        response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload?', headers=self.header, params=param)
        # if response.status_code == 202:
        #     print('ВЖУХ')


class VkPhotos(YaUploader):

    def __init__(self, name):
        super().__init__(name)
        self.token = vk_token

    def _get_user_id(self, name):
        URL = 'https://api.vk.com/method/users.get'
        params = {
            'user_ids': name,
            'access_token': vk_token,
            'v': '5.131'
        }
        res = requests.get(URL, params=params)
        return (res.json()['response'][0]['id'])


    def get_maxsize_photo(self, name):
        URL = 'https://api.vk.com/method/photos.get'
        user_id = self._get_user_id(name)
        params = {
            'user_ids': name,
            'access_token': vk_token,
            'v':'5.131',
            'owner_id': user_id,
            'album_id': 'profile',
            'extended' : '1',
            'count': '999',
            'extended': '1'
        }
        res = requests.get(URL, params=params)
        photo_dict = {}
        f_photo_dict = {}
        photo_list = []
        like = 0
        result = res.json()['response']['items']
        for photos in result:
            like = photos['likes']['count']
            for photo in photos['sizes']:
                photo['likes'] = like
                photo['size'] = photo['height'] + photo['width']
                f_photo = {key: photo[key] for key in photo if key not in ['height', 'width', 'type']}
                photo_dict = {**photo_dict, **f_photo}
            photo_list.append([*photo_dict.values()])
            photo_list.sort(key=lambda i: i[2], reverse=True)
        return(photo_list)


    def upl_from_vk_to_ya(self, name):
        photo_list = self.get_maxsize_photo(name)
        if len(photo_list) >5:
            for photo in photo_list[0:5]:
                disk_file_path = (f'/vk_test/{photo[2]}.jpg')
                photo_url = photo[0]
                self.ya_upload(disk_file_path, photo_url)
        else:
            for photo in photo_list:
                disk_file_path = (f'/vk_test/{photo[2]}.jpg')
                photo_url = photo[0]
                self.ya_upload(disk_file_path, photo_url)



if __name__ == '__main__':
    name = input('Введите id или как-называются-эти-буквы-вместо-id: ')
    vamilton = VkPhotos(name)
    vamilton.upl_from_vk_to_ya(name)
