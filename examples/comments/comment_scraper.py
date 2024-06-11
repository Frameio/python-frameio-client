###################################
# This scraper shows you how to gather comments from
# a Frame.io project and write to a tidy CSV.
# Comments are gathered recursively from the 
# Folders, files and version stacks within your project.
###################################


import csv
import os
from itertools import chain

from frameioclient import FrameioClient

class ClientNotTokenized(Exception):
    pass


class RootAssetIDNotFound(Exception):
    pass


def build_comments_list(client, asset_id, comment_list):
    """
    Takes an initialized client, recursively builds a list of comments
    and returns the list. (Technically, it's a list of dicts)
    """
    assets = client.assets.get_children(asset_id)

    for asset in assets:
        # Recurse through folders but skip the empty ones
        if (asset.get('type') == 'folder') and (asset.get('item_count') > 0):
            build_comments_list(client, asset['id'], comment_list)

        if asset.get('type') == 'file' and asset.get('comment_count') > 0:
            comments = client.comments.list(asset['id'])
            for comment in comments:
                # The 'get_comments" call won't return the asset name
                # So we'll add it to the dictionary now.
                comment['asset'] = { 'name': asset['name'] }
                comment_list.append(comment)

        if asset.get('type') == 'version_stack':
            # Read about version stacks: https://docs.frame.io/docs/managing-version-stacks
            versions = client.assets.get_children(asset['id'])
            for v_asset in versions:
                comments = client.comments.list(v_asset['id'])
                for comment in comments:
                    comment['asset'] = { 'name': asset['name'] }
                    comment_list.append(comment)

    return comment_list


def flatten_dict(d):
    # The get_comments API response is verbose and contains nested objects.
    # Use this helper functon to flatten the dict holding the API response data
    # and namespace the attributes.

    def expand(key, val):
            if isinstance(val, dict):
                return [ (key + '.' + k, v) for k, v in flatten_dict(val).items() ]
            else:
                return [ (key, val) ]
    
    items = [ item for k, v in d.items() for item in expand(k, v)]

    return dict(items)


def write_comments_csv(c_list):
    # Writes comments to comments.csv
    # Any attributes you add to the headers list will automatically be written to the CSV
    # The API returns many attributes so familiarize yourself with the response data: https://docs.frame.io/reference#getcomments
    headers = ['text', 'inserted_at', 'timestamp', 'has_replies', 'parent_id', 'asset.name', 'asset_id', 'owner.name', 'owner.email', 'owner_id', 'owner.account_id']

    # Flattening the comments dicts is not at all necessary, but the namespacing
    # makes the CSV headers much more readable.
    flat_comments_list = []
    for c in c_list:
        flat_comments_list.append(flatten_dict(c))

    with open('comments.csv', 'w') as file:
        f_csv = csv.DictWriter(file, headers, extrasaction='ignore')
        f_csv.writeheader()
        f_csv.writerows(flat_comments_list)


if __name__ == '__main__':

    TOKEN = os.getenv('FRAME_IO_TOKEN')
    if os.environ.get('FRAME_IO_TOKEN') == None:
        raise ClientNotTokenized('The Python SDK requires a valid developer token.')
    ROOT_ASSET_ID = os.getenv('ROOT_ASSET_ID')
    if os.environ.get('ROOT_ASSET_ID') == None:
        raise RootAssetIDNotFound('If you don\'t know what Root Asset ID is, read this guide: https://docs.frame.io/docs/root-asset-ids')

    # Initialize the client library
    client = FrameioClient(TOKEN)

    # Build the comments list
    comments = []
    comments_list = build_comments_list(client, ROOT_ASSET_ID, comments)

    # Write the comments to comments.csv
    write_comments_csv(comments_list)
