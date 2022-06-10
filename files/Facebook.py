import configparser
import requests
import json
import sys
from pprint import pprint

class Facebook:
    def __init__(self):
        self.path = 'settings.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.path)
        self.token = self.config.get('Tokens', 'facebook_token')

    def get_albums(self):
        album_list = {}
        rec = requests.get(f'https://graph.facebook.com/v14.0/me?fields=albums&access_token={self.token}')
        if rec.status_code != 200:
            sys.exit('Что-то пошло не так, давай сначала.')
        for album in rec.json()['albums']['data']:
            album_list[album['name']] = album['id']
        print('Доступные альбомы:')
        print(*album_list.keys(), sep='\n')
        need_album = ''
        while need_album not in album_list.keys():
            need_album = input('\nВыберите альбом из списка выше: ')
        album_id = album_list[need_album]
        return album_id

    def get_maxsize_photo(self):
        album_id = self.get_albums()
        photo_list = []
        likes = 0
        rec = requests.get(
            f'https://graph.facebook.com/v14.0/{album_id}?fields=photos%7Bheight%2Clink%2Cwidth%2Cupdated_time%7D&access_token={self.token}')
        if rec.status_code != 200:
            sys.exit('Что-то пошло не так, давай сначала.')
        for photo in rec.json()['photos']['data']:
            rec = requests.get(f"https://graph.facebook.com/v14.0/{photo['id']}?fields=images&access_token={self.token}")
            likes += 1
            like = f'sorry_no_data_{likes}'
            date = photo['updated_time'][:10]
            size = photo['width'] + photo['height']
            link = rec.json()['images'][0]['source']
            foto = [link, size, like, date]
            photo_list.append(foto)
            photo_list.sort(key=lambda i: i[1], reverse=True)
        return photo_list
