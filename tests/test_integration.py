import os
import sys
import json
import mimetypes
import platform
import time
import pytest

from frameioclient import FrameioClient

# .env variables used for test assertions
project_id = os.getenv('PROJECT_ID')
root_asset_id = os.getenv('ROOT_ASSET_ID')
download_asset_id = os.getenv('DOWNLOAD_FOLDER_ID')
upload_folder_id = os.getenv('UPLOAD_FOLDER_ID')


# Test download functionality
def test_download(setup_client):
    client = setup_client

    print("Testing download function...")
    try:
        os.mkdir('downloads')
    except FileExistsError:
        print("Directory already exists, moving on...")
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

# Test uploading a single .txt file
def test_upload_single_file(setup_client, tmpdir):
    client = setup_client
    testdir = tmpdir.mkdir('single_file_upload')
    file = testdir.join('file.txt')
    file.write('file body')
    print(file)

    # python-frameio-client only supports uploads in asset form (see library for details)
    upload_asset = client.create_asset(
        parent_asset_id=upload_folder_id,
        name="file.txt",
        type="file",
        filetype="text/plain",
        filesize="10"
    )

    # Expect FileNotFound exception becaucse it's not a real file
    with pytest.raises(FileNotFoundError):
        with open('file.txt', 'rb') as upload_file:        
                client.upload(upload_asset, upload_file)

    assert file.read() == 'file body'
    assert upload_asset['name'] == 'file.txt'
    assert upload_asset['project_id'] == project_id
    assert upload_asset['parent_id'] == upload_folder_id

# Test upload functionality       
def test_upload(setup_client):
    client = setup_client
    print("Beginning upload test")
    # Create new parent asset
    
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
        flat_dict[asset['name']] = asset['filesize']

    return flat_dict


def check_upload_completion(setup_client, download_folder_id, upload_folder_id):
    client = setup_client
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

    dl_items = flatten_asset_children(dl_asset_children)
    ul_items = flatten_asset_children(ul_asset_children)

    print("Running comparison...")

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


def clean_up(setup_client, asset_to_delete):
    client = setup_client
    print("Removing files from test...")

    try:
        client._api_call('delete', '/assets/{}'.format(asset_to_delete))
        print("Managed to cleanup!")
    except Exception as e:
        print(e)

    return True