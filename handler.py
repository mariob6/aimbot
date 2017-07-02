import time
import random


class MessageHandler(object):

    _HI = ['ciao', 'ciaone', 'bella ', 'hey']

    _INSULT = ['coglione', 'ricchione', 'stronzo', 'frocio', 'merda', 'cesso',
               'gay', 'idiota', 'imbecille', 'pure tu']

    def __init__(self, botId, botName, client, socket_delay=1):
        self.botId = botId
        self.botName = botName
        self.mention = self.getMention(botId)
        self.client = client
        self.delay = socket_delay

    def isPrivate(self, event):
        """Checks if private slack channel"""
        return event.get('channel').startswith('D')

    @staticmethod
    def getMention(user):
        return '<@{0}>'.format(user)

    def _isForMe(self, event):
        eventType = event.get('type')

        if not eventType or eventType != 'message' or \
                event.get('user') == self.botId:
            return False

        if self.isPrivate(event):
            return 'private'

        messageText = event.get('text')

        if self.mention in messageText.split():
            return 'mention'

        if self.botName in messageText.split():
            return 'name'

    def _decorateMessage(self, userId, text, mention=False, front=True,
                         toChannel=False):
        if toChannel:
            return '{0} {1}'.format(text, 'a tutti')

        if mention:
            userName = self.getMention(userId)
        else:
            # TODO get only the userName
            userName = self.getMention(userId)

        if front:
            return '{0} {1}'.format(userName, text)
        else:
            return '{0} {1}'.format(text, userName)

    def _postMessage(self, messageText, channel):
        self.client.api_call(
            'chat.postMessage', channel=channel,
            text=messageText, as_user=True)

    def isHi(self, message):
        for token in message.split(' '):
            if token in self._HI:
                return True

    def sayHi(self, user, channel, mention=False):
        """In private channel: say Hi + username
        In public: say Hi + username if mention else Hi everybody"""
        # TODO hack
        if channel.startswith('D'):
            mention = False
            messageText = self._decorateMessage(
                user, random.choice(self._HI), mention=mention, front=False)
        elif mention:
            messageText = self._decorateMessage(
                user, random.choice(self._HI), mention=mention, front=False)
        else:
            messageText = self._decorateMessage(
                user, random.choice(self._HI), toChannel=True)

        self._postMessage(messageText=messageText, channel=channel)

    def isInsult(self, message):
        for token in message.split(' '):
            if token in self._INSULT:
                return True

    def sayInsult(self, user, channel, mention=False):
        if channel.startswith('D') or not mention:
            mention = False
            messageText = self._decorateMessage(
                user, random.choice(self._INSULT), mention=mention)
        elif mention:
            messageText = self._decorateMessage(
                user, random.choice(self._INSULT), mention=mention)

        self._postMessage(messageText=messageText, channel=channel)

    def handleMessage(self, message, user, channel, mention):
        if self.isHi(message=message):
            return self.sayHi(user, channel, mention)
        elif self.isInsult(message=message):
            return self.sayInsult(user, channel, mention)

    def run(self):
        if not self.client.rtm_connect():
            print('[!] Connection to Slack failed.')
            return

        print('[.] AimBot is ON...')
        while True:
            eventList = self.client.rtm_read()
            if not len(eventList):
                continue

            for event in eventList:
                forMe = self._isForMe(event)
                if forMe:
                    mention = bool(forMe == 'mention')
                    self.handleMessage(
                        message=event.get('text'),
                        user=event.get('user'),
                        channel=event.get('channel'),
                        mention=mention)
        time.sleep(self.delay)
