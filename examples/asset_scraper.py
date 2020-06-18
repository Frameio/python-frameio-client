###################################
# This scraper shows you how to gather assets from
# a Frame.io account and write to a CSV.
# Assets are gathered recursively from each 
# team's projects.  Folders, files and version stacks are written to the CSV.
# Note: Debug statements are left in the file and commented out.
###################################


import csv
import os
import time
from itertools import chain

from frameioclient import FrameioClient


class ClientNotTokenized(Exception):
    pass


class RootAssetIDNotFound(Exception):
    pass


def get_teams_from_account(client):
    """
    Builds a list of teams for the account.  Note: the API offers two strategies to fetch an account's teams, 
    `'get_teams`` and `get_all_teams`.  Using `get_teams` we'll pull only the teams owned by the account_id, 
    disregarding teams the user belongs to but does not own.  More info: https://docs.frame.io/docs/directory-lists-and-file-trees#2-fetch-the-accounts-teams
    """
    acct = client.get_me()
    acct_id = acct['account_id']
    return client.get_teams(acct_id)

def get_projects_from_team(client, team):
    """Returns a list of projects for a team."""
    projects_in_team = []
    data = client.get_projects(team.get('id'))
    team_name = team.get('name')

    for proj in data:
        # Add project_name and team_name to the dict
        proj['project_name'] = proj.get('name')
        proj['team_name'] = team_name
        # print('Debug: Found project: {}'.format(proj['project_name']))
        projects_in_team.append(proj)
        # print('Debug: projects in team now {}'.format(len(projects_in_team)))

    return projects_in_team

def get_projects_from_account(client):
    """Gets projects from all teams in the account."""
    projects_in_account = []
    teams = get_teams_from_account(client)

    for team in teams:
        team_name = team.get('name')
        # print('Debug: === Found team: {} ==='.format(team_name))
        projects_in_team = (get_projects_from_team(client, team))
        projects_in_account.extend(projects_in_team)
        # print('Debug: projects in account now: {}'.format(len(projects_in_account)))

    return projects_in_account

def scrape_asset_data_from_projects(client, projects):
    """
    Scrapes the asset data for an authenticated client and provided list of projects.
    Returns a list of asset metadata for all assets contained in the project.
    """
    assets_in_projects = []
    for project in projects:
        assets_in_project = []
        proj_root_asset_id = project.get('root_asset_id')
        assets_in_project = scrape_asset_data(client, proj_root_asset_id, assets_in_project)
        assets_in_projects.extend(assets_in_project)
        # print('Debug: total assets collected from projects: {}'.format(len(assets_in_projects)))
    
        for asset in assets_in_project:
            # TODO: Repeats code from earlier and really shouldn't
            asset['project_name'] = project.get('project_name')
            asset['team_name'] = project.get('name')

    return assets_in_projects


def scrape_asset_data(client, asset_id, asset_list):
    """
    Takes an initialized client and an asset_id representing a position in a directory tree.
    Recursively builds a list of assets within the tree.  Returns a list of dicts.
    """
    assets = client.get_asset_children(asset_id)

    for asset in assets:
        # Recurse through folders but skip the empty ones
        if asset['type'] == "folder" and asset != []:
            # Include non-empty folders in the list of scraped assets
            asset_list.append(asset)
            scrape_asset_data(client, asset['id'], asset_list)

        if asset['type'] == "file":
            asset_list.append(asset)

        if asset['type'] == "version_stack":
            # Read about version stacks: https://docs.frame.io/docs/managing-version-stacks
            versions = client.get_asset_children(asset['id'])
            asset_list.append(asset)
            for v_asset in versions:
                asset_list.append(v_asset)

    return asset_list

def flatten_dict(d):
    """
    Use this helper functon to flatten a dict holding API response data
    and namespace the attributes.  
    """

    def expand(key, val):
            if isinstance(val, dict):
                return [ (key + '.' + k, v) for k, v in flatten_dict(val).items() ]
            else:
                return [ (key, val) ]
    
    items = [ item for k, v in d.items() for item in expand(k, v)]

    return dict(items)

def write_assets_to_csv(asset_list, filename):
    """
    Writes assets to assets.csv
    Any attributes you add to the headers list will automatically be written to the CSV
    The API returns many attributes so familiarize with the response data!
    """
    headers = [
        'id',
        'name', 
        'type',
        'inserted_at',
        'item_count',
        'comment_count',
        'filesize',
        'shared',
        'private',
        'versions',
        'parent_id', 
        'project_name',
        'project_id',
        'team_name',
        'creator.name',
        'creator.email',
    ]

    # Flattening the assets dicts is not necessary but namespaces the CSV headers nicely.
    flat_assets_list = []
    for a in asset_list:
        flat_assets_list.append(flatten_dict(a))

    with open('asset_record_for_account_id-{}'.format(filename), 'w') as f:
        f_csv = csv.DictWriter(f, headers, extrasaction='ignore')
        f_csv.writeheader()
        f_csv.writerows(flat_assets_list)

    return

if __name__ == '__main__':


    TOKEN = os.getenv('FRAME_IO_TOKEN')
    if os.environ.get('FRAME_IO_TOKEN') == None:
        raise ClientNotTokenized('The Python SDK requires a valid developer token.')
    ROOT_ASSET_ID = os.getenv('ROOT_ASSET_ID')
    if os.environ.get('ROOT_ASSET_ID') == None:
        raise RootAssetIDNotFound('If you don\'t know what Root Asset ID is, read this guide: https://docs.frame.io/docs/root-asset-ids')

    # Initialize the client library
    client = FrameioClient(TOKEN)

    # Gather all assets in the account
    projects = get_projects_from_account(client)
    assets_in_account = scrape_asset_data_from_projects(client, projects)

    # Pass a filename to the .csv writer so we can explicitly ID the file
    acct = client.get_me()
    acct_id = acct['account_id']
    filename = 'assets_for_account_id-{}.csv'.format(acct_id)

    # Write the .csv
    write_assets_to_csv(assets_in_account, filename)