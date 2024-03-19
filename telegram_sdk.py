import requests
import time
from config import config


class BotHandler:
    """
    класс для работы с телеграм ботом (отправка сообщений, файлов)
    это просто базовый набор методов/возможностей работы с ботом, мы же будем пользоваться 
    не всеми, а например отправкой сообщений или файлов
    """
    def __init__(self):
        self.config = config
        self.last_update_id = 0

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        if self.last_update_id > 0:
            params = {'timeout': timeout, 'offset': self.last_update_id}
            resp = requests.get(self.config.api_url + method, params)
            result_json = resp.json()['result']
        else:
            params = {'timeout': timeout, 'offset': offset}
            resp = requests.get(self.config.api_url + method, params)
            result_json = resp.json()['result']
        return result_json

    def send_message(self, text):
        params = {'chat_id': self.config.CHAT_ID, 'text': text, "parse_mode": "Markdown"}
        method = 'sendMessage'
        resp = requests.post(self.config.api_url + method, params)
        return resp

    def send_post(self, text, channel_id=None):
        if not channel_id:
            channel_id = self.config.CHANNEL_CHAT_ID
        params = {'chat_id': channel_id, 'text': text, "parse_mode": "Markdown"}
        method = 'sendMessage'
        resp = requests.post(self.config.api_url + method, params)
        return resp

    def send_file(self, document, caption, channel_id=None):
        if not channel_id:
            channel_id = self.config.CHANNEL_CHAT_ID
        files = {'document': open(document, 'rb')}
        resp = requests.post(self.config.api_url + 'sendDocument?chat_id=' + channel_id + f'&caption={caption}', files=files)
        return resp

    def send_photo(self, channel_id, document, caption):
        files = {'photo': open(document, 'rb')}
        resp = requests.post(self.config.api_url + 'sendPhoto?chat_id=' + channel_id + f'&caption={caption}', files=files)
        return resp

    def get_last_update(self):
        try:
            get_result = self.get_updates()
            new_updates = []
            last_update = get_result[-1]
            if last_update['update_id'] > self.last_update_id:
                for update in get_result:
                    if update['update_id'] > self.last_update_id:
                        new_updates.append(update)

            self.last_update_id = last_update['update_id']
            return new_updates
        except Exception:
            time.sleep(60)
            get_result = self.get_updates()
            new_updates = []
            last_update = get_result[-1]
            if last_update['update_id'] > self.last_update_id:
                for update in get_result:
                    if update['update_id'] > self.last_update_id:
                        new_updates.append(update)

            self.last_update_id = last_update['update_id']
            return new_updates

    def forward(self, mess):
        try:
            chat_id = mess['message']['chat']['id']
            message_id = mess['message']['message_id']
            method = 'forwardMessage'
            params = {'chat_id': self.config.CHAT_ID, 'from_chat_id': chat_id, 'message_id': message_id}
            resp = requests.get(self.config.api_url + method, params)
            return resp
        except KeyError:
            print('KeyError on mess')
            print(mess)