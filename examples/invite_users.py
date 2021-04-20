import os
from frameioclient import FrameioClient


def get_team_list(account_id):
    token = os.getenv('FRAMEIO_TOKEN')
    client = FrameioClient(token, host='https://api.frame.io')
    pass


def invite_users():
    pass


if __name__ == "__main__":
    invite_users()