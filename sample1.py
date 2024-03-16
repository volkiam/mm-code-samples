# Sample for get all events for user (print message in channels, change status, ..)

from mattermostdriver import Driver
import json 

with open('config.json', 'r') as f:
    config = json.load(f)

bot_username = config['bot_username']
bot_password = config['bot_password']
server_url = config['server_url']
server_port= config['server_port']


def main():
    driver = Driver({'url': server_url, 'login_id': bot_username, 'password': bot_password, 'scheme': 'https', 'port': server_port, 'verify': False}) #if you want to use token you should change password to token variable
    driver.login()
    bot_team = driver.teams.get_team_by_name('team_name')
    # bot_channel = driver.channels.get_channel_by_name(bot_team['id'], 'off-topic')
    # bot_channel_id = bot_channel['id']

    async def my_event_handler(payload):  
        if not payload:
            return
        
        payload = json.loads(payload)
        if 'event' not in payload:
            print("Message contains no event: {}".format(payload))
            return

        event_handlers = {
            'posted': _message_event_handler,
            'hello': _hello_event_handler,
        }

        event = payload['event']
        event_handler = event_handlers.get(event)
        if event_handler is None:
            print("No event handler available for {}, ignoring.".format(event))
            return
        # noinspection PyBroadException
        try:
            event_handler(payload)
        except Exception:
            print("{} event handler raised an exception".format(event))

    def _hello_event_handler(message):
        """Event handler for the 'hello' event"""
        print(f'status=ONLINE')

    def _message_event_handler(message):
        print(message)
        data = message['data']

        # In some cases (direct messages) team_id is an empty string
        if data['team_id'] != ''and bot_team['id'] != data['team_id']:
            print("Message came from another team ({}), ignoring...".format(data['team_id']))
            return

        broadcast = message['broadcast']

        if 'channel_id' in data:
            channelid = data['channel_id']
        elif 'channel_id' in broadcast:
            channelid = broadcast['channel_id']
        else:
            print("Couldn't find a channelid for event {}".format(message))
            return

        channel_type = data['channel_type']

        if channel_type != 'D':
            channel = data['channel_name']
        else:
            channel = channelid


        text = ''
        post_id = ''
        file_ids = None
        userid = None


        if 'post' in data:
            post = json.loads(data['post'])
            text = post['message']
            userid = post['user_id']
            if 'file_ids' in post:
                file_ids = post['file_ids']
            post_id = post['id']
            if 'type' in post and post['type'] == 'system_add_remove':
                print("Ignoring message from System")
                return

        if 'user_id' in data:
            userid = data['user_id']

        if not userid:
            print('No userid in event {}'.format(message))
            return

        # Thread root post id
        root_id = post.get('root_id')
        if root_id is '':
            root_id = post_id


        if text == 'hello bot':
            driver.posts.create_post({
                'channel_id': channelid,
                'message': 'Hi there!'
            })
            
        print(f'Message text: {text}, userid: {userid}, channel: {channel}, post_id: {post_id}, file_ids: {file_ids}')

    driver.init_websocket(my_event_handler)

if __name__ == '__main__':
    main()