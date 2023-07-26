import os

from time import time
from pprint import pprint
from frameioclient import FrameioClient
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

def demo_folder_tree(project_id):
    TOKEN = os.getenv("FRAMEIO_TOKEN")
    client = FrameioClient(TOKEN)

    start_time = time()
    tree = client.helpers.build_project_tree(project_id, slim=True)

    end_time = time()
    elapsed = round((end_time - start_time), 2)

    item_count = len(tree)
    pprint(tree)

    print(f"Found {item_count} items")
    print(f"Took {elapsed} second to fetch the slim payload for project: {project_id}")
    print("\n")

if __name__ == "__main__":
    # project_id = 'ba1791e8-bf1e-46cb-bcad-5e4bb6431a08'
    # project_id = 'f37bc51c-fec1-438d-8ccf-6a88ebd82146'
    project_id = 'ceb229b1-bd23-4543-832e-afa0b2151000'
    demo_folder_tree(project_id)
