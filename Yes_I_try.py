import requests
import os
import time
from pprint import pprint
from progress.bar import IncrementalBar
from datetime import datetime
import json
from ok_api import OkApi
import io
from PIL import Image
import configparser
from files.Vkontakte import VkPhotos
from files.Ya_upload import YaUploader
from files.Odnokl import OkPhotos

def read_config():
    path = 'settings.ini'
    config = configparser.ConfigParser()
    config.read(path)
    return config

def what_to_do():
    command_from = input('Откуда грузим? (Vk, Ok) ')
    command_to = input('Куда грузим? (Яндекс, Гугл) ')
    if command_from.lower() == 'vk':
        photo_list = VkPhotos().get_maxsize_photo()
    elif command_from.lower() == 'ok':
        photo_list = OkPhotos().get_album_photos()
    else:
        print('Прости, я больше ничего не умею')

    if command_to.lower() == 'яндекс':
        rec = YaUploader().upl_to_ya(photo_list)
    if command_to.lower() == 'гугл':
        print('Прости, я ещё так не умею')



if __name__ == '__main__':
    config = read_config()
    what_to_do()


