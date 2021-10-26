import os
import pdb
from pprint import pprint
from time import time

from frameioclient import FrameioClient, Utils

client = FrameioClient(os.getenv("FRAMEIO_TOKEN"))


def get_all_children(folder_id):
    assets = [
        chunk
        for chunk in Utils.stream_results(
            f"/assets/{folder_id}/children", client=client
        )
    ]

    for asset in assets:
        print(asset["name"])


if __name__ == "__main__":
    project_id = "2dfb6ce6-90d8-4994-881f-f02cd94b1c81"
    project_info = client.projects.get(project_id)
    root_asset_id = project_info["root_asset_id"]
    get_all_children(root_asset_id)