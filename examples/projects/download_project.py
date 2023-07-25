import os
from time import time

from dotenv import find_dotenv, load_dotenv
from frameioclient import FrameioClient
from frameioclient.lib.utils import FormatTypes, Utils

load_dotenv(find_dotenv())

def get_folder_size(path: str = '.'):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_folder_size(entry.path)
    return total

def demo_project_download(project_id: str, download_dir: str):
    TOKEN = os.getenv("FRAMEIO_TOKEN")
    client = FrameioClient(TOKEN)

    project_info = client.projects.get(project_id)

    start_time = time()
    downloaded_item_count = client.projects.download(project_id, destination_directory=download_dir)

    end_time = time()
    elapsed = round((end_time - start_time), 2)

    folder_size = get_folder_size(download_dir)

    print(f"Found {downloaded_item_count} items to download in the in the {project_info['name']} project")
    print(f"Took {elapsed} second to download {Utils.format_value(folder_size, type=FormatTypes.SIZE)} for project: {project_info['name']}")
    print("\n")

if __name__ == "__main__":
    project_id = 'bb4d6293-514b-4097-a9aa-792d91916414'

    destination_dir = '/Users/jeff/Movies/Assets/temp/Python SDK Test'
    demo_project_download(project_id, destination_dir)