import math
import os
from typing import Dict

from .logger import SDKLogger
from .transfer import AWSClient
from .utils import Utils

logger = SDKLogger("downloads")

from .exceptions import (AssetNotFullyUploaded, DownloadException,
                         WatermarkIDDownloadException)


class FrameioDownloader(object):
    def __init__(
        self,
        asset: Dict,
        download_folder: str,
        prefix: str,
        multi_part: bool = False,
        replace: bool = False,
    ):
        self.multi_part = multi_part
        self.asset = asset
        self.asset_type = None
        self.download_folder = download_folder
        self.replace = replace
        self.resolution_map = dict()
        self.destination = None
        self.watermarked = asset["is_session_watermarked"]  # Default is probably false
        self.filesize = asset["filesize"]
        self.futures = list()
        self.checksum = None
        self.original_checksum = None
        self.checksum_verification = True
        self.chunk_size = 25 * 1024 * 1024  # 25 MB chunk size
        self.chunks = math.ceil(self.filesize / self.chunk_size)
        self.prefix = prefix
        self.bytes_started = 0
        self.bytes_completed = 0
        self.in_progress = 0
        self.aws_client = None
        self.session = None
        self.filename = Utils.normalize_filename(asset["name"])
        self.request_logs = list()
        self.stats = True

        self._evaluate_asset()
        self._get_path()

    def _update_in_progress(self):
        self.in_progress = self.bytes_started - self.bytes_completed
        return self.in_progress  # Number of in-progress bytes

    def get_path(self):
        if self.prefix != None:
            self.filename = self.prefix + self.filename

        if self.destination == None:
            final_destination = os.path.join(self.download_folder, self.filename)
            self.destination = final_destination

        return self.destination

    def _evaluate_asset(self):
        if self.asset.get("_type") != "file":
            raise DownloadException(
                message=f"Unsupport Asset type: {self.asset.get('_type')}"
            )

        # This logic may block uploads that were started before this field was introduced
        if self.asset.get("upload_completed_at") == None:
            raise AssetNotFullyUploaded

        try:
            self.original_checksum = self.asset["checksums"]["xx_hash"]
        except (TypeError, KeyError):
            self.original_checksum = None

    def _create_file_stub(self):
        try:
            fp = open(self.destination, "w")
            # fp.write(b"\0" * self.file_size) # Disabled to prevent pre-allocatation of disk space
            fp.close()
        except FileExistsError as e:
            if self.replace == True:
                os.remove(self.destination)  # Remove the file
                self._create_file_stub()  # Create a new stub
            else:
                raise e
        return True

    def _get_path(self):
        logger.info(f"prefix: {self.prefix}")
        if self.prefix != None:
            self.filename = self.prefix + self.filename

        if self.destination == None:
            final_destination = os.path.join(self.download_folder, self.filename)
            self.destination = final_destination

        return self.destination

    def _get_checksum(self):
        try:
            self.original_checksum = self.asset["checksums"]["xx_hash"]
        except (TypeError, KeyError):
            self.original_checksum = None

        return self.original_checksum

    def get_download_key(self):
        try:
            url = self.asset["original"]
        except KeyError as e:
            if self.watermarked == True:
                resolution_list = list()
                try:
                    for resolution_key, download_url in sorted(
                        self.asset["downloads"].items()
                    ):
                        resolution = resolution_key.split("_")[
                            1
                        ]  # Grab the item at index 1 (resolution)
                        try:
                            resolution = int(resolution)
                        except ValueError:
                            continue

                        if download_url is not None:
                            resolution_list.append(download_url)

                    # Grab the highest resolution (first item) now
                    url = resolution_list[0]
                except KeyError:
                    raise DownloadException
            else:
                raise WatermarkIDDownloadException

        return url

    def download(self):
        """Call this to perform the actual download of your asset!"""

        # Check folders
        if os.path.isdir(os.path.join(os.path.curdir, self.download_folder)):
            logger.info("Folder exists, don't need to create it")
        else:
            logger.info("Destination folder not found, creating")
            os.mkdir(self.download_folder)

        # Check files
        if os.path.isfile(self.get_path()) == False:
            pass

        if os.path.isfile(self.get_path()) and self.replace == True:
            os.remove(self.get_path())

        if os.path.isfile(self.get_path()) and self.replace == False:
            logger.info("File already exists at this location.")
            return self.destination

        # Get URL
        url = self.get_download_key()

        # AWS Client
        self.aws_client = AWSClient(downloader=self, concurrency=5)

        # Handle watermarking
        if self.watermarked == True:
            return self.aws_client._download_whole(url)

        else:
            # Don't use multi-part download for files below 25 MB
            if self.asset["filesize"] < 26214400:
                return self.aws_client._download_whole(url)
            if self.multi_part == True:
                return self.aws_client.multi_thread_download(url)
            else:
                return self.aws_client._download_whole(url)
