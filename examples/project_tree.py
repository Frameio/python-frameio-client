import os

from time import time
from pprint import pprint
from frameioclient import FrameioClient

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
	project_id = '2dfb6ce6-90d8-4994-881f-f02cd94b1c81'
	demo_folder_tree(project_id)
