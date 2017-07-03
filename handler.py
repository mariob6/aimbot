#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import re

""" API import """
import os.path
import sys
import json
try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

import string



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
        self.CLIENT_API_TOKEN = '74399e8cbf7a440fbc751e043b97f798'


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

        if re.search(self.mention, messageText):
            return 'mention'

        if re.search(self.botName, messageText):
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

    def _normalizeText(self, messageText):
        translator = str.maketrans(' ', ' ', string.punctuation)
        messageText = messageText.translate(translator).lower()
        space = " "
        for key in ['\n', '\t']:
            messageText = messageText.replace(key, space)

        return " ".join(filter(None, messageText.strip().split(space)))

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

    def answerApi(self, text, user, channel):
        answer = ""
        ai = apiai.ApiAI(self.CLIENT_API_TOKEN)
        proper_text = text.replace(self.mention, "")
        print('API.AI. Testo: {0}'.format(proper_text))
        request = ai.text_request()
        request.lang = 'it'
        request.session_id = str(user) + str(time.time()).split('.')[0]
        request.query = proper_text
        response = json.loads(request.getresponse().read())
        print(response)
        answer = response['result']['fulfillment']['speech']
        print('anser api:' + answer)
        if len(answer) > 0:
            self._postMessage(messageText=answer, channel=channel)
            return(True)

    def handleMessage(self, message, user, channel, mention):
        if self.isHi(message=message):
            print('isHi')
            return self.sayHi(user, channel, mention)
        elif self.isInsult(message=message):
            print('isInsult')
            return self.sayInsult(user, channel, mention)
        elif self.answerApi(message, user, channel):
            print('answer api')
        else:
            # FALLBACK
            self._postMessage(messageText='Spacco botilia ammazzo familia', channel=channel)

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
                print('forMe: {0}. Event type: {1}'.format(forMe, event.get('type')))
                if forMe:
                    mention = bool(forMe == 'mention')
                    print('mention: {0}'.format(mention))
                    self.handleMessage(
                        message=self._normalizeText(event.get('text')),
                        user=event.get('user'),
                        channel=event.get('channel'),
                        mention=mention)
        time.sleep(self.delay)
