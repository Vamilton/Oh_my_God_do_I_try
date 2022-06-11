import configparser
from files.Vkontakte import VkPhotos
from files.Ya_upload import YaUploader
from files.Odnokl import OkPhotos
from files.Google import GoogleUploader
from files.Facebook import Facebook
import urllib
import requests

def read_config():
    path = 'settings.ini'
    config = configparser.ConfigParser()
    config.read(path)
    return config

def what_to_do():
    upl_from = ['вк', 'ок', 'фб']
    upl_to = ['яндекс', 'гугл']
    command_from = input('Откуда грузим? (Вк, Ок) ')
    while command_from not in upl_from:
        command_from = input('Я такое не понимаю, введи ещё раз: ')
    command_to = input('Куда грузим? (Яндекс, Гугл) ')
    while command_to not in upl_to:
        command_to = input('Я такое не понимаю, введи ещё раз: ')
    if command_from.lower() == 'вк':
        photo_list = VkPhotos().get_maxsize_photo()
    elif command_from.lower() == 'ок':
        photo_list = OkPhotos().get_album_photos()
    elif command_from.lower() == 'фб':
        photo_list = Facebook.get_maxsize_photo()
    else:
        print('Прости, я такое не умею')
    if command_to.lower() == 'яндекс':
        rec = YaUploader().upl_to_ya(photo_list)
    elif command_to.lower() == 'гугл':
        rec = GoogleUploader().upl_to_ggl(photo_list)
    else:
        print('Прости, я такое не умею')


if __name__ == '__main__':
    config = read_config()
    what_to_do()



