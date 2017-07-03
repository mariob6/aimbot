#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import re

from abstract_handler import AbstracHandler
from message_handler import MessageHandler


class ChatBotHandler(AbstracHandler):

    def __init__(self, botId, botName, client, socket_delay=1):
        self.botId = botId
        self.botName = botName
        self.mention = self.getMention(botId)
        self.client = client
        self.delay = socket_delay
        self.messageHandler = MessageHandler(self.mention)

    def isPrivate(self, event):
        """Checks if private slack channel"""
        return event.get('channel').startswith('D')

    def _isForMe(self, event):
        eventType = event.get('type')

        if not eventType or eventType != 'message' or \
                event.get('user') == self.botId:
            return False

        if self.isPrivate(event):
            return 'private'

        messageText = event.get('text')

        if re.search(str(self.mention), str(messageText)):
            return 'mention'

        if re.search(str(self.botName), str(messageText.lower())):
            return 'name'

    def _postMessage(self, messageText, channel):
        self.client.api_call(
            'chat.postMessage', channel=channel,
            text=messageText, as_user=True)

    def handle(self, message, user, channel, mention):
        privateChannel = channel.startswith('D')
        response = self.messageHandler.handle(
            message, user, mention, privateChannel)
        if response:
            return self._postMessage(response, channel)

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
                if not forMe:
                    continue

                mention = bool(forMe == 'mention')
                print('mention: {0}'.format(mention))
                self.handle(
                    message=event.get('text'),
                    user=event.get('user'),
                    channel=event.get('channel'),
                    mention=mention)
        time.sleep(self.delay)
