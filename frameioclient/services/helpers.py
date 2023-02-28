import os

from pathlib import Path
from time import time, sleep

from ..lib.service import Service
from ..lib.utils import Utils

from copy import deepcopy
from typing import List
from pprint import pprint


class FrameioHelpers(Service):
    def get_updated_assets(self, account_id, project_id, timestamp):
        """
        Get assets added or updated since timestamp.

        :Args:
          account_id (string): The account id.
          project_id (string): The project id.
          timestamp (string): ISO 8601 UTC format.
          (datetime.now(timezone.utc).isoformat())
        """
        payload = {
            "account_id": account_id,
            "page": 1,
            "page_size": 50,
            "include": "children",
            "sort": "-inserted_at",
            "filter": {
                "project_id": {"op": "eq", "value": project_id},
                "updated_at": {"op": "gte", "value": timestamp},
            },
        }
        endpoint = "/search/library"
        return self.client._api_call("post", endpoint, payload=payload)

    def get_assets_recursively(self, asset_id, slim=True):
        assets = self.client.assets.get_children(asset_id, slim=slim)
        print("Number of assets at top level", len(assets))

        for asset in assets:
            # try:
            print(
                f"Type: {asset['_type']}, Name: {asset['name']}, Children: {len(asset['children'])}"
            )
            # except KeyError:
            # 	print("No children found")

            total_bytes = 0

            if asset["_type"] == "file":
                # Don't do nothing, it's a file!
                continue

            if asset["_type"] == "version_stack":
                print("Grabbing top item from version stack")
                versions = self.client.assets.get_children(asset["id"], slim=True)
                asset = versions[0]  # re-assign on purpose
                continue

            # We only get the first three items when we use "include=children"
            if asset["_type"] == "folder":
                # try:
                if asset["item_count"] > 3:
                    # Recursively fetch the contents of the folder because we have to
                    asset["children"] = self.get_assets_recursively(asset["id"], slim)
                    print("Grabbed more items for this sub dir")

                else:
                    for i in asset["children"]:
                        # If a folder is found, we still need to recursively search it
                        if i["_type"] == "folder":
                            i["children"] = self.get_assets_recursively(i["id"], slim)

                # except KeyError as e:
                # 	# No children found in this folder, move on
                # 	print(e)
                # 	continue

        return assets

    def build_project_tree(self, project_id, slim=True):
        # if slim == True:
        # 	self.client.assets.get_children()

        # Get project info
        project = self.client.projects.get(project_id)

        # Get children
        initial_tree = self.get_assets_recursively(project["root_asset_id"], slim)

        return initial_tree

    def download_project(self, project_id, destination):
        project = self.client.projects.get(project_id)
        initial_tree = self.get_assets_recursively(project["root_asset_id"])
        self.recursive_downloader(destination, initial_tree)
        # pprint(initial_tree)
        # print(f"Downloading {Utils.format_bytes(total_bytes, type='size')}")

    def recursive_downloader(self, directory, asset, count=0):
        print(f"Directory {directory}")

        try:
            # First check to see if we need to make the directory
            target_directory = os.path.join(os.path.curdir, directory)
            if not os.path.isdir(target_directory):
                os.mkdir(os.path.abspath(target_directory))

        except Exception as e:
            target_directory = os.path.abspath(os.path.join(os.path.curdir, directory))
            print(e)

        if type(asset) == list:
            for i in asset:
                self.recursive_downloader(directory, i)

        else:
            try:
                if asset["_type"] == "folder":
                    if len(asset["children"]) >= 0:
                        count += 1
                        # Create the new folder that these items will go in before it's too late
                        if not os.path.exists(
                            os.path.join(target_directory, asset["name"])
                        ):
                            print("Path doesn't exist")
                            new_path = Path(
                                target_directory, str(asset["name"]).replace("/", "-")
                            )
                            print(new_path.absolute)
                            print("Making new directory")
                            Path.mkdir(new_path)
                            sleep(2)

                        # Pass along the new directory they'll be living in and the children
                        self.recursive_downloader(
                            f"{directory}/{str(asset['name']).replace('/', '-')}",
                            asset["children"],
                        )

                if asset["_type"] == "file":
                    count += 1
                    return self.client.assets.download(
                        asset, target_directory, multi_part=True
                    )

            except Exception as e:
                print(e)

        return True


if __name__ == "__main__":
    pass
