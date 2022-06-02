import requests
import os
import time
from pprint import pprint
from progress.bar import IncrementalBar
from datetime import datetime
import json
from ok_api import OkApi
import io
import urllib
import urllib.request
from PIL import Image
from files.Tokens import Tokens



#-----------------------Загрузчики-------------------
class YaUploader:
    def __init__(self):
        Tokens.__init__(self)
        self.header = {
            'Content-Type': 'application/json',

            'Authorization': f'OAuth {Tokens.ya_token(self)}'
        }

    def new_folder(self, folder_name):
        its_url = f'https://cloud-api.yandex.net/v1/disk/resources?path={folder_name}'
        response = requests.put(its_url, headers=self.header)
        return response.json()


    def ya_upload(self, disk_file_path, photo_url):
        param = {'url': photo_url, 'overwrite': 'true', 'path': disk_file_path}
        response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=self.header, params=param)

#-------------------------

#Токен брать тут: https://developers.google.com/oauthplayground/

class GoogleUploader:
    def __init__(self):
        Tokens.__init__(self)


    def new_ggl_folder(self, folder_name):
        token = Tokens.google_token(self)
        url = 'https://www.googleapis.com/drive/v3/files'
        headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json'
        }
        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        r = requests.post(url, headers=headers, data=json.dumps(metadata))
        folder_id = r.json()['id']
        return folder_id


    def goodle_upload(self, f_url, f_name, folder_name):
        token = Tokens.google_token(self)
        folder_id = self.new_ggl_folder(token, folder_name)

#-------------------Вконтакте--------------

class VkPhotos(YaUploader, GoogleUploader):

    def __init__(self, name):
        GoogleUploader.__init__(self)
        YaUploader.__init__(self)
        Tokens.__init__(self)


    def _get_user_id(self, name):
        URL = 'https://api.vk.com/method/users.get'
        params = {
            'user_ids': name,
            'access_token': Tokens.vk_token(self),
            'v': '5.131'
        }
        res = requests.get(URL, params=params)
        id_bool = bool(res.json()['response'])
        if not id_bool:
            name = input('Такого id не существует, введите нормальное: ')
            self._get_user_id(name)
        else:
            if 'can_access_closed' in res.json()['response'][0].keys() and not res.json()['response'][0]['can_access_closed']:
                name = input('Профиль закрыт, выберите другой: ')
                self._get_user_id(name)
            elif 'deactivated' in res.json()['response'][0].keys():
                name = input('Профиль неактивен, выберите другой: ')
                self._get_user_id(name)
            else:
                return (res.json()['response'][0]['id'])

    def get_size(self, url):
        foto_url = url
        raw = requests.get(foto_url, stream=True).raw
        size = Image.open(raw).size
        return size


    def get_maxsize_photo(self, name):
        URL = 'https://api.vk.com/method/photos.get'
        user_id = self._get_user_id(name)
        params = {
            'user_ids': name,
            'access_token': Tokens.vk_token(self),
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


    def vk_data(self, f_name, size):
        vk_data = {}
        vk_data['file_name'] = f_name
        vk_data['size'] = size
        return vk_data

    def vk_info(self, vk_data):
        with open("vk_on_ya_info.json", "w") as f:
            json.dump(vk_data, f)



    def upl_from_vk_to_ya(self, name, quantity=5):
        names_list = []
        vk_response = []
        photo_list = self.get_maxsize_photo(name)
        folder_name = f'Vk_{name}'
        self.new_folder(folder_name)
        if len(photo_list) < quantity:
            quantity = len(photo_list)
        bar = IncrementalBar('Загрузка фото с ВК на Яндекс', max=quantity)
        for photo in photo_list[0:quantity]:
            f_name = (f'{photo[2]}.jpg')
            if f_name in names_list:
                f_name = f'{photo[2]}_{photo[4]}.jpg'
            disk_file_path = f'/{folder_name}/{f_name}'
            photo_url = photo[0]
            self.ya_upload(disk_file_path, photo_url)
            vk_response.append(self.vk_data(f_name, photo[1]))
            names_list.append(f_name)
            bar.next()
        self.vk_info(vk_response)

    def upl_from_vk_to_ggl(self, name, quantity=5):
        photo_list = self.get_maxsize_photo(name)
        names_list = []
        folder_name = f'VK_{name}'
        if len(photo_list) > quantity:
            bar = IncrementalBar('Загрузка фото с ВК на Гугл', max=quantity)
            for photo in photo_list[0:quantity]:
                f_url = photo[0]
                f_name = (f'{photo[2]}.jpg')
                if f_name in names_list:
                    f_name = f'{photo[2]}_{date.today()}.jpg'
                self.goodle_upload(f_url, f_name, folder_name)


#---------------Одноклассники----------------


class OkPhotos(YaUploader):

    def __init__(self, name):
        YaUploader.__init__(self)
        self.access_token = ok_access_token
        self.application_key = ok_public_token
        self.application_secret_key = ok_private_token
        self.session_secret_key = session_secret_key
        self.ok = OkApi(access_token=self.access_token,
                   application_key=self.application_key,
                   application_secret_key=self.application_secret_key)

    def get_profile_photos(self, name):
        profile_photo = []
        response = self.ok.photos.getPhotos(fid=name, album_name='pphotos', count=100)
        for ids in (response.json()['photos']):
            profile_photo.append(ids['id'])
        return profile_photo

    def get_photo_likes(self, name):
        profile_photo = self.get_profile_photos(name)
        likes_and_url = []
        for id in profile_photo:
            response = self.ok.photos.getPhotoInfo(photo_id=id, scope='VALUABLE_ACCESS;PHOTO_CONTENT', session_secret_key='self.session_secret_key')
            likes_and_url.append([response.json()['photo']['like_count'], response.json()['photo']['pic640x480']])
        likes_and_url.sort(key=lambda i: i[0], reverse=True)
        return likes_and_url


    def ok_data(self, f_name, size):
        ok_data = {}
        ok_data['file_name'] = f_name
        ok_data['size'] = size
        return ok_data

    def ok_info(self, ok_data):
        with open("ok_on_ya_info.json", "w") as f:
            json.dump(ok_data, f)


    def upl_from_ok_to_ya(self, name, quantity=5):
        ok_response = []
        names_list = []
        photo_list = self.get_photo_likes(name)
        folder_name = f'Ok_{name}'
        self.new_folder(folder_name)
        if len(photo_list) < quantity:
            quantity = len(photo_list)
        bar = IncrementalBar('Загрузка фото с ОК на Яндекс', max=quantity)
        for photo in photo_list[0:quantity]:
            f_name = f'{photo[0]}.jpg'
            if f_name in names_list:
                f_name = f'{photo[0]}_nothing_can_be_done.jpg'
            disk_file_path = (f'/{folder_name}/{f_name}')
            photo_url = photo[1]
            names_list.append(f_name)
            self.ya_upload(disk_file_path, photo_url)
            size = VkPhotos.get_size(self, photo[1])
            ok_response.append(self.ok_data(f_name, size))
            bar.next()
        self.ok_info(ok_response)


if __name__ == '__main__':
    name = input('Введите id или как-называются-эти-буквы-вместо-id: ')
    you = VkPhotos(name)
    you.upl_from_vk_to_ya(name)

