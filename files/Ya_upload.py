import configparser
import requests
from progress.bar import IncrementalBar
import json
import sys


class YaUploader:
    def __init__(self):
        self.path = 'settings.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.path)
        self.token = self.config.get("Tokens", "ya_token")
        self.header = {
            'Content-Type': 'application/json',

            'Authorization': f'OAuth {self.token}'
        }

    def new_folder(self, folder_name):
        its_url = f'https://cloud-api.yandex.net/v1/disk/resources?path={folder_name}'
        response = requests.put(its_url, headers=self.header)
        if response.status_code != 201:
            sys.exit('Что-то пошло не так, давай сначала.')
        return response.json()


    def ya_upload(self, disk_file_path, photo_url):
        param = {'url': photo_url, 'overwrite': 'true', 'path': disk_file_path}
        response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=self.header, params=param)
        if response.status_code != 202:
            sys.exit('Что-то пошло не так, давай сначала.')

    def rec_data(self, f_name, size):
        rec_data = {}
        rec_data['file_name'] = f_name
        rec_data['size'] = size
        return rec_data

    def rec_info(self, rec_data, folder_name):
        with open(f'{folder_name}_info.json', 'w') as f:
            json.dump(rec_data, f)

    def upl_to_ya(self, photo_list, quantity=5):
        names_list = []
        response = []
        folder_name = input('Как назвать папку? ')
        self.new_folder(folder_name)
        if len(photo_list) < quantity:
            quantity = len(photo_list)
        bar = IncrementalBar('Загрузка фото на Яндекс', max=quantity)
        for photo in photo_list[0:quantity]:
            f_name = (f'{photo[2]}.jpg')
            if f_name in names_list:
                f_name = f'{photo[2]}_{photo[3]}.jpg'
            disk_file_path = f'/{folder_name}/{f_name}'
            photo_url = photo[0]
            self.ya_upload(disk_file_path, photo_url)
            response.append(self.rec_data(f_name, photo[1]))
            names_list.append(f_name)
            bar.next()
        self.rec_info(response, folder_name)
