from google.oauth2 import service_account
from apiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
import os
import time
from pprint import pprint


with open('famous-momentum-351512-1ba814e3d26c.json', 'r') as file_object:
    ggl_token = json.load(file_object)['private_key']

class GoogleUploader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file'
          ]
        self.servise_account_file = r'C:\Users\Блейз\Documents\Питонян\Домашки\Курсовое\famous-momentum-351512-1ba814e3d26c.json'
        self.credentials = service_account.Credentials.from_service_account_file(
            self.servise_account_file, scopes=self.SCOPES)
        self.service = build('drive', 'v3', credentials=self.credentials)

    def new_bad_ggl_folder(self, folder_name):
        # вот эта штука сохраняет не на мой диск, а на диск аккаунта Google Cloud Platform,
        # но может расшарить папку на любой емейл
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            "role": "owner", "type": "user", 'emailAddress': 'vamilton@gmail.com'
        }
        r = self.drive_service.files().create(body = body).execute()
        r = self.service.files().create(body=file_metadata).execute()
        self.service.permissions().create(body={"role": "owner", "type": "user", 'emailAddress': 'some_email@gmail.com'}, fileId=r['id']).execute()

    def goodle_upload(self, f_url, f_name, folder_name):
        token = self.token
        folder_id = self.new_ggl_folder(token, folder_name)


        #-----это всё прекрасно, но не работает, если нет доступа к папке----
        response = urllib.request.urlopen(f_url)
        fh = io.BytesIO(response.read())
        media_body = MediaIoBaseUpload(fh, mimetype='image/jpeg',
                                       resumable=True)
        body = {'name': f_name, 'parents': [folder_id]}
        r = self.service.files().create(body=body, media_body=media_body).execute()
