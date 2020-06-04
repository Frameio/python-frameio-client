import os
import sys
import json
import mimetypes
import platform
import time

from pprint import pprint
from frameioclient import FrameioClient

token = os.getenv("FRAMEIO_TOKEN")
project_id = os.getenv("PROJECT_ID")
download_asset_id = os.getenv("DOWNLOAD_FOLDER_ID")


# Initialize the client
def init_client():
    if len(token) < 5:
        print("Bad token, exiting test.")
        sys.exit(1)
    
    client = FrameioClient(token)
    print("Client connection initialized.")

    return client

# Test download functionality
def test_download(client):
    print("Testing download function...")
    os.mkdir('downloads')

    asset_list = client.get_asset_children(
        download_asset_id,
        page=1,
        page_size=40,
        include="children"
    )

    print("Downloading {} files.".format(len(asset_list)))
    for asset in asset_list:
        client.download(asset, 'downloads')

    print("Done downloading files")

    return True

# Test upload functionality       
def test_upload(client):
    print("Beginning upload test")
    # Create new parent asset
    project_info = client.get_project(project_id)
    root_asset_id = project_info['root_asset_id']
    
    print("Creating new folder to upload to")
    new_folder = client.create_asset(
            parent_asset_id=root_asset_id,  
            name="Python {} Upload Test".format(platform.python_version()),
            type="folder",
        )
    
    new_parent_id = new_folder['id']

    print("Folder created, id: {}".format(new_parent_id))

    # Upload all the files we downloaded earlier
    dled_files = os.listdir('downloads')

    for count, fn in enumerate(dled_files, start=1):
        print("Uploading {}".format(fn))
        abs_path = os.path.join(os.curdir, 'downloads', fn)
        filesize = os.path.getsize(abs_path)
        filename = os.path.basename(abs_path)
        filemime = mimetypes.guess_type(abs_path)[0]

        asset = client.create_asset(
            parent_asset_id=new_parent_id,  
            name=filename,
            type="file",
            filetype=filemime,
            filesize=filesize
        )

        with open(abs_path, "rb") as ul_file:
            client.upload(asset, ul_file)
    
        print("Done uploading file {} of {}".format((count), len(dled_files)))

    print("Sleeping for 5 seconds to allow uploads to finish...")
    time.sleep(5)

    print("Continuing...")

    return new_parent_id

# Flatten asset children and pull out important info for comparison
def flatten_asset_children(asset_children):
    flat_dict = dict()

    for asset in asset_children:
        try:
            size_name = "{}-{}".format(asset['name'], 'size')
            flat_dict[size_name] = asset['filesize']

            xxhash_name = "{}-{}".format(asset['name'], 'xxHash')
            flat_dict[xxhash_name] = asset['checksums']['xx_hash']
        except TypeError:
            continue

    return flat_dict


def check_for_checksums(asset_children):
    for i in range(10):
        while i <= 10:
            for asset in asset_children:
                try:
                    asset['checksums']['xx_hash']
                    print("Success..")
                    print("Checksum dict: ")
                    pprint(asset['checksums'])
                    print("\n")
                except TypeError:
                    print("Failure...")
                    print("Checksum dict \n")
                    pprint(asset['checksums'])
                    print("Asset ID: {}".format(asset['id']))
                    print("Asset Name: {}".format(asset['name']))
                    print("Checksums not yet calculated, sleeping for 10 seconds.")
                    time.sleep(5)
                    i += 1
                    continue

    return True

def check_upload_completion(client, download_folder_id, upload_folder_id):
    # Do a comparison against filenames and filesizes here to make sure they match

    print("Beginning upload comparison check")

    # Get asset children for download folder
    dl_asset_children = client.get_asset_children(
        download_folder_id,
        page=1,
        page_size=40,
        include="children"
    )

    print("Got asset children for original download folder")

    # Get asset children for upload folder
    ul_asset_children = client.get_asset_children(
        upload_folder_id,
        page=1,
        page_size=40,
        include="children"
    )

    print("Got asset children for uploaded folder")

    print("Making sure checksums are calculated before verifying")
    check_for_checksums(ul_asset_children)

    dl_items = flatten_asset_children(dl_asset_children)
    ul_items = flatten_asset_children(ul_asset_children)

    print("Valid uploads: {}/{}".format(len(ul_items), len(dl_items)))
    print("Percentage uploads valid: {:.2%}".format(len(ul_items)/len(dl_items)))

    print("Running comparison...")

    print("DL Items: \n")
    pprint(dl_items)

    print("\nUL Items: \n")
    pprint(ul_items)

    if sys.version_info.major >= 3:
        import operator
        comparison = operator.eq(dl_items, ul_items)
        
        if comparison == False:
            print("File mismatch between upload and download")
            sys.exit(1)

    else:
        # Use different comparsion function in < Py3
        comparison = cmp(dl_items, ul_items)
        if comparison != 0:
            print("File mismatch between upload and download")
            sys.exit(1)

    print("Integration test passed!!!")

    return True


def clean_up(client, asset_to_delete):
    print("Removing files from test...")

    try:
        client._api_call('delete', '/assets/{}'.format(asset_to_delete))
        print("Managed to cleanup!")
    except Exception as e:
        print(e)

    return True

def run_test():
    print("Beginning Integration test...")

    client = init_client()
    test_download(client)
    upload_folder_id = test_upload(client)
    check_upload_completion(client, download_asset_id, upload_folder_id)
    clean_up(client, upload_folder_id)

    print("Test complete, exiting...")

if __name__ == "__main__":
    run_test()
