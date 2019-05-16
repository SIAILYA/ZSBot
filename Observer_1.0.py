import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from random import randint
import requests
import pendulum
import pickle


class Bot:
    def __init__(self):
       self.vk = vk_api.VkApi(token='group_token')
        self.long_poll = VkBotLongPoll(self.vk, group_id='group_id')
        self.vk_api = self.vk.get_api()

        self.warns = {}
        try:
            with open('warns.txt', 'rb') as inp:
                try:
                    self.warns = pickle.load(inp)
                except EOFError:
                    self.warns = {}
        except FileNotFoundError:
            l = open('warns.txt', 'w')
            l.close()

        self.lexics = ['ебать', 'хуй', 'пизда', 'бля', 'блять', 'бля', 'ебать',
                       'охуеть', 'ахуеть', 'охуел', 'ахуел', 'охуела', 'ахуела',
                       'нахуй', 'нахуя', 'сука', 'заебал', 'пидарас', 'нихуя',
                       'съебал', 'ебучий', 'поебать']
        try:
            with open('lexics.txt', 'rb') as inp:
                try:
                    self.lexics += pickle.load(inp)
                    self.lexics = list(set(self.lexics))
                except EOFError:
                    pass
        except FileNotFoundError:
            l = open('lexics.txt', 'w')
            l.close()

        self.admins = {2000000001:[223632391]}
        try:
            with open('admins.txt', 'rb') as inp:
                try:
                    self.admins.update(pickle.load(inp))
                except EOFError:
                    pass
        except FileNotFoundError:
            l = open('admins.txt', 'w')
            l.close()

        self.whitelist = [222383631, 223632391]
        try:
            with open('white.txt', 'rb') as inp:
                try:
                    self.admins += pickle.load(inp)
                except EOFError:
                    pass
        except FileNotFoundError:
            l = open('white.txt', 'w')
            l.close()

        self.rules = {}
        try:
            with open('rules.txt', 'rb') as inp:
                try:
                    self.rules.update(pickle.load(inp))
                except EOFError:
                    pass
        except FileNotFoundError:
            l = open('rules.txt', 'w')
            l.close()

    def save_to_file(self, name, var):
        with open(name, 'wb') as out:
            pickle.dump(var, out)

    def main(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                # self.warns[event.obj.from_id] = self.warns.get(event.obj.from_id, 0)
                with open('warns.txt', 'wb') as out:
                    pickle.dump(self.warns, out)
                self.req = self.vk_api.users.get(user_ids=event.obj.from_id, fields='photo_id',
                                                 name_case='nom')
                self.user_id = event.obj.from_id
                self.inbox(event)
                print(self.req[0]['first_name'], ' ',  self.req[0]['last_name'], ': ',
                      event.obj.text, sep='')
                if event.obj.text == '':
                    print(event.obj)
                    if event.obj.action['type'] == 'chat_unpin_message':
                        try:
                            self.vk_api.messages.pin(peer_id=event.obj.peer_id, message_id=event.obj.action['conversation_message_id'])
                        except vk_api.exceptions.ApiError:
                            self.send_msg(event.obj.peer_id, 'В беседе включена функция автозакреплния, но произошла внутреняя ошибка: vk_api.exceptions.ApiError')

    def inbox(self, event):
        if event.obj.text[0] == '!':
            self.admin_commands(event)
        if 'илья' in event.obj.text.lower():
            self.send_msg(event.obj.peer_id, 'Кстати хочется заметить, что Илья дебил')
        if 'филипп' in event.obj.text.lower():
            self.send_msg(event.obj.peer_id, 'Кстати хочется заметить, что Филипп дебил')
        if (event.obj.text.lower() == 'время') or (event.obj.text.lower() == 'дата'):
            self.send_msg(event.obj.peer_id, self.get_time(event.obj.text.lower()))
        if event.obj.text.lower() == 'план' or event.obj.text.lower() == 'расписание':
            self.down_plan()
            self.photo(event.obj.peer_id, root='res.png')
        if event.obj.text.lower() in ['анекбот', 'анек']:
            self.send_msg(event.obj.peer_id, self.get_humor())
        if self.obscene_language(event):
            user_id = event.obj.from_id
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

            self.save_to_file('warns.txt', self.warns)

    def admin_commands(self, event):
        msg = event.obj.text
        if 'вайтлист' in msg:
            if event.obj.from_id in self.admins[event.obj.peer_id]:
                if 'reply_message' in event.obj:
                    self.whitelist += [event.obj.reply_message['from_id']]
                    self.send_msg(event.obj.peer_id, f'Пользователь @id{event.obj.reply_message["from_id"]}'
                    f'({self.vk_api.users.get(user_ids=event.obj.reply_message["from_id"], fields="photo_id", name_case="nom")[0]["first_name"]}) внесен в белый список!')
                    self.save_to_file('whitelist.txt', self.whitelist)
                else:
                    self.send_msg(event.obj.peer_id, 'Перешлите чье-либо сообщение, чтобы добавить человека в белый список')

        elif 'мат' in msg:
            pass

        elif 'варн' in msg:
            pass

        elif 'админ' in msg:
            if event.obj.from_id in self.admins[event.obj.peer_id]:
                if 'reply_message' in event.obj:
                    new_admin = {event.obj.peer_id: self.admins.get(event.obj.peer_id, []) + [
                        event.obj.reply_message['from_id']]}
                    self.admins.update(new_admin)
                    print(self.admins[event.obj.peer_id])
                    self.send_msg(event.obj.peer_id, f'Пользователь @id{event.obj.reply_message["from_id"]}'
                    f'({self.vk_api.users.get(user_ids=event.obj.reply_message["from_id"], fields="photo_id", name_case="nom")[0]["first_name"]}) теперь администратор беседы!')
                    self.save_to_file('admins.txt', self.admins)
                else:
                    self.send_msg(event.obj.peer_id, 'Перешлите чье-либо сообщение, чтобы добавить человека в список администраторов беседы')
            else:
                self.send_msg(event.obj.peer_id, 'Вы не являетесь администратором беседы')

        elif 'кик' in msg:
            if event.obj.from_id in self.admins[event.obj.peer_id]:
                if 'reply_message' in event.obj:
                    try:
                        self.kick(event, by_reply=1)
                    except vk_api.exceptions.ApiError:
                        self.send_msg(event.obj.peer_id, 'Не могу исключить данного пользователя!')
                else:
                    self.send_msg(event.obj.peer_id, 'Перешлите чье-либо сообщение, чтобы кикнуть человека')

        elif 'обнулить' in msg:
            if event.obj.from_id in self.admins[event.obj.peer_id]:
                if event.obj.from_id in [223632391]:
                    self.warns = []
                    self.save_to_file('warns.txt', self.warns)
                    self.send_msg(event.obj.peer_id, 'Все варны пользователей успешно обнулены!')

        elif 'правила' in msg:
            if event.obj.text.strip() == '!правила':
                try:
                    self.send_msg(event.obj.peer_id, f'Правила беседы: \n {self.rules[event.obj.peer_id]}')
                except KeyError:
                    self.send_msg(event.obj.peer_id, 'Правила беседы не установлены!')
            elif event.obj.from_id in self.admins[event.obj.peer_id]:
                self.rules[event.obj.peer_id] = self.rules.get(event.obj.peer_id, '')
                self.rules[event.obj.peer_id] = event.obj.text.lstrip('!правила')
                self.send_msg(event.obj.peer_id, 'Правила беседы обновлены!')
                self.save_to_file('rules.txt', self.rules)
            else:
                try:
                    self.send_msg(event.obj.peer_id, f'Правила беседы: \n {self.rules[event.obj.peer_id]}')
                except KeyError:
                    self.send_msg(event.obj.peer_id, 'Правила беседы не установлены!')

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

    def obscene_language(self, event):
        if self.user_id not in self.whitelist:
            for word in event.obj.text.split(' '):
                if set(word.lower()) in [set(i) for i in self.lexics]:
                    return True
            for obscene_word in self.lexics:
                if (obscene_word in event.obj.text.replace(' ', '').lower()) and not(self.obscene_warning(event)):
                    return True
            return False

    def obscene_warning(self, event):
        for word in 'заштрихуй дебет оскорблять перебалтывай'.split(' '):
            if word in event.obj.text.replace(' ', '').lower():
                return True
        return False

    def obscene_check(self, word):
        if word in self.lexics:
            return True

    def kick(self, event, by_reply=0):
        if by_reply == 0:
            if event.obj.from_id not in self.whitelist:
                self.vk_api.messages.removeChatUser(chat_id=event.obj.peer_id - 2000000000,
                                                    member_id=event.obj.from_id)
            else:
                self.send_msg(event.obj.peer_id, f'Пользователь @id{event.obj.from_id}({self.req[0]["first_name"]}) находится в вайтлисте!')
        else:
            if event.obj.reply_message['from_id'] not in self.admins[event.obj.peer_id]:
                self.vk_api.messages.removeChatUser(chat_id=event.obj.peer_id - 2000000000,
                                                    member_id=event.obj.reply_message['from_id'])
            else:
                self.send_msg(event.obj.peer_id, f'Пользователь @id{event.obj.from_id}({self.req[0]["first_name"]}) является администратором беседы')

    @staticmethod
    def get_time(datetime):
        if datetime == 'время':
            return pendulum.now(tz='Europe/Moscow').format('HH:mm:ss')
        else:
            return pendulum.now(tz='Europe/Moscow').format('DD MMMM YYYY, dddd', locale='en')

    @staticmethod
    def down_plan():
        res = requests.get("http://амтэк35.рф/index.php?mode=schedule")
        x = str(res.content).index('upimage', 0, 60000)
        url = str(res.content)[x - 34:x + 27]
        img = requests.get(url)
        out = open("res.png", "wb")
        out.write(img.content)
        out.close()

    @staticmethod
    def get_humor():
        site = requests.get('https://nekdo.ru/random/').text
        ind1 = str(site).index('<div class="text" id=', 0, 100000)
        ind2 = str(site).index('</div>', ind1, 100000)
        anek = '\n'.join(site[ind1 + 24:ind2][site[ind1 + 24:ind2].index('>') + 1:].split('<br>'))
        return anek

if __name__ == "__main__":
    # Bot.send_msg()
    Bot().main()
