import os
import sys
import json
import time
import shutil
import socket
import requests
import platform

from math import ceil
from pprint import pprint, pformat
from datetime import datetime
from frameioclient import FrameioClient, Utils, KB, MB
from frameioclient.lib.utils import FormatTypes

from dotenv import find_dotenv
find_dotenv()

token = os.getenv("FRAMEIO_TOKEN") # Your Frame.io token
project_id = os.getenv("PROJECT_ID") # Project you want to upload files back into
download_asset_id = os.getenv("DOWNLOAD_FOLDER_ID") # Source folder on Frame.io (to then verify against)
environment = os.getenv("ENVIRONMENT", default="PRODUCTION")
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
ci_job_name = os.getenv("CIRCLE_JOB", default=None)

download_dir = 'downloads'

retries = 0

# Initialize the client
def init_client() -> FrameioClient:
    if len(token) < 5:
        print("Bad token, exiting test.")
        sys.exit(1)
    
    if environment == "PRODUCTION":
        client = FrameioClient(token, threads=10)
        print("Client connection initialized.")

    else:
        client = FrameioClient(token, host='https://api.dev.frame.io', threads=10)
        print("Client connection initialized.")

    return client

# Verify local and source
def verify_local(client: FrameioClient, dl_children):
    # Compare remote filenames and hashes
    global dl_items
    dl_items = dict()

    # Iterate over local directory and get filenames and hashes
    dled_files = os.listdir(download_dir)
    for count, fn in enumerate(dled_files, start=1):
        print("{}/{} Generating hash for: {}".format(count, len(dled_files), fn))
        dl_file_path = os.path.join(os.path.abspath(os.path.curdir), download_dir, fn)
        print("Path to downloaded file for hashing: {}".format(dl_file_path))
        xxhash = Utils.calculate_hash(dl_file_path)
        xxhash_name = "{}_{}".format(fn, 'xxHash')
        dl_items[xxhash_name] = xxhash

    print("QCing Downloaded Files...")

    print("Original Items Check: \n")
    og_items = flatten_asset_children(dl_children)
    pprint(og_items)

    print("Downloaded Items Check: \n")
    pprint(dl_items)

    pass_fail = Utils.compare_items(og_items, dl_items)

    # If verification fails here, try downloading again.
    if pass_fail == False:
        print("Mismatch between original and downloaded files, re-downloading...")
        test_download(client, override=True)
    else:
        return True

# Test download functionality
def test_download(client: FrameioClient, override=False):
    print("Testing download function...")
    if override:
        # Clearing download directory
        shutil.rmtree(download_dir)

    if os.path.isdir(download_dir):
        print("Local downloads folder detected...")
        asset_list = client.assets.get_children(
            download_asset_id,
            page=1,
            page_size=40,
            include="children"
        )

        verify_local(client, asset_list)
        return True
    
    os.mkdir(download_dir)

    asset_list = client.assets.get_children(
        download_asset_id,
        page=1,
        page_size=40,
        include="children"
    )

    print("Downloading {} files.".format(len(asset_list)))
    for count, asset in enumerate(asset_list, start=1):
        start_time = time.time()
        print("{}/{} Beginning to download: {}".format(count, len(asset_list), asset['name']))
        
        client.assets.download(asset, download_dir, multi_part=True)
        
        download_time = time.time() - start_time
        download_speed = Utils.format_value(ceil(asset['filesize']/(download_time)), type=FormatTypes.SPEED)

        print("{}/{} Download completed in {:.2f}s @ {}".format((count), len(asset_list), download_time, download_speed))

    print("Done downloading files")

    # Verify downloads
    if verify_local(client, asset_list):
        print("Download verification passed")

    return True

# Test upload functionality
def test_upload(client: FrameioClient):
    print("Beginning upload test")
    # Create new parent asset
    project_info = client.projects.get(project_id)
    root_asset_id = project_info['root_asset_id']
    
    print(f"Creating new folder to upload to in project {project_id}")
    test_run_name = "{}_{}_Py{}_{}".format(socket.gethostname(), platform.system(), platform.python_version(), datetime.now().strftime('%B-%d-%Y'))
    print(f"Folder name: {test_run_name}")
    new_folder = client.assets.create_folder(
            parent_asset_id=root_asset_id, 
            name=test_run_name,
        )
    
    new_parent_id = new_folder['id']

    print("Folder created, id: {}, name: {}".format(new_parent_id, new_folder['name']))

    # Upload all the files we downloaded earlier
    dled_files = os.listdir(download_dir)

    for count, fn in enumerate(dled_files, start=1):
        start_time = time.time()
        ul_abs_path = os.path.join(os.curdir, download_dir, fn)
        filesize = os.path.getsize(ul_abs_path)
        filename = os.path.basename(ul_abs_path)

        print("{}/{} Beginning to upload: {}".format(count, len(dled_files), fn))

        client.assets.upload(new_parent_id, ul_abs_path)

        upload_time = time.time() - start_time
        upload_speed = Utils.format_value(ceil(filesize/(upload_time)), type=FormatTypes.SPEED)

        print("{}/{} Upload completed in {:.2f}s @ {}".format((count), len(dled_files), upload_time, upload_speed))

    print("Sleeping for 10 seconds to allow upload and media analysis to finish...")
    time.sleep(10)

    print("Continuing...")

    return new_parent_id

