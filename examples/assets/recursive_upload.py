import os
import mimetypes
import concurrent.futures

from frameioclient import FrameioClient
from pprint import pprint

global file_num
file_num = 0

global file_count
file_count = 0

def create_n_upload(task):
    client=task[0]
    file_p=task[1]
    parent_asset_id=task[2]
    abs_path = os.path.abspath(file_p)
    file_s = os.path.getsize(file_p)
    file_n = os.path.split(file_p)[1]
    file_mime = mimetypes.guess_type(abs_path)[0]
    
    asset = client.create_asset(
      parent_asset_id=parent_asset_id,  
      name=file_n,
      type="file",
      filetype=file_mime,
      filesize=file_s
    )
    
    with open(abs_path, "rb") as ul_file:
        asset_info = client.upload(asset, ul_file)
    
    return asset_info


def create_folder(folder_n, parent_asset_id):
    asset = client.create_asset(
      parent_asset_id=parent_asset_id,  
      name=folder_n,
      type="folder",
    )
    
    return asset['id']


def file_counter(root_folder):
    matches = []
    for root, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            matches.append(os.path.join(filename))

    return matches


def recursive_upload(client, folder, parent_asset_id):
    # Seperate files and folders:
    file_list = list()
    folder_list = list()

    for item in os.listdir(folder):
        if item == ".DS_Store": # Ignore .DS_Store files on Mac
            continue

        complete_item_path = os.path.join(folder, item)

        if os.path.isfile(complete_item_path):
            file_list.append(item)
        else:
            folder_list.append(item)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for file_p in file_list:
            global file_num
            file_num += 1
            print(f"Starting {file_num}/{file_count}")
            complete_dir_obj = os.path.join(folder, file_p)
            task = (client, complete_dir_obj, parent_asset_id)
            executor.submit(create_n_upload, task)

    for folder_i in folder_list:
        new_folder = os.path.join(folder, folder_i)
        new_parent_asset_id = create_folder(folder_i, parent_asset_id)
        recursive_upload(client, new_folder, new_parent_asset_id)


if __name__ == "__main__":
    root_folder = "./test_structure"
    parent_asset_id = "PARENT_ASSET_ID"
    client = FrameioClient(os.getenv("FRAME_IO_TOKEN"))

    file_count = len(file_counter(root_folder))
    recursive_upload(client, root_folder, parent_asset_id)