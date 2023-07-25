import os
from frameioclient import FrameioClient

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


token = os.getenv("FRAMEIO_TOKEN") # Your Frame.io token
destination_folder_id = "d986681a-e460-4cc6-8db6-bbfbebdb88c7"

def simple_recursive_upload(destination_folder_id: str, source_folder: str):
    client = FrameioClient(token)

    print("Starting upload...")
    client.assets.upload_folder(source_folder, destination_folder_id)


if __name__ == "__main__":
    source_directory = '/Users/jeff/Movies/Assets/images/RAW Images/nikon'

    simple_recursive_upload("d986681a-e460-4cc6-8db6-bbfbebdb88c7", source_directory)
