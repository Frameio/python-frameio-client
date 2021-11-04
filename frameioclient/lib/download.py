import concurrent.futures
import math
import os
import time

import requests

from .logger import SDKLogger
from .transfer import AWSClient
from .utils import Utils

# from .telemetry import Event, ComparisonTest

logger = SDKLogger('downloads')

from .exceptions import (AssetChecksumMismatch, AssetChecksumNotPresent,
                         AssetNotFullyUploaded, DownloadException,
                         WatermarkIDDownloadException)


class FrameioDownloader(object):
    def __init__(self, asset, download_folder, prefix, multi_part=False, replace=False):
        self.multi_part = multi_part
        self.asset = asset
        self.asset_type = None
        self.download_folder = download_folder
        self.replace = replace
        self.resolution_map = dict()
        self.destination = None
        self.watermarked = asset["is_session_watermarked"]  # Default is probably false
        self.file_size = asset["filesize"]
        self.futures = list()
        self.checksum = None
        self.original_checksum = None
        self.checksum_verification = True
        self.chunk_size = 25 * 1024 * 1024  # 25 MB chunk size
        self.chunks = math.ceil(self.file_size / self.chunk_size)
        self.prefix = prefix
        self.bytes_started = 0
        self.bytes_completed = 0
        self.in_progress = 0
        self.aws_client = AWSClient(concurrency=5)
        self.session = self.aws_client._get_session()
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
                message="Unsupport Asset type: {}".format(self.asset.get("_type"))
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

    def download_handler(self):
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

        # Handle watermarking
        if self.watermarked == True:
            return self.aws_client()._download_whole(url)
        else:
            # Don't use multi-part download for files below 25 MB
            if self.file_size < 26214400:
                return self._download_whole(url)
            if self.multi_part == True:
                return self.multi_thread_download(url)
            else:
                return self._download_whole(url)

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
                print(e)
                raise e
        except TypeError as e:
            print(e)
            raise e
        return True

    def _optimize_concurrency(self):
        """
        This method looks as the net_stats and disk_stats that we've run on \
            the current environment in order to suggest the best optimized \
            number of concurrent TCP connections.

        Example::
            AWSClient._optimize_concurrency()
        """

        net_stats = NetworkBandwidth
        disk_stats = DiskBandwidth

        # Algorithm ensues
        #
        #

        return 5

    def _get_byte_range(self, url, start_byte=0, end_byte=2048):
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

    def _download_whole(self, url):
        start_time = time.time()
        print(
            "Beginning download -- {} -- {}".format(
                self.asset["name"], Utils.format_bytes(self.file_size, type="size")
            )
        )

        # Downloading
        r = self.session.get(url, stream=True)

        # Downloading
        with open(self.destination, "wb") as handle:
            try:
                # TODO make sure this approach works for SBWM download
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        handle.write(chunk)
            except requests.exceptions.ChunkedEncodingError as e:
                raise e

        download_time = time.time() - start_time
        download_speed = Utils.format_bytes(math.ceil(self.file_size / (download_time)))
        print(
            "Downloaded {} at {}".format(
                Utils.format_bytes(self.file_size, type="size"), download_speed
            )
        )

        return self.destination, download_speed

    def _download_chunk(self, task):
        # Download a particular chunk
        # Called by the threadpool executor

        # Destructure the task object into its parts
        url = task[0]
        start_byte = task[1]
        end_byte = task[2]
        chunk_number = task[3]

        # Set the initial chunk_size, but prepare to overwrite
        chunk_size = end_byte - start_byte

        if self.bytes_started + (chunk_size) > self.file_size:
            difference = abs(
                self.file_size - (self.bytes_started + chunk_size)
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
        r = self.session.get(url, headers=headers, stream=True)

        # Write the file to disk
        output_fn = self.destination + f"_{chunk_number}"
        print(output_fn)

        with open(output_fn, "wb", buffering=4096) as fp:            
            fp.write(r.content)  # Write the data

        # Save requests logs
        self.request_logs.append(
            {
                "headers": r.headers,
                "http_status": r.status_code,
                "bytes_transferred": len(r.content),
            }
        )

        # Increase the count for bytes_completed, but only if it doesn't overrun file length
        self.bytes_completed += chunk_size
        if self.bytes_completed > self.file_size:
            self.bytes_completed = self.file_size

        # After the function completes, we report back the # of bytes transferred
        return chunk_size

    def multi_thread_download(self, url):
        start_time = time.time()

        # # Generate stub
        # try:
        #     self._create_file_stub()

        # except Exception as e:
        #     raise DownloadException(message=e)

        offset = math.ceil(self.file_size / self.chunks)
        in_byte = 0  # Set initially here, but then override

        print(
            "Multi-part download -- {} -- {}".format(
                self.asset["name"], Utils.format_bytes(self.file_size, type="size")
            )
        )

        # Queue up threads
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.aws_client.concurrency
        ) as executor:
            for i in range(int(self.chunks)):
                # Increment by the iterable + 1 so we don't mutiply by zero
                out_byte = offset * (i + 1)
                # Create task tuple
                task = (url, in_byte, out_byte, i)

                # Append tasks to futures list
                self.futures.append(executor.submit(self._download_chunk, task))
                # Reset new in byte equal to last out byte
                in_byte = out_byte

                # Stagger start for each chunk by 0.1 seconds
                if i < self.aws_client.concurrency:
                    time.sleep(0.5)

            # executor.shutdown(wait=True)
            for future in concurrent.futures.as_completed(self.futures):
                try:
                    chunk_size = future.result()
                except Exception as exc:
                    print(exc)

            # Calculate and print stats
            download_time = round((time.time() - start_time), 2)
            download_speed = round((self.file_size / download_time), 2)

        if self.checksum_verification == True:
            # Check for checksum, if not present throw error
            if self._get_checksum() == None:
                raise AssetChecksumNotPresent

            # Calculate the file hash
            if (
                Utils.calculate_hash(
                    self.destination
                )
                != self.original_checksum
            ):
                raise AssetChecksumMismatch


            # Log completion event
            SDKLogger("downloads").info(
                "Downloaded {} at {}".format(
                    Utils.format_bytes(self.file_size, type="size"), download_speed
                )
            )

            # Submit telemetry
            transfer_stats = {
                "speed": download_speed,
                "time": download_time,
                "cdn": AWSClient.check_cdn(url),
            }

            # Event(self.user_id, 'python-sdk-download-stats', transfer_stats)

            # If stats = True, we return a dict with way more info, otherwise \
            if self.stats:
                # We end by returning a dict with info about the download
                dl_info = {
                    "destination": self.destination,
                    "speed": download_speed,
                    "elapsed": download_time,
                    "cdn": AWSClient.check_cdn(url),
                    "concurrency": self.aws_client.concurrency,
                    "size": self.file_size,
                    "chunks": self.chunks,
                }
                return dl_info
            else:
                return self.destination
