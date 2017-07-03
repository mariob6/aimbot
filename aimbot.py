import os
import slackclient
from chatbot_handler import ChatBotHandler
# delay in seconds before checking for new events

botNameVar = 'AIMBOT_SLACK_NAME'
botTokenVar = 'AIMBOT_SLACK_TOKEN'
botIdVar = 'AIMBOT_SLACK_ID'

botName = os.environ.get(botNameVar)
botToken = os.environ.get(botTokenVar)
botId = os.environ.get(botIdVar)


if __name__ == '__main__':
    client = slackclient.SlackClient(botToken)
    handler = ChatBotHandler(botId, botName, client)
    handler.run()
