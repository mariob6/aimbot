import os, slackclient, time
import random
import websocket

# delay in seconds before checking for new events
SOCKET_DELAY = 1


botNameVar = 'AIMBOT_SLACK_NAME'
botTokenVar = 'AIMBOT_SLACK_TOKEN'
botIdVar = 'AIMBOT_SLACK_ID'

botName = os.environ.get(botNameVar)
botToken = os.environ.get(botTokenVar)
botID = os.environ.get(botIdVar)

client = slackclient.SlackClient(botToken)


def is_private(event):
    """Checks if private slack channel"""
    return event.get('channel').startswith('D')


def is_for_me(event):
    # TODO Implement later
    return True


def handle_message(message, user, channel):
    # TODO Implement later
    post_message(message='Buonaseeraaa', channel=channel)

def post_message(message, channel):
    client.api_call('chat.postMessage', channel=channel,
                          text=message, as_user=True)

def run():

        isOk = client.api_call("users.list").get('ok')
        print(isOk)

        websocket.enableTrace(True)
        if  not client.rtm_connect():
            print('[!] Connection to Slack failed.')
            return

        print('[.] AimBot is ON...')
        while True:
            event_list = client.rtm_read()
            if not len(event_list):
                continue

            for event in event_list:
                print(event)
                if is_for_me(event):
                    handle_message(
                        message=event.get('text'),
                        user=event.get('user'),
                        channel=event.get('channel'))
        time.sleep(SOCKET_DELAY)


if __name__=='__main__':
    run()
