import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from random import randint
import requests
import pendulum
import pickle

# ToDo: 

class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(token='a58d2fee5ee13e1395da4a684e8067c39ed66a'
                                     '91f1d22344059901c29b58bca9601baf20dca1fe1b3d1ff')
        self.long_poll = VkBotLongPoll(self.vk, group_id='181100955')
        self.vk_api = self.vk.get_api()

        self.warns = {}
        with open('warns.txt', 'rb') as inp:
            try:
                self.warns = pickle.load(inp)
            except EOFError:
                self.warns = {}

    def photo(self, send_id, root='img.jpg'):
        request = requests.post(self.vk.method('photos.getMessagesUploadServer')['upload_url'],
                                files={'photo': open(root, 'rb')}).json()
        save_photo = self.vk_api.photos.saveMessagesPhoto(
            photo=request['photo'], server=request['server'], hash=request['hash'])[0]
        photo = f'photo{save_photo["owner_id"]}_{save_photo["id"]}'
        self.vk_api.messages.send(peer_id=send_id, message='',
                                  random_id=randint(-1000, 1000), attachment=photo)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id, message=message, random_id=randint(-1000, 1000))

    def main(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.warns[event.obj.from_id] = self.warns.get(event.obj.from_id, 0)
                with open('warns.txt', 'wb') as out:
                    pickle.dump(self.warns, out)
                print(event.obj.peer_id, event.obj.from_id)
                self.req = self.vk_api.users.get(user_ids=event.obj.from_id, fields='photo_id',
                                                 name_case='nom')
                self.inbox(event)
                print(self.req[0]['first_name'], ' в беседе ', event.obj.peer_id, ': ',
                      event.obj.text, sep='')

    def obscene_language(self, event):
        for word in event.obj.text.split(' '):
            if word.lower() in ['ебать', 'хуй', 'пизда', 'бля', 'блять', 'бля', 'ебать',
                                'охуеть', 'ахуеть', 'охуел', 'ахуел', 'охуела', 'ахуела',
                                'нахуй', 'нахуя', 'сука', 'заебал', 'пидарас', 'нихуя']:
                return True
        return False

    def inbox(self, event):
        if 'илья' in event.obj.text.lower():
            self.send_msg(event.obj.peer_id, 'Кстати хочется заметить, что Илья дебил')
        if 'филип' in event.obj.text.lower():
            self.send_msg(event.obj.peer_id, 'Кстати хочется заметить, что Филипп дебил')
        if (event.obj.text.lower() == 'время') or (event.obj.text.lower() == 'дата'):
            self.send_msg(event.obj.peer_id, self.get_time(event.obj.text.lower()))
        if self.obscene_language(event):
            user_id = event.obj.from_id
            print(self.warns)
            self.warns[event.obj.from_id] += 1
            count = self.warns[event.obj.from_id]
            name = self.req[0]['first_name']
            if count < 4:
                warn = f'@id{user_id}({name}), в данной беседе запрещен мат!' \
                    f' Вы получили {count} предупреждений. Еще {5 - count} варнов и БАН'
                # print(self.warns)
                self.send_msg(event.obj.peer_id, warn)
            elif count == 4:
                kick = f'@id{user_id}({name}), вы получили уже 4 предупрежденя за мат.' \
                    f' В следующий раз вы будете исключены из беседы!'
                self.send_msg(event.obj.peer_id, kick)
            else:
                self.kick(event)
            with open('warns.txt', 'wb') as out:
                pickle.dump(self.warns, out)
            # print(self.req[0]['first_name'] + ' матерится')

    @staticmethod
    def get_time(datetime):
        if datetime == 'время':
            return pendulum.now(tz='Europe/Moscow').format('HH:mm:ss')
        else:
            return pendulum.now(tz='Europe/Moscow').format('DD MMMM YYYY, dddd', locale='en')

    def kick(self, event):
        if event.obj.from_id not in [222383631, 223632391]:
            self.vk_api.messages.removeChatUser(chat_id=event.obj.peer_id - 2000000000,
                                                member_id=event.obj.from_id)
        else:
            print(f'Пользователь vk.com/id{event.obj.from_id} находится в вайтлисте!')


if __name__ == "__main__":
    Bot().main()
