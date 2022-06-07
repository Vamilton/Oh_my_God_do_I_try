import configparser
import requests
import json
import sys
from progress.bar import IncrementalBar
from pprint import pprint

#Токен брать тут: https://developers.google.com/oauthplayground/

class GoogleUploader:
    def __init__(self):
        self.path = 'settings.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.path)
        self.token = self.config.get('Tokens', 'google_token')


    def new_ggl_folder(self):
        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
            'Content-Type': 'application/json'
        }
        folder_name = input('Как назвать папку для фото? ')
        url = 'https://www.googleapis.com/drive/v3/files'
        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        r = requests.post(url, headers=headers, data=json.dumps(metadata))
        if r.status_code == 401:
            sys.exit('Токен устарел, обнови и начни сначала.')
        folder_id = r.json()['id']
        return folder_id


    def goodle_upload(self, folder_id, f_name, f_url):
        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
        }
        url = 'https://www.googleapis.com/upload/drive/v3/files/?uploadType=multipart'
        metadata = {
            'name': f_name,
            'parents': [folder_id]
        }
        files = {
            'data': ('metadata', json.dumps(metadata), 'application/json; charset=UTF-8'),
            'file': requests.get(f_url).content
        }
        response = requests.post(url, headers=headers, files=files)

    def upl_to_ggl(self, photo_list, quantity=5):
        names_list = []
        folder_id = self.new_ggl_folder()
        if len(photo_list) > quantity:
            bar = IncrementalBar('Загрузка фото на Гугл', max=quantity)
            for photo in photo_list[0:quantity]:
                f_url = photo[0]
                f_name = (f'{photo[2]}.jpg')
                if f_name in names_list:
                    f_name = f'{photo[2]}_{photo[3]}.jpg'
                self.goodle_upload(folder_id, f_name, f_url)
                bar.next()
