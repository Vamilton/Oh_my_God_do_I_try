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
        elif r.status_code != 200:
            sys.exit('Что-то пошло не так, давай сначала.')
        folder_id = r.json()['id']
        return folder_id, folder_name


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
        if response.status_code != 200:
            sys.exit('Что-то пошло не так, давай сначала.')

    def rec_data(self, f_name, size):
        rec_data = {}
        rec_data['file_name'] = f_name
        rec_data['size'] = size
        return rec_data

    def rec_info(self, rec_data, folder_name):
        with open(f'{folder_name}_info.json', 'w') as f:
            json.dump(rec_data, f)


    def upl_to_ggl(self, photo_list, quantity=5):
        names_list = []
        response = []
        folder_id, folder_name = self.new_ggl_folder()
        if len(photo_list) < quantity:
            quantity = len(photo_list)
        bar = IncrementalBar('Загрузка фото на Гугл', max=quantity)
        for photo in photo_list[0:quantity]:
            f_url = photo[0]
            f_name = (f'{photo[2]}.jpg')
            if f_name in names_list:
                f_name = f'{photo[2]}_{photo[3]}.jpg'
            self.goodle_upload(folder_id, f_name, f_url)
            response.append(self.rec_data(f_name, photo[1]))
            names_list.append(f_name)
            bar.next()
        self.rec_info(response, folder_name)