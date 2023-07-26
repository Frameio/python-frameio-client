import csv
import time
from itertools import islice
from pathlib import Path
from re import split
from typing import Dict, List, Tuple

from dotenv import dotenv_values, find_dotenv
from frameioclient import FrameioClient
from requests.exceptions import HTTPError
from tqdm import tqdm

dotenv_path = find_dotenv()
env = dotenv_values(Path(dotenv_path))

FRAMEIO_TOKEN = env["FRAMEIO_TOKEN"]
fio_client = FrameioClient(FRAMEIO_TOKEN)


def split_seq(iterable, size):
    it = iter(iterable)
    item = list(islice(it, size))
    while item:
        yield item


def purge_projects(team_id):
    # Get projects
    projects_list = fio_client.teams.list_projects(team_id)
    for project in projects_list:
        fio_client._api_call("DELETE", f"/projects/{project['id']}")


def purge_projects_from_csv(csv_path: str):
    with open(csv_path, "r") as project_list:
        for row in csv.reader(project_list):
            if row[0] == "id":
                continue
            try:
                fio_client._api_call("DELETE", f"/projects/{row[0]}")
                print(f"Deleted: {row[1]}")
            except Exception as e:
                print(e)

            # Sleeping so as not to run amuck of rate limits
            time.sleep(1)

    return True


def batch_disable_presentations(csv_path):
    fio_client = FrameioClient(FRAMEIO_TOKEN)
    with open(csv_path, "r") as project_list:
        for row in csv.reader(project_list):
            if row[0] == "id":
                continue
            try:
                fio_client._api_call("DELETE", f"/presentations/{row[0]}")
                print(f"Deleted: {row[1]}")
            except Exception as e:
                print(e)

            # Sleeping so as not to run amuck of rate limits
            time.sleep(3)

    return True


def batch_update_labels(asset_list: List, new_label: str) -> Dict:
    """Updates the labels for a list of assets using the batch update endpont

    Args:
        asset_list (List): List of Frame.io Asset IDs
        new_label (str): New Label to be applied

    Returns:
        bool: True or false for whether or not they all updated correctly
    """
    fio_client = FrameioClient(FRAMEIO_TOKEN)
    batch_ops = list()
    all_successful = True

    for batch in split_seq(
        asset_list, 50
    ):  # Split into batches of 50 because that's the limit
        for asset_id in batch:  # Iterate over the items in each batch
            batch_ops.append({"id": asset_id, "label": new_label})

        update_payload = {"batch": batch_ops}

        try:
            fio_client._api_call("POST", f"/batch/assets/label", payload=update_payload)
        except Exception as e:
            all_successful = False

    return all_successful


def batch_delete_assets(csv_path, token: str):
    fio_client = FrameioClient(token)

    # Write header row
    csv_columns = ["timestamp", "asset_id", "error"]
    with open("deletion_results.csv", "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=csv_columns)
        writer.writeheader()

    asset_ids = []  # Real list rather than CSV
    start_pos = 798  # Start position in CSV

    # Read from CSV into a list so that we can slice the list if needed
    with open(csv_path, "r") as asset_list:
        for row in csv.reader(asset_list):
            asset_ids.append(row[0])

    # Iterate over asset_ids
    for row in asset_ids:
        print(row)
        try:
            fio_client.assets.delete(row)
            print(f"Deleted: {row}")
        except HTTPError as e:
            if e.response.status_code == 403 or e.response.status_code == 400:
                data = {
                    "timestamp": time.time(),
                    "asset_id": row,
                    "error": e.response.status_code,
                }
                with open("deletion_results.csv", "a") as outfile:
                    csv_writer = csv.DictWriter(outfile, fieldnames=csv_columns)
                    csv_writer.writerow(data)

                    # Sleeping so as not to run amuck of rate limits
                    time.sleep(1.25)

            elif e.response.status_code == 404:
                print(f"Asset: {row} already deleted")
                continue

            else:
                continue

    return True


def batch_remove_users(team_id: str, csv_path: str):
    users = []  # Real list rather than CSV
    start_pos = 798  # Start position in CSV

    # Read from CSV into a list so that we can slice the list if needed
    with open(csv_path, "r") as asset_list:
        for row in csv.reader(asset_list):
            users.append(row[0])

    # Iterate over asset_ids
    for row in split_seq(users):
        fio_client.teams.remove_members(team_id, row)


if __name__ == "__main__":
    # batch_update_labels(test_list, "in_progress")
    # batch_remove_users("csv_file_1.csv")
    # batch_delete_assets("csv_file_2.csv")

    # csv_path_1 = "/Users/jeff/Downloads/csv_file_1.csv"
    # csv_path_2 = "/Users/jeff/Downloads/csv_file_2.csv"
