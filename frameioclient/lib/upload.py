import os
import time
import math
import requests
import threading
import concurrent.futures

from .utils import Utils

thread_local = threading.local()


class FrameioUploader(object):
    def __init__(self, asset=None, file=None):
        self.asset = asset
        self.file = file
        self.chunk_size = None
        self.file_count = 0
        self.file_num = 0
        self.futures = []
        self.completed_uploads = []
        self.completed_other_tasks = []
        self.map = dict()

    def _calculate_chunks(self, total_size, chunk_count):
        """Calculate chunk size

        Args:
            total_size (int): Total filesize in bytes
            chunk_count (int): Total number of URL's we got back from the API

        Returns:
            chunk_offsets (list): List of chunk offsets
        """
        self.chunk_size = int(math.ceil(total_size / chunk_count))

        chunk_offsets = list()

        for index in range(chunk_count):
            offset_amount = index * self.chunk_size
            chunk_offsets.append(offset_amount)

        return chunk_offsets

    def _get_session(self):
        if not hasattr(thread_local, "session"):
            thread_local.session = requests.Session()
        return thread_local.session

    def _smart_read_chunk(self, chunk_offset, is_final_chunk):
        with open(os.path.realpath(self.file.name), "rb") as file:
            file.seek(chunk_offset, 0)
            if (
                is_final_chunk
            ):  # If it's the final chunk, we want to just read until the end of the file
                data = file.read()
            else:  # If it's not the final chunk, we want to ONLY read the specified chunk
                data = file.read(self.chunk_size)
            return data

    def _upload_chunk(self, task):
        url = task[0]
        chunk_offset = task[1]
        chunk_id = task[2]
        chunks_total = len(self.asset["upload_urls"])

        is_final_chunk = False

        if chunk_id + 1 == chunks_total:
            is_final_chunk = True

        session = self._get_session()

        chunk_data = self._smart_read_chunk(chunk_offset, is_final_chunk)

        try:
            r = session.put(
                url,
                data=chunk_data,
                headers={
                    "content-type": self.asset["filetype"],
                    "x-amz-acl": "private",
                },
            )
            # print("Completed chunk, status: {}".format(r.status_code))
        except Exception as e:
            print(e)

        r.raise_for_status()

    def upload(self):
        total_size = self.asset["filesize"]
        upload_urls = self.asset["upload_urls"]

        chunk_offsets = self._calculate_chunks(total_size, chunk_count=len(upload_urls))

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for i in range(len(upload_urls)):
                url = upload_urls[i]
                chunk_offset = chunk_offsets[i]

                task = (url, chunk_offset, i)
                executor.submit(self._upload_chunk, task)
        
        return self.asset

    def file_counter(self, folder):
        matches = []
        for root, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                matches.append(os.path.join(filename))

        self.file_count = len(matches)

        return matches

    def recursive_upload(self, client, folder, parent_asset_id):
        # Seperate files and folders:
        file_list = list()
        folder_list = list()

        if self.file_count == 0:
            self.file_counter(folder)

        for item in os.listdir(folder):
            if item == ".DS_Store":  # Ignore .DS_Store files on Mac
                continue

            complete_item_path = os.path.join(folder, item)

            if os.path.isfile(complete_item_path):
                file_list.append(item)
            else:
                folder_list.append(item)

        # Create folders first
        for folder_name in folder_list:
            new_folder = os.path.join(folder, folder_name)
            new_parent_asset_id = client.assets.create(
                parent_asset_id=parent_asset_id, name=folder_name, type="folder"
            )["id"]

            self.recursive_upload(client, new_folder, new_parent_asset_id)

        if client.threads > 1:
            # Multi-threaded create + upload
            with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
                for index, file_p in enumerate(file_list):
                    self.file_num += 1 # Increment file number
                    complete_dir_obj = os.path.join(folder, file_p) # Get full path
                    task = (client, complete_dir_obj, parent_asset_id, self.file_num) # Create task tuple
                    self.futures.append(executor.submit(self._upload_processor, task)) # Submit to futures

                    # Every 50 assets, request the project
                    if index % 10 == 0:
                        task = (client, '2214a3b1-2ed0-46de-9350-81f49ee49bc4', index)
                        self.futures.append(executor.submit(self._project_tester, task))
                    
                    if index % 5 == 0:
                        task = (client, index)
                        self.futures.append(executor.submit(self._account_tester, task))

                    time.sleep(.05)

                # Wait on threads to finish
                for future in concurrent.futures.as_completed(self.futures):
                    response_info = dict()
                    index = None

                    try:
                        response_info, index = future.result()
                        # print(response_info, index)
                    except Exception as exc:
                        print(exc)

                    try:
                        if response_info.get('_type') != 'asset':
                            self.completed_other_tasks.append(index)
                            print("It's an account or a project GET")
                            # print("Completed {}/{}".format(len(self.completed_uploads), self.file_count))
                    except:
                        pass

                    try:
                        if response_info.get('_type') == 'asset' and index not in self.completed_uploads:
                            print("Completed {}/{}".format(len(self.completed_uploads), self.file_count))
                            self.completed_uploads.append(index)
                    except:
                        pass
        else:
            # Single threaded
            for file_p in file_list:
                self.file_num += 1

                complete_dir_obj = os.path.join(folder, file_p)
                print(
                    f"Starting {self.file_num:02d}/{self.file_count}, Size: {Utils.format_bytes(os.path.getsize(complete_dir_obj), type='size')}, Name: {file_p}"
                )

                client.assets.upload(parent_asset_id, complete_dir_obj)

    @staticmethod
    def _upload_processor(task):
        client = task[0]
        file_p = task[1]
        parent_asset_id = task[2]
        index = task[3]
        asset_info = client.assets.upload(parent_asset_id, file_p)

        if asset_info.get('id') != None:
            print(f"Uploaded asset for request: {index}")
        else:
            print("Failed somehow")
        
        return asset_info, index

    @staticmethod
    def _project_tester(task):        
        client = task[0]
        project_id = task[1]
        index = task[2]
        project_info = client.projects.get(project_id)
        
        if project_info.get('id') != None:
            print(f"Got project info for request: {index}")
        else:
            print("Failed somehow")
        return project_info, index

    @staticmethod
    def _account_tester(task):
        client = task[0]
        index = task[1]
        accounts_info = client.users.get_accounts()

        try:    
            if len(accounts_info) > 0:
                print(f"Got account info for request: {index}")
            else:
                print("Failed somehow")
        except Exception as e:
            pass

        return accounts_info, index
