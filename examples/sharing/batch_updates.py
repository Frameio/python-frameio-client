import csv
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import dotenv_values, find_dotenv
from tqdm import tqdm

from frameioclient import FrameioClient

dotenv_path = find_dotenv('/Users/jeff/Code/devrel/python-frameio-client/.env')
env = dotenv_values(Path(dotenv_path))

FRAMEIO_TOKEN = env["FRAMEIO_TOKEN"]
fio_client = FrameioClient(FRAMEIO_TOKEN)

# Gets or creates a logger
logger = logging.getLogger(__name__)  

# set log level
logger.setLevel(logging.INFO)

# define file handler and set formatter
file_handler = logging.FileHandler('log_file.log')
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)


def grant_access_to_all_teams():
    # 1. Get accounts list
    # 2. Iterate over accounts
    # 3. Fetch all teams in account
    # 4. Add user to each team as a team member
    
    accounts = fio_client._api_call('GET', '/accounts')
    for account in accounts:
        teams = fio_client.teams.list(account['id'])
        for team in teams:
            fio_client.teams.add_members(team['id'], ['user@frame.io'])

    pass


def batch_disable_presentation_links(csv_path):
    with open(csv_path, "r") as project_list:
        for row in csv.reader(project_list):
            if row[0] == "id":
                continue
            try:
                fio_client.presentation_links.update(row[0], enabled=False)
                logger.info(f"Disabled presentation link: {row[0]}")
            except Exception as e:
                print(e)
                logger.error(f"Failed to disable presentation link: {row[0]}")

    return True


def batch_disable_review_links(csv_path):
    with open(csv_path, "r") as review_link_list:
        for row in csv.reader(review_link_list):
            if row[0] == "id":
                continue
            try:
                fio_client.review_links.update_settings(row[0], is_active=False)
                logger.info(f"Disabled review link: {row[0]}")
            except Exception as e:
                print(e)
                logger.error(f"Failed to disable review link: {row[0]}")
            time.sleep(.05)

    return True

def batch_delete_review_links(csv_path):
    with open(csv_path, "r") as review_link_list:
        for row in csv.reader(review_link_list):
            if row[0] == "id":
                continue
            try:
                fio_client._api_call("DELETE", f"/review_links/{row['id']}")
            except Exception as e:
                print(e)
                logger.error(f"Failed to disable review link: {row[0]}")
            time.sleep(.05)

    return True

if __name__ == '__main__':
    presentation_links_csv_path = '/Users/jeff/Code/examples/presentation_links_to_delete.csv'
    review_links_csv_path = '/Users/jeff/Code/devrel/python-frameio-client/fio fio_review_links 2022-12-13T1244.csv'

    batch_disable_presentation_links(presentation_links_csv_path)
    batch_disable_review_links(review_links_csv_path)

    grant_access_to_all_teams()