# Flatten asset children and pull out important info for comparison
def flatten_asset_children(asset_children):
    flat_dict = dict()

    for asset in asset_children:
        try:
            xxhash_name = "{}_{}".format(asset['name'], 'xxHash')
            xxhash_checksum = asset['checksums']['xx_hash']

            if sys.version_info.major < 3: # if Python 2 convert the field
                xxhash_checksum = str(xxhash_checksum.encode('utf-8'))

            flat_dict[xxhash_name] = xxhash_checksum

        except TypeError as e:
            print(e)
            xxhash_name = "{}_{}".format(asset['name'], 'xxHash')
            flat_dict[xxhash_name] = "missing"

            continue

    return flat_dict

def check_for_checksums(client, upload_folder_id):
    # Get asset children for upload folder
    asset_children = client.assets.get_children(
        upload_folder_id,
        page=1,
        page_size=40,
        include="children"
    )

    global retries
    print("Checking for checksums attempt #{}".format(retries+1))
    
    if retries < 20:
        for asset in asset_children:
            try:
                asset['checksums']['xx_hash']
                print("Success...")
                print("Asset ID: {}".format(asset['id']))
                print("Asset Name: {}".format(asset['name']))
                print("Checksum dict: {}".format(asset['checksums']))
            except TypeError as e:
                # print(e)
                print("Failure...")
                print("Checksum dict: {}".format(asset['checksums']))
                print("Asset ID: {}".format(asset['id']))
                print("Asset Name: {}".format(asset['name']))
                print("Checksums not yet calculated, sleeping for 15 seconds.")
                time.sleep(15)
                retries += 1
                check_for_checksums(client, upload_folder_id)
        return True
    else:
        return False

def check_upload_completion(client, download_folder_id, upload_folder_id):
    # Do a comparison against filenames and filesizes here to make sure they match

    print("Beginning upload comparison check")

    # Get asset children for download folder
    dl_asset_children = client.assets.get_children(
        download_folder_id,
        page=1,
        page_size=40,
        include="children"
    )

    print("Got asset children for original download folder")

    print("Making sure checksums are calculated before verifying")
    check_for_checksums(client, upload_folder_id)

    # Get asset children for upload folder
    ul_asset_children = client.assets.get_children(
        upload_folder_id,
        page=1,
        page_size=40,
        include="children"
    )

    print("Got asset children for uploaded folder")

    global dl_items # Get the global dl_items

    # if len(dl_items.items) < 1:

    og_items = flatten_asset_children(dl_asset_children)
    ul_items = flatten_asset_children(ul_asset_children)

    print("'Completed' uploads: {}/{}".format(int(len(ul_items)), int(len(og_items))))
    print("Percentage uploads completed but not verified: {:.2%}".format(len(ul_items)/len(og_items)))

    print("Running verification...")

    print("OG Items Check:")
    pprint(og_items)
    
    print("DL Items Check:")
    pprint(dl_items)

    print("UL Items Check:")
    pprint(ul_items)

    pass_fail = Utils.compare_items(og_items, ul_items)

    print("Verification complete for {}/{} uploaded assets.".format(int(len(ul_items)), int(len(og_items))))

    if ci_job_name is not None:
        print("CircleCI Job Name: {}".format(ci_job_name))
        if ci_job_name == "upload_test_job":
            send_to_slack(format_slack_message(pass_fail, og_items, dl_items, ul_items))

    if pass_fail == True:
        print("Integration test passed! :)")
    else:
        print("Integration test failed! :(")
        sys.exit(1)

    return True

def format_slack_message(pass_fail, og_items, dl_items, ul_items):
    # Format slack message for sending
    message = "Test Pass/Fail: *{}*\n\n*Original assets:* \n{}\n*Downloaded assets:* \n {}\n*Uploaded assets:* \n {}".format(pass_fail, pformat(og_items), pformat(dl_items), pformat(ul_items))
    print(message)

    return message

def send_to_slack(message: str):
    # Send Slack message to provided 
    if len(slack_webhook_url) < 2:
        print("No Slack webhook ENV var provided, not sending a Slack message...")
    
    data = {
        'text': message,
        'username': 'Upload Integration Test',
        'icon_emoji': ':robot_face:'
    }

    response = requests.post(slack_webhook_url, data=json.dumps(
        data), headers={'Content-Type': 'application/json'})
    
    print('Response: ' + str(response.text))
    print('Response code: ' + str(response.status_code))

    if response.status_code == 200:
        return True
    else:
        return False

def clean_up(client: FrameioClient, asset_to_delete: str):
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
