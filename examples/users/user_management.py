import os
from frameioclient import FrameioClient

def manage_users():
    token = os.getenv("FRAMEIO_TOKEN")
    team_id = "35543cd2-954a-c6ee-4aa1-ce9e19602aa9"

    users_list = [
        "example_2@example.com",
        "example_2@example.com"
    ]

    client = FrameioClient(token)
    client.teams.add_members(team_id, users_list)
    client.teams.remove_members(team_id, users_list)


if __name__ == "__main__":
    manage_users()
