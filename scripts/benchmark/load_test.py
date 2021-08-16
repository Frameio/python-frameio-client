import os
import time
from frameioclient import FrameioClient

# base_directory = os.path.abspath(os.path.curdir)
# Define base directory 
base_directory = "/Users/jeff/Temp/Messy"

upload_dir = os.path.join(base_directory, "upload_me")

# Define the constants for the file creation stage
clip_name_head = "A001"
clip_name_tail = "161207_R6ZJ"
file_size_kb = 100

# List of directories to turn into the nested folder structure
directory_names = [
    "this",
    "is",
    "a",
    "very",
    "nested",
    "folder",
    "structure",
    "why",
    "is",
    "it",
    "so",
    "deep",
]


# Create the base for the upload directory if it doesn't already exist
if not os.path.exists(upload_dir):
    os.mkdir(upload_dir)


def write_frame(full_filename_path):
    filesize_bytes = file_size_kb * 1024
    if not os.path.isfile(full_filename_path):
        try:
            f = open(full_filename_path, "wb")
            f.seek(filesize_bytes - 1)
            f.write(b"\0")
            f.close()
        except Exception as e:
            print(e)
        finally:
            return True
    else:
        # Already exists
        return True

def create_folder_depth(depth):
    # Build folder path
    destination_dir = os.path.join(upload_dir, "/".join(directory_names[:depth]))
    try:
        # Create directory structure
        os.makedirs(destination_dir)
    except FileExistsError as e:
        print(e)

    return destination_dir


def create_files_and_folders(
    depth=10, clips=10, clip_length_min=1, fps=24, file_extension="ari"
):
    # Calculate number of frames to generate
    total_frame_count = fps * clip_length_min * 60
    # total_frame_count = 10

    starting_dir = create_folder_depth(depth)

    if starting_dir != None:
        for clip_number in range(1, clips + 1):  # Iterate for number of clips
            # Build clip name
            partial_clip_name = "{}C{:03d}".format(clip_name_head, clip_number)
            # print(f"Clip name: {partial_clip_name}")

            # Create directory for each clip
            try:
                os.mkdir(os.path.join(starting_dir, partial_clip_name))
            except FileExistsError as e:
                # Folder exists already
                pass

            # Create 100 kb file for each frame
            for frame in range(1, total_frame_count + 1):
                frame_name = (
                    f"{partial_clip_name}_{clip_name_tail}.{frame:07d}.{file_extension}"
                )
                # print(frame_name)
                frame_path = os.path.join(starting_dir, partial_clip_name, frame_name)
                write_frame(frame_path)

    return base_directory


def load_test(
    remote_project_id,
    source_folder="",
    remote_destination="",
    environment="staging",
):
    if environment == "staging":
        token = os.getenv("FRAMEIO_TOKEN_STAGING")
        api_url = "https://api.staging.frame.io"
    elif environment == "dev":
        token = os.getenv("FRAMEIO_TOKEN_DEV")
        api_url = "https://api.dev.frame.io"
    else:
        token = os.getenv("FRAMEIO_TOKEN")
        api_url = "https://api.frame.io"

    client = FrameioClient(token, host=api_url, threads=20)
    client.assets.upload_folder(
        source_path=source_folder, 
        destination_id=remote_destination,
        project_id=remote_project_id
    )

    return True


if __name__ == "__main__":
    # Set the remote project ID to use
    remote_project_id = "ed5d1f58-2ab3-4f20-9bca-c9026f5a8bd6"
    # Set the remote root directory to upload into
    remote_root_asset_id = 'cf1d7ee6-14ae-422b-99d8-1f608696e023'

    # Uncomment to prevent creation of files/folders
    # upload_dir = create_files_and_folders(depth=10, clips=1) # Will create a folder depth of 10 and then make 1,440 frames
    start_time = time.time()

    upload_dir = base_directory

    # Runs the load test using the upload directory we get back from the file and folder seed stage
    load_test(remote_project_id, upload_dir, remote_root_asset_id)
    
    end_time = time.time()
    print(f"Took {round((end_time - start_time), 2)} seconds.")
