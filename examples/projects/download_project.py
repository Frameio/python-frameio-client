from frameioclient.lib.utils import FormatTypes, Utils
import os
from pathlib import Path

import pdb
from time import time,sleep
from pprint import pprint
from frameioclient import FrameioClient

def get_folder_size(path='.'):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_folder_size(entry.path)
    return total

def demo_project_download(project_id):
	TOKEN = os.getenv("FRAMEIO_TOKEN")
	client = FrameioClient(TOKEN)

	start_time = time()
	download_dir = '/Volumes/Jeff-EXT/Python Transfer Test'
	item_count = client.projects.download(project_id, destination_directory=download_dir)

	# item_count = client.projects.download(project_id, destination_directory='/Users/jeff/Temp/Transfer vs Python SDK/Python SDK')

	end_time = time()
	elapsed = round((end_time - start_time), 2)

	
	folder_size = get_folder_size(download_dir)
	# pdb.set_trace()

	print(f"Found {item_count} items")
	print(f"Took {elapsed} second to download {Utils.format_value(folder_size, type=FormatTypes.SIZE)} for project: {client.projects.get(project_id)['name']}")
	print("\n")

if __name__ == "__main__":
	# project_id = '2dfb6ce6-90d8-4994-881f-f02cd94b1c81'
	# project_id='e2845993-7330-54c6-8b77-eafbd5144eac'
	# project_id = '5d3ff176-ab1f-4c0b-a027-abe3d2a960e3'
	project_id = 'ba1791e8-bf1e-46cb-bcad-5e4bb6431a08'
	demo_project_download(project_id)

# Took 443.84 second to download 12.43 GB to USB HDD for project: HersheyPark Summer Campaign using Python SDK