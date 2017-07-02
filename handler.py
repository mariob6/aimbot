import time
import random


class MessageHandler(object):

    _HI = {'ciao', 'ciaone', 'bella ', 'hey'}

    def __init__(self, botId, botName, client, socket_delay=1):
        self.botId = botId
        self.botName = botName
        self.mention = self.getMention(botName)
        self.client = client
        self.delay = socket_delay

    @staticmethod
    def isPrivate(event):
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
        print(messageText)

        if self.mention in messageText.split():
            return 'mention'

        if self.botName in messageText.split():
            return 'name'

    def _postMessage(self, messageText, channel):
        self.client.api_call(
            'chat.postMessage', channel=channel,
            text=messageText, as_user=True)

    @staticmethod
    def isHi(self, message):
        for token in message.split(' '):
            if token in self._HI:
                return True

    def sayHi(self, user, channel, private=False):
        if self.isPrivate(channel):
            messageText = '{0} {1}'.format(random.sample(self._HI), user)
            self._postMessage(messageText=messageText, channel=channel)

        elif private:
            userMention = self.getMention(user)
            messageText = '{0} {1}'.format(random.sample(self._HI), userMention)
            self._postMessage(messageText=messageText, channel=channel)

        else:
            # TODO generalizzare a tutti
            messageText = '{0} {1}'.format(random.sample(self._HI), 'a tutti')
            self._postMessage(messageText=messageText, channel=channel)

    def hanldeMessage(self, message, user, channel, private):
        if self.isHi(message):
            return self.sayHi(user, channel, private)

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
                print(event)
                if self._isForMe(event):
                    self.handleMessage(
                        message=event.get('text'),
                        user=event.get('user'),
                        channel=event.get('channel'))
        time.sleep(self.delay)
