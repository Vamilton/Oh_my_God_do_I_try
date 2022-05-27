import requests
import os
import time
from pprint import pprint
from progress.bar import IncrementalBar
from datetime import datetime
import json
from ok_api import OkApi
from google.oauth2 import service_account
from apiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
import io
import urllib
import urllib.request

with open('vk_token.txt', 'r') as file_object:
    vk_token = file_object.read().strip()

with open('ya_token.txt', 'r') as file_object:
    ya_token = file_object.read().strip()

with open('OK_ACCESS_TOKEN.txt', 'r') as file_object:
    ok_access_token = file_object.read().strip()

with open('OK_APP_PUBLIC_TOKEN.txt', 'r') as file_object:
    ok_public_token = file_object.read().strip()

with open('OK_APP_PRIVATE_TOKEN.txt', 'r') as file_object:
    ok_private_token = file_object.read().strip()

with open('Session_secret_key.txt', 'r') as file_object:
    session_secret_key = file_object.read().strip()

with open('famous-momentum-351512-1ba814e3d26c.json', 'r') as file_object:
    ggl_token = json.load(file_object)['private_key']

#-----------------------Загрузчики-------------------
class YaUploader:
    def __init__(self, token):
        self.ya_token = ya_token
        self.header = {
            'Content-Type': 'application/json',

            'Authorization': f'OAuth {ya_token}'
        }

    def ya_upload(self, disk_file_path, photo_url):
        param = {'url': photo_url, 'overwrite': 'true', 'path': disk_file_path}
        response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=self.header, params=param)

#==========================#
class GoogleUploader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.servise_account_file = r'C:\Users\Блейз\Documents\Питонян\Домашки\Курсовое\famous-momentum-351512-1ba814e3d26c.json'
        self.credentials = service_account.Credentials.from_service_account_file(
            self.servise_account_file, scopes=self.SCOPES)
        self.service = build('drive', 'v3', credentials=self.credentials)

    def goodle_upload(self):
        folder_id = '1vAKblfbfZYPJRT_9F0rsbiI1HB8GfDrg'
        url = "https://sun9-77.userapi.com/s/v1/if2/lPNZ9S6_0vfbK992z9e8LAur5qji-tiePWmm_SuTVgOnVjVukueY0jh0GtercEHRgK25O79xR77vOZjTZm8Oe7OF.jpg?size=1728x2160&quality=95&type=album"
        response = urllib.request.urlopen(url)
        fh = io.BytesIO(response.read())
        media_body = MediaIoBaseUpload(fh, mimetype='image/jpeg',
                                       chunksize=1024 * 1024, resumable=True)
        body = {
            'title': 'pic.jpg',
            'parents': [folder_id]
        }
        r = self.service.files().create(body=body, media_body=media_body).execute()
        pprint(r)

#-------------------Вконтакте--------------

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
        }
        res = requests.get(URL, params=params)
        photo_dict = {}
        f_photo_dict = {}
        photo_list = []
        like = 0
        result = res.json()['response']['items']
        for photos in result:
            like = photos['likes']['count']
            date = datetime.fromtimestamp(photos['date']).strftime("%B_%d_%Y")
            for photo in photos['sizes']:
                photo['likes'] = like
                photo['size'] = photo['height'] + photo['width']
                photo['date'] = date
                f_photo = {key: photo[key] for key in photo if key not in ['height', 'width']}
                photo_dict = {**photo_dict, **f_photo}
            photo_list.append([*photo_dict.values()])
            photo_list.sort(key=lambda i: i[2], reverse=True)
        return(photo_list)


    def vk_data(self, f_name, size):
        vk_data = {}
        vk_data['file_name'] = f_name
        vk_data['size'] = size
        return vk_data

    def vk_info(self, vk_data):
        with open("vk_on_ya_info.json", "w") as f:
            json.dump(vk_data, f)

    def upl_from_vk_to_ya(self, name, quantity=5):
        vk_response = []
        names_list = []
        photo_list = self.get_maxsize_photo(name)
        if len(photo_list) >= quantity:
            bar = IncrementalBar('Загрузка фото с ВК', max=5)
            for photo in photo_list[0:quantity]:
                f_name = (f'{photo[2]}.jpg')
                if f_name in names_list:
                    disk_file_path = f'/vk_test/{photo[2]}{photo[4]}.jpg'
                    f_name = f'{photo[2]}_{photo[4]}.jpg'
                else:
                    disk_file_path = (f'/vk_test/{photo[2]}.jpg')
                photo_url = photo[0]
                self.ya_upload(disk_file_path, photo_url)
                vk_response.append(self.vk_data(f_name, photo[1]))
                names_list.append(f_name)
                bar.next()
        else:
            bar = IncrementalBar('Загрузка фото с ВК', max=len(photo_list))
            for photo in photo_list:
                f_name = (f'{photo[2]}.jpg')
                if f_name in names_list:
                    disk_file_path = f'/vk_test/{photo[2]}ddddd.jpg'
                    f_name = f'{photo[2]}_{date.today()}.jpg'

                else:
                    disk_file_path = (f'/vk_test/{photo[2]}.jpg')
                names_list.append(f_name)
                photo_url = photo[0]
                self.ya_upload(disk_file_path, photo_url)
                bar.next()
        self.vk_info(vk_response)



#---------------Одноклассники----------------


class OkPhotos(YaUploader):

    def __init__(self, name):
        super().__init__(name)
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
        return(likes_and_url)



    def upl_from_ok_to_ya(self, name, quantity=5):
        ok_response = []
        photo_list = self.get_photo_likes(name)
        if len(photo_list) >= quantity:
            bar = IncrementalBar('Загрузка фото с ОК', max=5)
            for photo in photo_list[0:quantity]:
                f_name = (f'{photo[0]}.jpg')
                disk_file_path = (f'/ok_test/{photo[0]}.jpg')
                photo_url = photo[1]
                self.ya_upload(disk_file_path, photo_url)
                # ok_response.append(self.vk_data(f_name, photo[1]))
                bar.next()
        else:
            bar = IncrementalBar('Загрузка фото с OK', max=len(photo_list))
            for photo in photo_list:
                f_name = (f'{photo[0]}.jpg')
                disk_file_path = (f'/ok_test/{photo[0]}.jpg')
                photo_url = photo[1]
                self.ya_upload(disk_file_path, photo_url)
                bar.next()
        # self.vk_info(vk_response)


if __name__ == '__main__':
    # name = input('Введите id или как-называются-эти-буквы-вместо-id: ')
    you = GoogleUploader()
    you.goodle_upload()


