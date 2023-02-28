import os
from frameioclient import FrameioClient


def get_team_list(account_id):
    token = os.getenv('FRAMEIO_TOKEN')
    client = FrameioClient(token)

    return client.teams.list_all('account_id')


def invite_users():
    token = os.getenv('FRAMEIO_TOKEN')
    client = FrameioClient(token)

    user_list = [
        "janedoe@frame.io",
        "johndoe@frame.io"
    ]

    client.teams.add_members('team_id', user_list)


if __name__ == "__main__":
    invite_users()