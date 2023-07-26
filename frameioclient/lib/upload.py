import concurrent.futures
import math
import os
import threading
from typing import List

import requests

from .utils import FormatTypes, Utils

thread_local = threading.local()


class FrameioUploader(object):
    def __init__(self, asset=None, file=None):
        self.asset = asset
        self.file = file
        self.chunk_size = None
        self.file_count = 0
        self.file_num = 0
        self.futures = []

    def _calculate_chunks(self, total_size: int, chunk_count: int) -> List[int]:
        """
        Calculate chunk size

        :param total_size: Total filesize in bytes
        :param chunk_count: Total number of URL's we got back from the API

        :return chunk_offsets: List of chunk offsets
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

    def _smart_read_chunk(self, chunk_offset: int, is_final_chunk: bool) -> bytes:
        with open(os.path.realpath(self.file.name), "rb") as file:
            file.seek(chunk_offset, 0)
            if (
                is_final_chunk
            ):  # If it's the final chunk, we want to just read until the end of the file
                data = file.read()
            else:  # If it's not the final chunk, we want to ONLY read the specified chunk
                data = file.read(self.chunk_size)
            return data

    def _upload_chunk(self, task) -> int:
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

        return len(chunk_data)

    def upload(self):
        total_size = self.asset["filesize"]
        upload_urls = self.asset["upload_urls"]

        chunk_offsets = self._calculate_chunks(total_size, chunk_count=len(upload_urls))
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for i in range(len(upload_urls)):
                url = upload_urls[i]
                chunk_offset = chunk_offsets[i]

                task = (url, chunk_offset, i)
                self.futures.append(executor.submit(self._upload_chunk, task))

            # Keep updating the progress while we have > 0 bytes left.
            # Wait on threads to finish
            for future in concurrent.futures.as_completed(self.futures):
                try:
                    chunk_size = future.result()
                    print(chunk_size)
                except Exception as exc:
                    print(exc)

    def count_files(self, folder):
        matches = []
        for root, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                matches.append(os.path.join(filename))

        self.file_count = len(matches)

        return matches

    def upload_recursive(self, client, folder, parent_asset_id):
        # Seperate files and folders:
        file_list = list()
        folder_list = list()

        if self.file_count == 0:
            self.count_files(folder)

        for item in os.listdir(folder):
            if item == ".DS_Store":  # Ignore .DS_Store files on Mac
                continue

            complete_item_path = os.path.join(folder, item)

            if os.path.isfile(complete_item_path):
                file_list.append(item)
            else:
                folder_list.append(item)

        for file_p in file_list:
            self.file_num += 1

            complete_dir_obj = os.path.join(folder, file_p)
            print(
                "Starting {:02d}/{}, Size: {}, Name: {}".format(
                    self.file_num,
                    self.file_count,
                    Utils.format_value(
                        os.path.getsize(complete_dir_obj), type=FormatTypes.SIZE
                    ),
                    file_p,
                )
            )
            client.assets.upload(parent_asset_id, complete_dir_obj)

        for folder_name in folder_list:
            new_folder = os.path.join(folder, folder_name)
            new_parent_asset_id = client.assets.create(
                parent_asset_id=parent_asset_id, name=folder_name, type="folder"
            )["id"]

            self.upload_recursive(client, new_folder, new_parent_asset_id)
