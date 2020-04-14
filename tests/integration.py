import os
import sys
import mimetypes

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

# Download files using the download function and then re-upload them to a folder next to this one
def test_download(client): 
    print("Testing download function")

    os.mkdir('downloads')
    os.chdir('downloads')
    
        
def test_upload(client):
    # Create new parent asset
    project_info = client.get_asset(project_id)
    root_asset_id = project_info['root_asset_id']
    
    new_folder = client.create_asset(
            parent_asset_id=root_asset_id,  
            name="Upload Test",
            type="folder",
        )
    
    new_parent_id = new_folder['id']

    # Upload all the files we downloaded earlier
    dled_files = os.listdir('.')

    for fn in dled_files:
        filesize = os.path.getsize(fn)
        filename = os.path.basename(fn)
        filemime = mimetypes.guess_type(fn)[0]

        asset = client.create_asset(
            parent_asset_id=new_parent_id,  
            name=filename,
            type="file",
            filetype=filemime,
            filesize=filesize
        )

        with open(fn, "rb") as ul_file:
            client.upload(asset, ul_file)
    
    return new_parent_id


def check_upload_completion(client, download_folder_id, upload_folder_id):
    # Do a comparison against filenames and filesizes here to make sure they match

    dl_asset_children = client.get_asset_children(download_folder_id)
    ul_asset_children = client.get_asset_children(upload_folder_id)

    dl_items = {
                    "filename_1": "my file",
                    "filesize_1": 15609,
                    "filename_2": "other file",
                    "filesize_2": 1235
                }

    ul_items = {
                    "filename_1": "my file",
                    "filesize_1": 15609,
                    "filename_2": "other file",
                    "filesize_2": 1235
                }

    comparison = cmp(dl_items, ul_items)
    
    if comparison != 0:
        print("File mismatch between upload and download")
        sys.exit(1)

    return True


def clean_up(client, asset_to_delete):
    # Remove downloaded files
    os.chdir('..')
    print(os.listdir('.'))

    print('About to delete everything in the folder named download in a second')
    # os.rmdir('download')

    # Remove uploaded folder


if __name__ == "__main__":
    print("Beginning Integration test...")

    client = init_client()
    test_download(client)
    upload_folder_id = test_upload(client)

    check_upload_completion(client, download_asset_id, upload_folder_id)

