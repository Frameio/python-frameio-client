import os
import sys
import json
import time
import socket
import xxhash
import platform
import mimetypes

from math import ceil
from pprint import pprint
from datetime import datetime
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

# Verify local and source
def verify_local(dl_children):
    # Compare remote filenames and hashes

    # Iterate over local directory and get filenames and hashes
    dled_files = os.listdir('downloads')
    for count, fn in enumerate(dled_files):
        print("{}/{} Generating hash for: {}".format(count, len(dled_files), fn))


# Test download functionality
def test_download(client):
    print("Testing download function...")
    if os.path.isdir('downloads'):
        print("Local downloads folder detected...")
        return True
    
    os.mkdir('downloads')

    asset_list = client.get_asset_children(
        download_asset_id,
        page=1,
        page_size=40,
        include="children"
    )

    print("Downloading {} files.".format(len(asset_list)))
    for count, asset in enumerate(asset_list, start=1):
        start_time = time.time()
        print("{}/{} Beginning to download: {}".format(count, len(asset_list), asset['name']))
        
        client.download(asset, 'downloads')
        
        download_time = time.time() - start_time
        download_speed = format_bytes(ceil(asset['filesize']/(download_time)))

        print("{}/{} Download completed in {:.2f}s @ {}".format((count), len(asset_list), download_time, download_speed))

    print("Done downloading files")

    return True

def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'KB/s', 2: 'MB/s', 3: 'GB/s', 4: 'TB/s'}
    while size > power:
        size /= power
        n += 1
    return " ".join((str(round(size, 2)), power_labels[n]))

# Test upload functionality       
def test_upload(client):
    print("Beginning upload test")
    # Create new parent asset
    project_info = client.get_project(project_id)
    root_asset_id = project_info['root_asset_id']
    
    print("Creating new folder to upload to")
    new_folder = client.create_asset(
            parent_asset_id=root_asset_id,  
            name="{}_{}_Py{}_{}".format(socket.gethostname(), platform.system(), platform.python_version(), datetime.now().strftime("%B-%d-%Y")),
            type="folder",
        )
    
    new_parent_id = new_folder['id']

    print("Folder created, id: {}, name: {}".format(new_parent_id, new_folder['name']))

    # Upload all the files we downloaded earlier
    dled_files = os.listdir('downloads')

    for count, fn in enumerate(dled_files, start=1):
        start_time = time.time()
        print("{}/{} Beginning to upload: {}".format(count, len(dled_files), fn))
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

        upload_time = time.time() - start_time
        upload_speed = format_bytes(ceil(filesize/(upload_time)))

        print("{}/{} Upload completed in {:.2f}s @ {}".format((count), len(dled_files), upload_time, upload_speed))

    print("Sleeping for 5 seconds to allow uploads to finish...")
    time.sleep(5)

    print("Continuing...")

    return new_parent_id

# Flatten asset children and pull out important info for comparison
def flatten_asset_children(asset_children):
    flat_dict = dict()

    for asset in asset_children:
        try:
            xxhash_name = "{}_{}".format(asset['name'], 'xxHash')
            flat_dict[xxhash_name] = asset['checksums']['xx_hash']
        except TypeError:
            xxhash_name = "{}_{}".format(asset['name'], 'xxHash')
            flat_dict[xxhash_name] = "missing"

            continue

    return flat_dict

def check_for_checksums(asset_children):
    for asset in asset_children:
        try:
            asset['checksums']['xx_hash']
            print("Success..")
            print("Asset ID: {}".format(asset['id']))
            print("Asset Name: {}".format(asset['name']))
            print("Checksum dict: {}".format(asset['checksums']))
        except TypeError as e:
            print(e)
            print("Failure...")
            print("Checksum dict: {}".format(asset['checksums']))
            print("Asset ID: {}".format(asset['id']))
            print("Asset Name: {}".format(asset['name']))
            print("Checksums not yet calculated, sleeping for 5 seconds.")

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

    print("'Completed' uploads: {}/{}".format(int(len(ul_items)), int(len(dl_items))))
    print("Percentage uploads completed but not verified: {:.2%}".format(len(ul_items)/len(dl_items)))

    print("Running verification...")

    print("DL Items Check: \n")
    pprint(dl_items)

    print("\nUL Items Check: \n")
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

    print("Verification complete for {}/{} uploaded assets.".format(int(len(ul_items)), int(len(dl_items))))
    print("Integration test passed!")

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
    # clean_up(client, upload_folder_id)

    print("Test complete, exiting...")

if __name__ == "__main__":
    run_test()
