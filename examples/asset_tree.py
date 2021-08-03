import os

import pdb
from time import time
from pprint import pprint
from frameioclient import FrameioClient

def demo_folder_tree(project_id, slim):
	TOKEN = os.getenv("FRAMEIO_TOKEN")
	client = FrameioClient(TOKEN)

	start_time = time()
	tree = client.projects.tree(project_id, slim)

	end_time = time()
	elapsed = round((end_time - start_time), 2)

	item_count = len(tree)
	pprint(tree)
	# pdb.set_trace()

	print(f"Found {item_count} items")
	print(f"Took {elapsed} second to fetch the slim payload for project: {project_id}")
	print("\n")

if __name__ == "__main__":
	project_id = '2dfb6ce6-90d8-4994-881f-f02cd94b1c81'
	# project_id='e2845993-7330-54c6-8b77-eafbd5144eac'
	demo_folder_tree(project_id, slim=True)
	# demo_folder_tree(project_id, slim=False)

# 445 seconds for slim
# 509 seconds for non-slim