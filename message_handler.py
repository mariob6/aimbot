import os.path
import json
import random
import sys
import string
import time
from abstract_handler import AbstracHandler

""" API import """

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai


class MessageHandler(AbstracHandler):

    _HI = ['ciao', 'ciaone', 'bella', 'hey']

    _INSULT = ['coglione', 'ricchione', 'stronzo', 'frocio', 'merda', 'cesso',
               'gay', 'idiota', 'imbecille', 'pure tu']

    def __init__(self, mention):
        self.mention = mention
        self.CLIENT_API_TOKEN = '958998f497d34a4d8555fecafd265f28'

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

    def _normalizeText(self, messageText):
        translator = str.maketrans(' ', ' ', string.punctuation)
        messageText = messageText.translate(translator).lower()
        space = " "
        for key in ['\n', '\t']:
            messageText = messageText.replace(key, space)

        return " ".join(filter(None, messageText.strip().split(space)))

    def sayHi(self, user, mention, privateChannel):
        """In private channel: say Hi + username
        In public: say Hi + username if mention else Hi everybody"""
        if privateChannel:
            mention = False
            messageText = self._decorateMessage(
                user, random.choice(self._HI), mention=mention, front=False)
        elif mention:
            messageText = self._decorateMessage(
                user, random.choice(self._HI), mention=mention, front=False)
        else:
            messageText = self._decorateMessage(
                user, random.choice(self._HI), toChannel=True)

        return messageText

    def sayInsult(self, user, mention, privateChannel):
        if privateChannel or not mention:
            mention = False
            messageText = self._decorateMessage(
                user, random.choice(self._INSULT), mention=mention)
        elif mention:
            messageText = self._decorateMessage(
                user, random.choice(self._INSULT), mention=mention)

        return messageText

    def answerApi(self, text, user):
        answer = ""
        ai = apiai.ApiAI(self.CLIENT_API_TOKEN)
        proper_text = text.replace(self.mention, "")
        print('API.AI. Testo: {0}'.format(proper_text))
        request = ai.text_request()
        request.lang = 'it'
        request.session_id = str(user) + str(time.time()).split('.')[0]
        request.query = proper_text
        response = json.loads(request.getresponse().read().decode('utf-8'))
        answer = response \
            .get('result', {}) \
            .get('fulfillment', {}) \
            .get('speech', None)

        print('anser api:' + answer)
        return answer

    def classifyIntent(self, message):
        for token in message.split(" "):
            if token in self._HI:
                return 'hi'

            elif token in self._INSULT:
                return 'insult'

        return 'ApiAi'

    def answerFromIntent(self, intent, user, mention, privateChannel, message):
        if intent == 'hi':
            return self.sayHi(user, mention, privateChannel)
        elif intent == 'insult':
            return self.sayInsult(user, mention, privateChannel)
        else:
            answer = self.answerApi(message, user)
            if not answer:
                return('Spacco botilia ammazzo familia')

            return answer

    def handle(self, message, user, mention, privateChannel=False):
        message = self._normalizeText(message)
        intent = self.classifyIntent(message)

        return self.answerFromIntent(
            intent, user, mention, privateChannel, message)
