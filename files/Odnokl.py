import configparser
from datetime import datetime
import sys
from pprint import pprint
from ok_api import OkApi

class OkPhotos:

    def __init__(self):
        self.path = 'settings.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.path)
        self.access_token = self.config.get("Tokens", "ok_access_token")
        self.application_key = self.config.get("Tokens", "ok_public_token")
        self.application_secret_key = self.config.get("Tokens", "ok_private_token")
        self.session_secret_key = self.config.get("Tokens", "session_secret_key")
        self.ok = OkApi(access_token=self.access_token,
                   application_key=self.application_key,
                   application_secret_key=self.application_secret_key)

    def get_album_photos(self):
        name = input('Введите id пользователя: ')
        photo_list = []
        field_s = 'photo.pic_max, photo.standard_height, photo.standard_width, photo.created_ms, photo.like_count'
        response = self.ok.photos.getPhotos(fid=name, fields=field_s, album_name='pphotos', count=100)
        if response.status_code != 200:
            sys.exit('Что-то пошло не так, давай сначала.')
        for photo in response.json()['photos']:
            photo_list.append([photo['pic_max'], f'{photo["standard_height"]}x{photo["standard_width"]}', photo['like_count'],
                                  datetime.fromtimestamp(photo['created_ms']/1000).strftime("%B_%d_%Y_%H-%M-%S"),
                                 photo["standard_height"]+photo["standard_width"] ]
                                 )
        while response.json()['hasMore']:
            ancho_r = response.json()['anchor']
            response = self.ok.photos.getPhotos(fid=name, anchor=ancho_r, fields=field_s, album_name='pphotos', count=100)
            if response.status_code != 200:
                sys.exit('Что-то пошло не так, давай сначала.')
            for photo in response.json()['photos']:
                photo_list.append([photo['pic_max'], f'{photo["standard_height"]}x{photo["standard_width"]}',
                                      datetime.fromtimestamp(photo['created_ms'] / 1000).strftime("%B_%d_%Y_%H-%M-%S"),
                                      photo['like_count'], photo["standard_height"] + photo["standard_width"]]
                                     )
        photo_list.sort(key=lambda i: i[4], reverse=True)
        return photo_list
