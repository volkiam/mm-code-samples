# Samples of code to use mattermost REST API 

import requests, json
from requests import Response
import csv

with open('config.json', 'r') as f:
    config = json.load(f)

# Read config
server_url = config["server_url"]
MATTERMOST_CHANNEL_ID =config["channel_id"]
username = config["bot_username"]
password =config["bot_password"]

# Set Vars
MATTERMOST_API_URL = f'https://{server_url}/api/v4'

# Get session token
def get_session_token (main_url, username, password):
    headers = {
        'Content-Type': 'application/json'
        }
    payload = {
               'login_id': username, 
               'password': password
               }
    url = f'{main_url}/users/login'
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200,201]:
        token = response.headers["token"]
    else:
        token = ""
        print(f'Error within get session token. Error: {response.status_code}')
    return token


# Get user_id
def get_user_id (main_url, token,email):
    headers = {
        "Authorization": "Bearer " + token,
        'Accept': "application/scim+json; charset=UTF-8"
    }
    url = f'{main_url}/users/email/{email}'
    response = requests.get(url, headers=headers)
    if response.status_code in [200,201]:
        user_id = response.json()["id"]  
    else:
        user_id = ""
        print(f'Error within get user_id. Error: {response.status_code}')
    return  user_id

# Add user into channel
def add_member (main_url, token, channel_id, user_id):
    headers = {
        "Authorization": "Bearer " + token,
        'Content-Type': 'application/json'
        }
    payload = {
               'user_id': user_id
               }
    url = f'{main_url}/channels/{channel_id}/members'
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code


def main() -> None:
    """main"""
    token = get_session_token(MATTERMOST_API_URL, username, password)

    result = get_session_token2 ()

    with open('users.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                email = row[1] 
                user_id = get_user_id(MATTERMOST_API_URL, token, email)

                result = add_member(MATTERMOST_API_URL, token, MATTERMOST_CHANNEL_ID, user_id)   
                if result in [200,201]:
                    print(f'User {row[0]} has been appended to the channel')
                else:
                    print(f'Error: user {row[0]} not appended. Http code: {result}')
                line_count += 1
        print(f'Processed {line_count - 1} lines.')

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('Error: '+ str(e))
        raise