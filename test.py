import os, slackclient

if __name__ == '__main__':

    botNameVar = 'AIMBOT_SLACK_NAME'
    botTokenVar = 'AIMBOT_SLACK_TOKEN'

    botName = os.environ.get(botNameVar)
    botToken = os.environ.get(botTokenVar)
    # initialize slack client
    client = slackclient.SlackClient(botToken)
    # check if everything is alright
    print(botName)
    print(botToken)
    isOk = client.api_call("users.list").get('ok')
    print(isOk)

    if(isOk):
        for user in client.api_call("users.list").get('members'):
            if user.get('name') == botName:
                print(user.get('id'))
