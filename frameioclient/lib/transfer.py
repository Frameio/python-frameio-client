import concurrent.futures
import math
import os
import time
from pprint import pprint
from random import randint
from typing import Dict, List, Optional

import requests

from .exceptions import (
    AssetChecksumMismatch,
    AssetChecksumNotPresent,
    AssetNotFullyUploaded,
    DownloadException,
    WatermarkIDDownloadException,
)
from .logger import SDKLogger
from .transport import HTTPClient
from .utils import FormatTypes, Utils

logger = SDKLogger("frameioclient.transfer")


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
            # fp.write(b"\0" * self.filesize) # Disabled to prevent pre-allocatation of disk space
            fp.close()
        except FileExistsError as e:
            if self.replace == True:
                os.remove(self.destination)  # Remove the file
                self._create_file_stub()  # Create a new stub
            else:
                raise e
        return True

    def _get_path(self):
        logger.info("prefix: {}".format(self.prefix))
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


class AWSClient(HTTPClient, object):
    def __init__(self, downloader: FrameioDownloader, concurrency=None, progress=True):
        super().__init__(self)  # Initialize via inheritance
        self.progress = progress
        self.progress_manager = None
        self.destination = downloader.destination
        self.bytes_started = 0
        self.bytes_completed = 0
        self.downloader = downloader
        self.futures = []
        self.original = self.downloader.asset["original"]

        # Ensure this is a valid number before assigning
        if concurrency is not None and type(concurrency) == int and concurrency > 0:
            self.concurrency = concurrency

    @staticmethod
    def check_cdn(url):
        # TODO improve this algo
        if "assets.frame.io" in url:
            return "Cloudfront"
        elif "s3" in url:
            return "S3"
        else:
            return None

    def _create_file_stub(self):
        try:
            fp = open(self.downloader.destination, "w")
            # fp.write(b"\0" * self.filesize) # Disabled to prevent pre-allocatation of disk space
            fp.close()
        except FileExistsError as e:
            if self.replace == True:
                os.remove(self.downloader.destination)  # Remove the file
                self._create_file_stub()  # Create a new stub
            else:
                print(e)
                raise e
        except TypeError as e:
            print(e)
            raise e
        return True

    def _get_byte_range(
        self, url: str, start_byte: Optional[int] = 0, end_byte: Optional[int] = 2048
    ):
        """
        Get a specific byte range from a given URL. This is **not** optimized \
            for heavily-threaded operations currently.

        :Args:
            url (string): The URL you want to fetch a byte-range from
            start_byte (int): The first byte you want to request
            end_byte (int): The last byte you want to extract

        Example::
            AWSClient().get_byte_range(asset, "~./Downloads")
        """

        range_header = {"Range": "bytes=%d-%d" % (start_byte, end_byte)}

        headers = {**self.shared_headers, **range_header}

        br = requests.get(url, headers=headers).content
        return br

    def _download_whole(self, url: str):
        start_time = time.time()
        print(
            "Beginning download -- {} -- {}".format(
                self.asset["name"],
                Utils.format_value(self.downloader.filesize, type=FormatTypes.SIZE),
            )
        )

        # Downloading
        self.session = self._get_session()
        r = self.session.get(url, stream=True)

        # Downloading
        with open(self.downloader.destination, "wb") as handle:
            try:
                # TODO make sure this approach works for SBWM download
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        handle.write(chunk)
            except requests.exceptions.ChunkedEncodingError as e:
                raise e

        download_time = time.time() - start_time
        download_speed = Utils.format_value(
            math.ceil(self.downloader.filesize / (download_time))
        )
        print(
            f"Downloaded {Utils.format_value(self.downloader.filesize, type=FormatTypes.SIZE)} at {Utils.format_value(download_speed, type=FormatTypes.SPEED)}"
        )

        return self.destination, download_speed

    def _download_chunk(self, task: List):
        # Download a particular chunk
        # Called by the threadpool executor

        # Destructure the task object into its parts
        url = task[0]
        start_byte = task[1]
        end_byte = task[2]
        chunk_number = task[3]
        # in_progress = task[4]

        # Set the initial chunk_size, but prepare to overwrite
        chunk_size = end_byte - start_byte

        if self.bytes_started + (chunk_size) > self.downloader.filesize:
            difference = abs(
                self.downloader.filesize - (self.bytes_started + chunk_size)
            )  # should be negative
            chunk_size = chunk_size - difference
            print(f"Chunk size as done via math: {chunk_size}")
        else:
            pass

        # Set chunk size in a smarter way
        self.bytes_started += chunk_size

        # Specify the start and end of the range request
        headers = {"Range": "bytes=%d-%d" % (start_byte, end_byte)}

        # Grab the data as a stream
        self.session = self._get_session()
        r = self.session.get(url, headers=headers, stream=True)

        # Write the file to disk
        with open(self.destination, "r+b") as fp:
            fp.seek(start_byte)  # Seek to the right spot in the file
            chunk_size = len(r.content)  # Get the final chunk size
            fp.write(r.content)  # Write the data

        # Save requests logs
        self.downloader.request_logs.append(
            {
                "headers": r.headers,
                "http_status": r.status_code,
                "bytes_transferred": len(r.content),
            }
        )

        # Increase the count for bytes_completed, but only if it doesn't overrun file length
        self.bytes_completed += chunk_size
        if self.bytes_completed > self.downloader.filesize:
            self.bytes_completed = self.downloader.filesize

        # After the function completes, we report back the # of bytes transferred
        return chunk_size

    def multi_thread_download(self):
        start_time = time.time()

        # Generate stub
        try:
            self._create_file_stub()
        except Exception as e:
            raise DownloadException(message=e)

        pprint(self.downloader)

        offset = math.ceil(self.downloader.filesize / self.downloader.chunks)
        in_byte = 0  # Set initially here, but then override

        print(
            f"Multi-part download -- {self.downloader.asset['name']} -- {Utils.format_value(self.downloader.filesize, type=FormatTypes.SIZE)}"
        )

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.concurrency
        ) as executor:
            for i in range(int(self.downloader.chunks)):
                # Increment by the iterable + 1 so we don't mutiply by zero
                out_byte = offset * (i + 1)

                # Create task tuple
                task = (self.downloader.asset["original"], in_byte, out_byte, i)

                # Stagger start for each chunk by 0.1 seconds
                if i < self.concurrency:
                    time.sleep(randint(1, 5) / 10)

                # Append tasks to futures list
                self.futures.append(executor.submit(self._download_chunk, task))

                # Reset new in byte equal to last out byte
                in_byte = out_byte

            # Wait on threads to finish
            for future in concurrent.futures.as_completed(self.futures):
                try:
                    chunk_size = future.result()
                    print(chunk_size)
                except Exception as exc:
                    print(exc)

        # Calculate and print stats
        download_time = round((time.time() - start_time), 2)
        pprint(self.downloader)
        download_speed = round((self.downloader.filesize / download_time), 2)

        if self.downloader.checksum_verification == True:
            # Check for checksum, if not present throw error
            if self.downloader._get_checksum() == None:
                raise AssetChecksumNotPresent

            # Calculate the file hash
            if (
                Utils.calculate_hash(self.destination)
                != self.downloader.original_checksum
            ):
                raise AssetChecksumMismatch

        # Log completion event
        SDKLogger("downloads").info(
            f"Downloaded {Utils.format_value(self.downloader.filesize, type=FormatTypes.SIZE)} at {Utils.format_value(download_speed, type=FormatTypes.SPEED)}"
        )

        # Submit telemetry
        transfer_stats = {
            "speed": download_speed,
            "time": download_time,
            "cdn": AWSClient.check_cdn(self.original),
        }

        # Event(self.user_id, 'python-sdk-download-stats', transfer_stats)

        # If stats = True, we return a dict with way more info, otherwise \
        if self.downloader.stats:
            # We end by returning a dict with info about the download
            dl_info = {
                "destination": self.destination,
                "speed": download_speed,
                "elapsed": download_time,
                "cdn": AWSClient.check_cdn(self.original),
                "concurrency": self.concurrency,
                "size": self.downloader.filesize,
                "chunks": self.downloader.chunks,
            }
            return dl_info
        else:
            return self.destination
