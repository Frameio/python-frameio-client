import os
from frameioclient import FrameioClient

token = os.getenv("FRAMEIO_TOKEN")

users_list = [
    "example_2@example.com",
    "example_2@example.com"
]

team_id = "35543cd2-954a-c6ee-4aa1-ce9e19602aa9"

client = FrameioClient(token)
client.teams.add_members(team_id, users_list)
client.teams.remove_members(team_id, users_list)
